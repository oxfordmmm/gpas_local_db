from gpaslocal.logs import logger
from gpaslocal.db import get_session
from gpaslocal.db import db_revision_ok
import pandas as pd  # type: ignore
from progressbar import ProgressBar
from gpaslocal import models
from gpaslocal.upload_models import GpasSummary, Mutations
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from pydantic import ValidationError
from gpaslocal.constants import tb_drugs


def import_summary(summary_csv: str, mapping_csv: str, dryrun: bool):
    """Upload data from a summary csv"""
    logger.info(f"Verifying and uploading data to database from Summary {summary_csv}")
    with get_session() as session:
        try:
            if not db_revision_ok(session):
                return False

            df_sum = pd.read_csv(summary_csv)
            df_map = pd.read_csv(mapping_csv)

            df_merged = df_sum.merge(
                df_map, left_on="Sample ID", right_on="remote_sample_name", how="left"
            )
            pbar = ProgressBar(max_value=len(df_merged))

            for index, row in pbar(df_merged.iterrows()):
                try:
                    gpas_summary = GpasSummary(**row)

                    analysis_record = analysis(session, gpas_summary, index, dryrun)
                    session.flush()

                    speciation(session, gpas_summary, index, dryrun, analysis_record)
                    session.flush()

                    drugs(session, gpas_summary, index, dryrun, analysis_record)
                    session.flush()

                    details(session, gpas_summary, analysis_record)
                    session.flush()

                except ValidationError as err:
                    for error in err.errors():
                        logger.error(
                            f"Summary Row {index+2} {error['loc']} : {error['msg']}"
                        )
                except DBAPIError as err:
                    logger.error(f"Summary Row {index+2} : {err}")

                except ValueError as err:
                    logger.error(f"Summary Row {index+2} : {err}")

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


def find_sample(session: Session, guid: str) -> models.Sample:
    if sample := (
        session.query(models.Sample).filter(models.Sample.guid == guid).first()
    ):
        return sample
    else:
        raise ValueError(f"Sample {guid} does not exist")


def analysis(
    session: Session, row_model: GpasSummary | Mutations, index: int, dryrun: bool
) -> models.Analysis:
    sample = find_sample(session, row_model.sample_name)
    if analysis := (
        session.query(models.Analysis)
        .filter(
            models.Analysis.sample == sample,
            models.Analysis.batch_name == row_model.batch,
        )
        .first()
    ):
        analysis.assay_system == "GPAS TB"
    else:
        analysis = models.Analysis(
            sample=sample, batch_name=row_model.batch, assay_system="GPAS TB"
        )
        session.add(analysis)
        logger.info(
            f"Row {index+2}: Batch {row_model.batch}, Sample {row_model.sample_name} does not exist{'' if dryrun else ', adding'}"
        )

    return analysis


def speciation(
    session: Session,
    gpas_summary: GpasSummary,
    index: int,
    dryrun: bool,
    analysis_record: models.Analysis,
) -> models.Speciation | None:
    if gpas_summary.species is None:
        logger.info(
            f"Summary row {index+2}: Speciation for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name} not found"
        )
        return None

    speciation = (
        (
            session.query(models.Speciation)
            .filter(
                models.Speciation.analysis == analysis_record,
                models.Speciation.species_number == 1,
            )
            .first()
        )
        if analysis_record.id
        else None
    )

    if not speciation:
        speciation = models.Speciation(analysis=analysis_record, species_number=1)
        session.add(speciation)
        logger.info(
            f"Summary row {index+2}: Speciation for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name} does not exist{'' if dryrun else ', adding'}"
        )
    else:
        logger.info(
            f"Summary row {index+2}: Speciation for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name} already exists{'' if dryrun else ', updating'}"
        )

    speciation.species = gpas_summary.species
    speciation.sub_species = gpas_summary.sub_species
    speciation.analysis_date = gpas_summary.run_date

    return speciation


