import pandas as pd # type: ignore
import gpaslocal.models as models
from gpaslocal.db import get_session, init_db, dispose_db
from gpaslocal.upload_models import RunImport, SpecimensImport, SamplesImport
from pydantic import ValidationError
from gpaslocal.logs import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError
from progressbar import ProgressBar
from datetime import date

def import_data(excel_wb: str, dryrun: bool = False) -> bool:
    try:
        init_db()
        
        logger.info(f"Verifying and uploading data to database from Excel Workbook {excel_wb}")
        with get_session() as session:
            try:
                runs(session, excel_wb=excel_wb, dryrun=dryrun)
                # flush the session to make sure we have the run ids
                session.flush()
                
                specimens(session, excel_wb=excel_wb, dryrun=dryrun)
                session.flush()
                
                samples(session, excel_wb=excel_wb, dryrun=dryrun)
                session.flush()
                
            except Exception as e:
                logger.error(f"Failed to upload data: {e}")
        
            if logger.error_occurred: # type: ignore
                session.rollback()
                logger.error("Upload failed, please see log messages for details")
                return False
            
            if dryrun:
                logger.info("Dry run mode, no data was uploaded")
                session.rollback()
            else:
                logger.info("Data uploaded successfully")
                session.commit()
        
        return True
    finally:
        dispose_db()

def runs(session: Session, excel_wb: str, dryrun: bool) -> None:
    
    df = pd.read_excel(excel_wb, sheet_name="Runs")
    pbar = ProgressBar(max_value=len(df))
    
    for index, row in pbar(df.iterrows()):
        try:
            run_import = RunImport(**row)
            run_record = models.Run(
                code=run_import.code,
                run_date=run_import.run_date,
                site=run_import.site,
                sequencing_method=run_import.sequencing_method,
                machine=run_import.machine,
                user=run_import.user,
                number_samples=run_import.number_samples,
                flowcell=run_import.flowcell,
                passed_qc=run_import.passed_qc,
                comment=run_import.comment
            )
            existing_run = session.query(models.Run).filter(models.Run.code == run_import.code).first()
            if existing_run:
                logger.info(f"Runs Sheet Row {index+2}: Run {row['code']} already exists{', updating' if not dryrun else ''}")
                run_record.id = existing_run.id
            else:
                logger.info(f"Runs Sheet Row {index+2}: Run {row['code']} does not exist{', adding' if not dryrun else ''}")
            session.merge(run_record)
        except ValidationError as err:
            for error in err.errors():
                logger.error(f"Runs Sheet Row {index+2} {error['loc']} : {error['msg']}")
        except DBAPIError as err:
            logger.error(f"Runs Sheet Row {index+2} : {err}")
    session.flush()

def specimens(session: Session, excel_wb: str, dryrun: bool) -> None:
    
    df = pd.read_excel(excel_wb, sheet_name="Specimens")
    pbar = ProgressBar(max_value=len(df))
    
    for index, row in pbar(df.iterrows()):
        try:
            specimen_import = SpecimensImport(**row)
            
            owner_id = owner(session, index, row, dryrun)
            specimen_record = models.Specimen(
                owner_id=owner_id,
                accession=specimen_import.accession,
                collection_date=specimen_import.collection_date,
                country_sample_taken=specimen_import.country_sample_taken_code,
                specimen_type=specimen_import.specimen_type,
                specimen_qr_code=specimen_import.specimen_qr_code,
                bar_code=specimen_import.bar_code
            )
            existing_specimen = session.query(models.Specimen).filter(
                models.Specimen.accession == specimen_import.accession, 
                models.Specimen.collection_date == specimen_import.collection_date
            ).first()
            if existing_specimen:
                logger.info(f"Specimens Sheet Row {index+2}: Specimen {row['accession']}, {row['collection_date'].date()} already exists{', updating' if not dryrun else ''}")
                specimen_record.id = existing_specimen.id
            else:
                logger.info(f"Specimens Sheet Row {index+2}: Specimen {row['accession']}, {row['collection_date'].date()} does not exist{', adding' if not dryrun else ''}")
            session.merge(specimen_record)
        except ValidationError as err:
            for error in err.errors():
                logger.error(f"Specimens Sheet Row {index+2} {error['loc']} : {error['msg']}")
        except DBAPIError as err:
            logger.error(f"Specimens Sheet Row {index+2} : {err}")
    session.flush()
    
def owner(session:Session, index: int, row: dict, dryrun: bool) -> int:
    try:
        owner_record = models.Owner(
            site=row['owner_site'],
            user=row['owner_user']
        )
        existing_owner = session.query(models.Owner).filter(
            models.Owner.site == row['owner_site'], 
            models.Owner.user == row['owner_user']
        ).first()
        if existing_owner:
            owner_record.id = existing_owner.id
        else:
            logger.info(f"Specimens Sheet Row {index+2}: Owner {row['owner_site']}, {row['owner_user']} does not exist{', adding' if not dryrun else ''}")
        session.merge(owner_record)
    except DBAPIError as err:
        logger.error(f"Specimens Sheet Row {index+2} : {err}")
    session.flush()
    return owner_record.id

def samples(session: Session, excel_wb: str, dryrun: bool) -> None:
    
    df = pd.read_excel(excel_wb, sheet_name="Samples")
    pbar = ProgressBar(max_value=len(df))
    
    for index, row in pbar(df.iterrows()):
        try:
            sample_import = SamplesImport(**row)
            
            run_id = find_run(session, row['run_code'])
            specimen_id = find_specimen(session, row['accession'], row['collection_date'].date())
            sample_record = models.Sample(
                specimen_id=specimen_id,
                run_id=run_id,
                guid=sample_import.guid,
                sample_category=sample_import.sample_category,
                nucleic_acid_type=list(sample_import.nucleic_acid_type),
                
            )
            existing_sample = session.query(models.Sample).filter(
                models.Sample.guid == sample_import.guid
            ).first()
            if existing_sample:
                logger.info(f"Samples Sheet Row {index+2}: Sample {row['guid']} already exists{', updating' if not dryrun else ''}")
                sample_record.id = existing_sample.id
            else:
                logger.info(f"Samples Sheet Row {index+2}: Sample {row['guid']} does not exist{', adding' if not dryrun else ''}")
            session.merge(sample_record)
        except ValidationError as err:
            for error in err.errors():
                logger.error(f"Samples Sheet Row {index+2} {error['loc']} : {error['msg']}")
        except ValueError as err:
            logger.error(f"Samples Sheet Row {index+2} : {err}")
                
                
def find_run(session: Session, run_code: str) -> int:
    run = session.query(models.Run).filter(models.Run.code == run_code).first()
    if not run:
        raise ValueError(f"Run {run_code} does not exist")
    return run.id

def find_specimen(session: Session, accession: str, collection_date: date ) -> int:
    specimen = session.query(models.Specimen).filter(
        models.Specimen.accession == accession, 
        models.Specimen.collection_date == collection_date
    ).first()
    if not specimen:
        raise ValueError(f"Specimen {accession}, {collection_date} does not exist")
    return specimen.id