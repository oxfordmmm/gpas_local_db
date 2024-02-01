import pandas as pd
import gpaslocal.models as models
from gpaslocal.db import Session as gpaslocal_session
from gpaslocal.upload_models import RunImport, SpecimensImport, SamplesImport
from pydantic import ValidationError
from gpaslocal.utils import logger, error_occurred
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError


def import_data(excel_wb: str, dryrun: bool = False) -> bool:
    
    logger.info(f"Verifying and uploading data to database from Excel Workbook {excel_wb}")
    with gpaslocal_session.begin() as session:
        try:
            upload_run(session, excel_wb=excel_wb, dryrun=dryrun)
            # flush the session to make sure we have the run ids
            session.flush()
            
        except Exception as e:
            logger.error(f"Failed to upload data: {e}")
    
    if error_occurred():
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

def upload_run(session: Session, excel_wb: str, dryrun: bool) -> None:
    
    df = pd.read_excel(excel_wb, sheet_name="Runs")
    
    for index, row in df.iterrows():
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
                logger.info(f"Runs Sheet Row {index+2}: Run {row['code']} already exists{dryrun and ', updating'}")
                run_record.id = existing_run.id
            else:
                logger.info(f"Runs Sheet Row {index+2}: Run {row['code']} does not exist{dryrun and ', adding'}")
            session.merge(run_record)
        except ValidationError as err:
            for error in err.errors():
                logger.error(f"Runs Sheet Row {index+2} {error['loc']} : {error['msg']}")
        except DBAPIError as err:
            logger.error(f"Runs Sheet Row {index+2} : {err}")
    session.flush()

def upload_specimens(session: Session, excel_wb: str, dryrun: bool) -> None:
    
    df = pd.read_excel(excel_wb, sheet_name="Specimens")
    
    for index, row in df.iterrows():
        try:
            specimen_import = SpecimensImport(**row)
            
            owner_id = upload_owner(session, index, row, dryrun)
            specimen_record = models.Specimen(
                owner_id=owner_id,
                accession=specimen_import.accession,
                collection_date=specimen_import.collection_date,
                country_sample_taken_code=specimen_import.country_sample_taken_code,
                specimen_type=specimen_import.specimen_type,
                speciment_qr_code=specimen_import.speciment_qr_code,
                bar_code=specimen_import.bar_code
            )
            existing_specimen = session.query(models.Specimen).filter(
                models.Specimen.accession == specimen_import.accession, 
                models.Specimen.collection_date == specimen_import.collection_date
            ).first()
            if existing_specimen:
                logger.info(f"Specimens Sheet Row {index+2}: Specimen {row['accession']}, {row['collection_date']} already exists{dryrun and ', updating'}")
                specimen_record.id = existing_specimen.id
            else:
                logger.info(f"Specimens Sheet Row {index+2}: Specimen {row['accession']}, {row['collection_date']} does not exist{dryrun and ', adding'}")
            session.merge(specimen_record)
        except ValidationError as err:
            for error in err.errors():
                logger.error(f"Specimens Sheet Row {index+2} {error['loc']} : {error['msg']}")
        except DBAPIError as err:
            logger.error(f"Specimens Sheet Row {index+2} : {err}")
    session.flush()
    
def upload_owner(session:Session, index: int, row: dict, dryrun: bool) -> int:
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
            logger.info(f"Specimens Sheet Row {index+2}: Owner {row['owner_site']}, {row['owner_user']} does not exist{dryrun and ', adding'}")
        session.merge(owner_record)
    except DBAPIError as err:
        logger.error(f"Specimens Sheet Row {index+2} : {err}")
    session.flush()
    return owner_record.id