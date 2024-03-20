import pandas as pd  # type: ignore
import gpaslocal.models as models
from gpaslocal.db import get_session, db_revision_ok
from gpaslocal.upload_models import (
    RunImport,
    SpecimensImport,
    SamplesImport,
    StoragesImport,
)
from pydantic import ValidationError
from gpaslocal.logs import logger
from sqlalchemy.orm import Session
from sqlalchemy import not_
from sqlalchemy.exc import DBAPIError
from progressbar import ProgressBar
from datetime import date
import re

def import_data(excel_wb: str, dryrun: bool = False) -> bool:
    logger.info(
        f"Verifying and uploading data to database from Excel Workbook {excel_wb}"
    )
    with get_session() as session:
        try:
            if not db_revision_ok(session):
                return False

            runs(session, excel_wb=excel_wb, dryrun=dryrun)
            session.flush()

            specimens(session, excel_wb=excel_wb, dryrun=dryrun)
            session.flush()

            samples(session, excel_wb=excel_wb, dryrun=dryrun)
            session.flush()

            storage(session, excel_wb=excel_wb, dryrun=dryrun)
            session.flush()

        except Exception as e:
            logger.error(f"Failed to upload data: {e}")

        if logger.error_occurred:  # type: ignore
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


def runs(session: Session, excel_wb: str, dryrun: bool) -> None:
    df = pd.read_excel(excel_wb, sheet_name="Runs")
    pbar = ProgressBar(max_value=len(df))

    for index, row in pbar(df.iterrows()):
        try:
            run_import = RunImport(**row)

            if run_record := (
                session.query(models.Run)
                .filter(models.Run.code == run_import.code)
                .first()
            ):
                # update the run record
                run_record.update_from_importmodel(run_import)
                logger.info(
                    f"Runs Sheet Row {index+2}: Run {run_import.code} already exists{'' if dryrun else ', updating'}"
                )
            else:
                # add the run record
                run_record = models.Run()
                run_record.update_from_importmodel(run_import)
                session.add(run_record)
                logger.info(
                    f"Runs Sheet Row {index+2}: Run {run_import.code} does not exist{'' if dryrun else ', adding'}"
                )
        except ValidationError as err:
            for error in err.errors():
                logger.error(
                    f"Runs Sheet Row {index+2} {error['loc']} : {error['msg']}"
                )
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

            if specimen_record := (
                session.query(models.Specimen)
                .filter(
                    models.Specimen.accession == specimen_import.accession,
                    models.Specimen.collection_date == specimen_import.collection_date,
                )
                .first()
            ):
                specimen_record.update_from_importmodel(specimen_import)
                specimen_record.owner = owner_record
                logger.info(
                    f"Specimens Sheet Row {index+2}: Specimen {specimen_import.accession}, {specimen_import.collection_date} already exists{'' if dryrun else ', updating'}"
                )
            else:
                specimen_record = models.Specimen()
                specimen_record.update_from_importmodel(specimen_import)
                specimen_record.owner = owner_record
                session.add(specimen_record)
                logger.info(
                    f"Specimens Sheet Row {index+2}: Specimen {specimen_import.accession}, {specimen_import.collection_date} does not exist{'' if dryrun else ', adding'}"
                )

            specimen_detail(session, specimen_record, specimen_import)

        except ValidationError as err:
            for error in err.errors():
                logger.error(
                    f"Specimens Sheet Row {index+2} {error['loc']} : {error['msg']}"
                )
        except DBAPIError as err:
            logger.error(f"Specimens Sheet Row {index+2} : {err}")


def owner(
    session: Session, index: int, specimen_import: SpecimensImport, dryrun: bool
) -> models.Owner:
    owner_record = (
        session.query(models.Owner)
        .filter(
            models.Owner.site == specimen_import.owner_site,
            models.Owner.user == specimen_import.owner_user,
        )
        .first()
    )
    if not owner_record:
        owner_record = models.Owner(
            site=specimen_import.owner_site, user=specimen_import.owner_user
        )
        session.add(owner_record)
        logger.info(
            f"Specimens Sheet Row {index+2}: Owner {specimen_import.owner_site}, {specimen_import.owner_user} does not exist{'' if dryrun else ', adding'}"
        )
    return owner_record