def drugs(
    session: Session,
    gpas_summary: GpasSummary,
    index: int,
    dryrun: bool,
    analysis_record: models.Analysis,
):
    if gpas_summary.resistance_prediction is None:
        logger.info(
            f"Summary row {index+2}: Drug Resistance for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name} Empty"
        )
        return

    for key, value in tb_drugs.items():
        if drug_resistance := (
            session.query(models.DrugResistance)
            .filter(
                models.DrugResistance.analysis == analysis_record,
                models.DrugResistance.antibiotic == value,
            )
            .first()
        ):
            logger.info(
                f"Summary row {index+2}: Drug Resistance for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name}, Antibiotic {value} already exists{'' if dryrun else ', updating'}"
            )
        else:
            drug_resistance = models.DrugResistance(
                analysis=analysis_record,
                antibiotic=value,
            )
            session.add(drug_resistance)
        drug_resistance.drug_resistance_result_type_code = (
            gpas_summary.resistance_prediction[key]
        )

    logger.info(
        f"Summary row {index+2}: Drug Resistance for Batch {gpas_summary.batch}, Sample {gpas_summary.sample_name} added"
    )


def details(
    session: Session,
    gpas_summary: GpasSummary,
    analysis_record: models.Analysis,
):
    other_types = session.query(models.OtherType).all()
    for other_type in other_types:
        value = gpas_summary[other_type.code]

        other_record = (
            session.query(models.Other)
            .filter(
                models.Other.analysis == analysis_record,
                models.Other.other_type_code == other_type.code,
            )
            .first()
        )

        if value is None:
            if other_record:
                session.delete(other_record)
            continue

        if not other_record:
            other_record = models.Other(
                analysis=analysis_record, other_type_code=other_type.code
            )
            session.add(other_record)

        other_record["value_" + other_type.value_type] = value


def import_mutation(mutation_csv: str, mapping_csv: str, dryrun: bool) -> bool:
    """Upload data from a mutation csv"""
    logger.info(
        f"Verifying and uploading data to database from Mutation {mutation_csv}"
    )
    with get_session() as session:
        try:
            if not db_revision_ok(session):
                return False

            df_mut = pd.read_csv(mutation_csv)
            df_map = pd.read_csv(mapping_csv)

            df_merged = df_mut.merge(
                df_map, left_on="Sample ID", right_on="remote_sample_name", how="left"
            )
            pbar = ProgressBar(max_value=len(df_merged))

            for index, row in pbar(df_merged.iterrows()):
                try:
                    mut = Mutations(**row)

                    analysis_record = analysis(session, mut, index, dryrun)
                    session.flush()

                    mutation(session, mut, index, dryrun, analysis_record)
                    session.flush()

                except ValidationError as err:
                    for error in err.errors():
                        logger.error(
                            f"Mutation Row {index+2} {error['loc']} : {error['msg']}"
                        )
                except DBAPIError as err:
                    logger.error(f"Mutation Row {index+2} : {err}")

                except ValueError as err:
                    logger.error(f"Mutation Row {index+2} : {err}")

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


def mutation(
    session: Session,
    mutation: Mutations,
    index: int,
    dryrun: bool,
    analysis_record: models.Analysis,
) -> models.Mutations | None:
    if mut := (
        session.query(models.Mutations)
        .filter(
            models.Mutations.analysis == analysis_record,
            models.Mutations.species == mutation.species,
            models.Mutations.drug == mutation.drug,
            models.Mutations.gene == mutation.gene,
            models.Mutations.mutation == mutation.mutation,
        )
        .first()
    ):
        logger.info(
            f"Mutation row {index+2}: Mutation for Batch {mutation.batch}, Sample {mutation.sample_name}, Species {mutation.species}, Drug {mutation.drug}, Gene {mutation.gene}, Mutation {mutation.mutation} already exists{'' if dryrun else ', updating'}"
        )
    else:
        mut = models.Mutations(
            analysis=analysis_record,
            species=mutation.species,
            drug=mutation.drug,
            gene=mutation.gene,
            mutation=mutation.mutation,
        )
        session.add(mut)
        logger.info(
            f"Mutation row {index+2}: Mutation for Batch {mutation.batch}, Sample {mutation.sample_name}, Species {mutation.species}, Drug {mutation.drug}, Gene {mutation.gene}, Mutation {mutation.mutation} does not exist{'' if dryrun else ', adding'}"
        )

    mut.position = mutation.position
    mut.ref = mutation.ref
    mut.alt = mutation.alt
    mut.coverage = mutation.coverage
    mut.prediction = mutation.prediction
    mut.evidence = mutation.evidence
    mut.evidence_json = mutation.evidence_json # type: ignore

    return mut
