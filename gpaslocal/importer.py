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
            
            # check if the run already exists
            run_record = session.query(models.Run).filter(models.Run.code == run_import.code).first()
            if run_record:
                # update the run record
                run_record.update_from_importmodel(run_import)
                logger.info(f"Runs Sheet Row {index+2}: Run {row['code']} already exists{', updating' if not dryrun else ''}")
            else:
                # add the run record
                run_record = models.Run()
                run_record.update_from_importmodel(run_import)
                session.add(run_record)
                logger.info(f"Runs Sheet Row {index+2}: Run {row['code']} does not exist{', adding' if not dryrun else ''}")
        except ValidationError as err:
            for error in err.errors():
                logger.error(f"Runs Sheet Row {index+2} {error['loc']} : {error['msg']}")
        except DBAPIError as err:
            logger.error(f"Runs Sheet Row {index+2} : {err}")

def specimens(session: Session, excel_wb: str, dryrun: bool) -> None:
    
    df = pd.read_excel(excel_wb, sheet_name="Specimens")
    pbar = ProgressBar(max_value=len(df))
    
    for index, row in pbar(df.iterrows()):
        try:
            specimen_import = SpecimensImport(**row)
            
            # get the specimen owner
            owner_record = owner(session, index, row, dryrun)
            
            # check if we already have a specimen with the same accession and collection date
            specimen_record = session.query(models.Specimen).filter(
                models.Specimen.accession == specimen_import.accession, 
                models.Specimen.collection_date == specimen_import.collection_date
            ).first()
            if specimen_record:
                specimen_record.update_from_importmodel(specimen_import)
                specimen_record.owner = owner_record
                # have to set country_sample_taken separately as the field names differ
                specimen_record.country_sample_taken=specimen_import.country_sample_taken_code
                logger.info(f"Specimens Sheet Row {index+2}: Specimen {row['accession']}, {row['collection_date'].date()} already exists{', updating' if not dryrun else ''}")
            else:
                specimen_record = models.Specimen()
                specimen_record.update_from_importmodel(specimen_import)
                specimen_record.owner = owner_record
                # have to set country_sample_taken separately as the field names differ
                specimen_record.country_sample_taken=specimen_import.country_sample_taken_code
                session.add(specimen_record)
                logger.info(f"Specimens Sheet Row {index+2}: Specimen {row['accession']}, {row['collection_date'].date()} does not exist{', adding' if not dryrun else ''}")
        except ValidationError as err:
            for error in err.errors():
                logger.error(f"Specimens Sheet Row {index+2} {error['loc']} : {error['msg']}")
        except DBAPIError as err:
            logger.error(f"Specimens Sheet Row {index+2} : {err}")
    
def owner(session:Session, index: int, row: dict, dryrun: bool) -> models.Owner:
    try:
        owner_record = session.query(models.Owner).filter(
            models.Owner.site == row['owner_site'], 
            models.Owner.user == row['owner_user']
        ).first()
        if not owner_record:
            owner_record = models.Owner(
                site=row['owner_site'],
                user=row['owner_user']
            )
            session.add(owner_record)
            logger.info(f"Specimens Sheet Row {index+2}: Owner {row['owner_site']}, {row['owner_user']} does not exist{', adding' if not dryrun else ''}")
    except DBAPIError as err:
        logger.error(f"Specimens Sheet Row {index+2} : {err}")
    return owner_record

def samples(session: Session, excel_wb: str, dryrun: bool) -> None:
    
    df = pd.read_excel(excel_wb, sheet_name="Samples")
    pbar = ProgressBar(max_value=len(df))
    
    for index, row in pbar(df.iterrows()):
        try:
            sample_import = SamplesImport(**row)
            
            # Check if the run and specimen exist
            run_record = find_run(session, row['run_code'])
            specimen_record = find_specimen(session, row['accession'], row['collection_date'].date())
            
            sample_record = session.query(models.Sample).filter(
                models.Sample.guid == sample_import.guid
            ).first()
            
            # We have to update the sample record by field here due to the requirement to change the nucleic_acid_type field to a list
            if sample_record:
                sample_record.run = run_record
                sample_record.specimen = specimen_record
                sample_record.guid = sample_import.guid
                sample_record.sample_category = sample_import.sample_category
                sample_record.nucleic_acid_type = list(sample_import.nucleic_acid_type)
                logger.info(f"Samples Sheet Row {index+2}: Sample {row['guid']} already exists{', updating' if not dryrun else ''}")
            else:
                sample_record = models.Sample()
                sample_record.run = run_record
                sample_record.specimen = specimen_record
                sample_record.guid = sample_import.guid
                sample_record.sample_category = sample_import.sample_category
                sample_record.nucleic_acid_type = list(sample_import.nucleic_acid_type)
                logger.info(f"Samples Sheet Row {index+2}: Sample {row['guid']} does not exist{', adding' if not dryrun else ''}")
                session.add(sample_record)
                
            
            # add the sample detail records
            sample_detail(session, sample_record, sample_import)
            
        except ValidationError as err:
            for error in err.errors():
                logger.error(f"Samples Sheet Row {index+2} {error['loc']} : {error['msg']}")
        except ValueError as err:
            logger.error(f"Samples Sheet Row {index+2} : {err}")
                
                
def find_run(session: Session, run_code: str) -> models.Run:
    run = session.query(models.Run).filter(models.Run.code == run_code).first()
    if not run:
        raise ValueError(f"Run {run_code} does not exist")
    return run

def find_specimen(session: Session, accession: str, collection_date: date ) -> models.Specimen:
    specimen = session.query(models.Specimen).filter(
        models.Specimen.accession == accession, 
        models.Specimen.collection_date == collection_date
    ).first()
    if not specimen:
        raise ValueError(f"Specimen {accession}, {collection_date} does not exist")
    return specimen

def sample_detail(session: Session, sample_record: models.Sample, sample_import: SamplesImport) -> None:
    
    # loop through the sample detail types and add the sample details
    sample_detail_types = session.query(models.SampleDetailType).all()
    for sample_detail_type in sample_detail_types:
        # get the value from the sample_import
        value = sample_import[sample_detail_type.code]
        # check if the sample detail exists
        sample_detail_record = session.query(models.SampleDetail).filter(
            models.SampleDetail.sample == sample_record,
            models.SampleDetail.sample_detail_type_code == sample_detail_type.code
        ).first()
        
        # if the value is None, and the sample detail exists, delete it
        if value is None:
            if sample_detail_record:
                session.delete(sample_detail_record)
            continue
        
        if sample_detail_record:
            sample_detail_record['value_'+sample_detail_type.value_type] = value
        else:
            sample_detail_record = models.SampleDetail()
            sample_detail_record.sample = sample_record
            sample_detail_record.sample_detail_type_code = sample_detail_type.code
            sample_detail_record['value_'+sample_detail_type.value_type] = value
            session.add(sample_detail_record)
        