def specimen_detail(
    session: Session, specimen_record: models.Specimen, specimen_import: SpecimensImport
) -> None:
    # loop through the specimen detail types and add the specimen details
    specimen_detail_types = session.query(models.SpecimenDetailType).all()
    for specimen_detail_type in specimen_detail_types:
        # get the value from the sample_import
        value = specimen_import[specimen_detail_type.code]
        # check if the sample detail exists
        specimen_detail_record = (
            session.query(models.SpecimenDetail)
            .filter(
                models.SpecimenDetail.specimen == specimen_record,
                models.SpecimenDetail.specimen_detail_type_code
                == specimen_detail_type.code,
            )
            .first()
        )

        # if the value is None, and the sample detail exists, delete it
        if value is None:
            if specimen_detail_record:
                session.delete(specimen_detail_record)
            continue

        if specimen_detail_record:
            specimen_detail_record["value_" + specimen_detail_type.value_type] = value
        else:
            specimen_detail_record = models.SpecimenDetail()
            specimen_detail_record.specimen = specimen_record
            specimen_detail_record.specimen_detail_type_code = specimen_detail_type.code
            specimen_detail_record["value_" + specimen_detail_type.value_type] = value
            session.add(specimen_detail_record)


def samples(session: Session, excel_wb: str, dryrun: bool) -> None:
    df = pd.read_excel(excel_wb, sheet_name="Samples")
    pbar = ProgressBar(max_value=len(df))

    for index, row in pbar(df.iterrows()):
        try:
            sample_import = SamplesImport(**row)

            # Check if the run and specimen exist
            run_record = find_run(session, sample_import.run_code)
            specimen_record = find_specimen(
                session, sample_import.accession, sample_import.collection_date
            )

            sample_record = (
                session.query(models.Sample)
                .filter(models.Sample.guid == sample_import.guid)
                .first()
            )

            if sample_record:
                sample_record.update_from_importmodel(sample_import)
                sample_record.run = run_record
                sample_record.specimen = specimen_record
                logger.info(
                    f"Samples Sheet Row {index+2}: Sample {sample_import.guid} already exists{'' if dryrun else ', updating'}"
                )
            else:
                sample_record = models.Sample()
                sample_record.update_from_importmodel(sample_import)
                sample_record.run = run_record
                sample_record.specimen = specimen_record
                logger.info(
                    f"Samples Sheet Row {index+2}: Sample {sample_import.guid} does not exist{'' if dryrun else ', adding'}"
                )
                session.add(sample_record)

            # add the sample detail records
            sample_detail(session, sample_record, sample_import)

            # add the spike records
            spikes(session, sample_record, sample_import, index)

        except ValidationError as err:
            for error in err.errors():
                logger.error(
                    f"Samples Sheet Row {index+2} {error['loc']} : {error['msg']}"
                )
        except ValueError as err:
            logger.error(f"Samples Sheet Row {index+2} : {err}")


def find_run(session: Session, run_code: str) -> models.Run:
    if run := session.query(models.Run).filter(models.Run.code == run_code).first():
        return run
    else:
        raise ValueError(f"Run {run_code} does not exist")


def find_specimen(
    session: Session, accession: str, collection_date: date
) -> models.Specimen:
    if specimen := (
        session.query(models.Specimen)
        .filter(
            models.Specimen.accession == accession,
            models.Specimen.collection_date == collection_date,
        )
        .first()
    ):
        return specimen
    else:
        raise ValueError(f"Specimen {accession}, {collection_date} does not exist")


def sample_detail(
    session: Session, sample_record: models.Sample, sample_import: SamplesImport
) -> None:
    # loop through the sample detail types and add the sample details
    sample_detail_types = session.query(models.SampleDetailType).all()
    for sample_detail_type in sample_detail_types:
        # get the value from the sample_import
        value = sample_import[sample_detail_type.code]
        # check if the sample detail exists
        sample_detail_record = (
            session.query(models.SampleDetail)
            .filter(
                models.SampleDetail.sample == sample_record,
                models.SampleDetail.sample_detail_type_code == sample_detail_type.code,
            )
            .first()
        )

        # if the value is None, and the sample detail exists, delete it
        if value is None:
            if sample_detail_record:
                session.delete(sample_detail_record)
            continue

        if sample_detail_record:
            sample_detail_record["value_" + sample_detail_type.value_type] = value
        else:
            sample_detail_record = models.SampleDetail()
            sample_detail_record.sample = sample_record
            sample_detail_record.sample_detail_type_code = sample_detail_type.code
            sample_detail_record["value_" + sample_detail_type.value_type] = value
            session.add(sample_detail_record)


def spikes(
    session: Session,
    sample_record: models.Sample,
    sample_import: SamplesImport,
    index: int,
) -> None:
    spike_names: dict = {
        k: v for k, v in sample_import.dict().items() if k.startswith("spike_name_")
    }
    spike_quantities: dict = {
        k: v for k, v in sample_import.dict().items() if k.startswith("spike_quantity_")
    }
    spike_fields = spike_names | spike_quantities

    # Extract the suffixes, convert them to integers
    suffixes = []
    for k in spike_fields:
        match = re.search(r"\d+$", k)
        if match is not None:
            suffixes.append(int(match.group()))
    # make sure the suffixes are unique
    suffixes = list(set(suffixes))

    for i in suffixes:
        spike_name: str = sample_import[f"spike_name_{i}"]
        spike_quantity: str = sample_import[f"spike_quantity_{i}"]
        # check if either the name and quantity is missing then skip
        if pd.isnull(spike_name) and pd.isnull(spike_quantity):
            continue
        # raise an error if just the name is missing
        if pd.isnull(spike_name):
            logger.error(
                f"Samples Sheet Row {index+2} : spike_name_{i} is missing name"
            )
            continue

        if spike_record := (
            session.query(models.Spike)
            .filter(
                models.Spike.sample == sample_record,
                models.Spike.name == spike_name,
            )
            .first()
        ):
            spike_record.quantity = spike_quantity
        else:
            spike_record = models.Spike()
            spike_record.sample = sample_record
            spike_record.name = spike_name
            spike_record.quantity = spike_quantity
            session.add(spike_record)

    # remove any spikes that are not in the spike table for this sample
    clean_spike_names = [x for x in spike_names.values() if not pd.isnull(x)]
    session.query(models.Spike).filter(
        not_(models.Spike.name.in_(clean_spike_names)),
        models.Spike.sample == sample_record,
    ).delete()


def storage(session: Session, excel_wb: str, dryrun: bool) -> None:
    df = pd.read_excel(excel_wb, sheet_name="Storage")
    pbar = ProgressBar(max_value=len(df))

    for index, row in pbar(df.iterrows()):
        try:
            storage_import = StoragesImport(**row)

            specimen_record = find_specimen(
                session, storage_import.accession, storage_import.collection_date
            )

            if storage_record := (
                session.query(models.Storage)
                .filter(
                    models.Storage.storage_qr_code == storage_import.storage_qr_code
                )
                .first()
            ):
                storage_record.update_from_importmodel(storage_import)
                storage_record.specimen = specimen_record
                logger.info(
                    f"Storage Sheet Row {index+2}: Storage {storage_import.storage_qr_code} already exists{'' if dryrun else ', updating'}"
                )
            else:
                storage_record = models.Storage()
                storage_record.update_from_importmodel(storage_import)
                storage_record.specimen = specimen_record
                logger.info(
                    f"Storage Sheet Row {index+2}: Storage {storage_import.storage_qr_code} does not exist{'' if dryrun else ', adding'}"
                )
                session.add(storage_record)

        except ValidationError as err:
            for error in err.errors():
                logger.error(
                    f"Storage Sheet Row {index+2} {error['loc']} : {error['msg']}"
                )
        except ValueError as err:
            logger.error(f"Storage Sheet Row {index+2} : {err}")
