# conftest.py
from typing import Generator
import pytest
import logging
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from gpaslocal.db import Model
from gpaslocal import models  # noqa: F401
from sqlalchemy.pool import NullPool


@pytest.fixture(scope="function")
def db_session(postgresql) -> Generator[Session, None, None]:
    """Fixture to create a database session for testing."""
    # Create a SQLAlchemy engine using the URL provided by pytest-postgresql
    connection = f"postgresql+psycopg2://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"
    engine = create_engine(connection, echo=False, poolclass=NullPool)
    Model.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    ## Add owners
    session.add(models.Owner(site="SiteC", user="User3"))
    session.add(models.Owner(site="blah", user="blah-user"))

    ## add countries
    session.add(
        models.Country(
            code="GBR", name="United Kingdom", code2="UK", lat=54.0, lon=-2.0
        )
    )

    ## add specimen_detail_types, omitting description as not really needed for testing
    specimen_detail_types = [
        {"code": "organism", "description": "", "value_type": "str"},
        {"code": "host", "description": "", "value_type": "str"},
        {"code": "host_diseases", "description": "", "value_type": "str"},
        {"code": "isolation_source", "description": "", "value_type": "int"},
        {"code": "lat", "description": "", "value_type": "float"},
        {"code": "lon", "description": "", "value_type": "float"},
    ]
    for detail_type in specimen_detail_types:
        session.add(models.SpecimenDetailType(**detail_type))

    ## add sample_detail_types
    sample_detail_types = [
        {"code": "extraction_method", "description": "", "value_type": "str"},
        {"code": "extraction_protocol", "description": "", "value_type": "float"},
        {"code": "extraction_date", "description": "", "value_type": "date"},
        {"code": "extraction_user", "description": "", "value_type": "str"},
        {"code": "dna_amplification", "description": "", "value_type": "bool"},
        {
            "code": "pre_sequence_concentration",
            "description": "",
            "value_type": "float",
        },
        {
            "code": "dilution_post_initial_concentration",
            "description": "",
            "value_type": "bool",
        },
        {"code": "input_volume", "description": "", "value_type": "float"},
    ]
    for detail_type in sample_detail_types:
        session.add(models.SampleDetailType(**detail_type))

    ## add runs
    session.add(
        models.Run(
            code="Run1", site="SiteA", sequencing_method="Illumina", machine="Machine1"
        )
    )
    session.add(
        models.Run(
            code="test1",
            run_date=date.fromisoformat("2024-01-01"),
            site="Oxford",
            sequencing_method="Illumina",
            machine="test_m1",
            user="blah",
            number_samples=2,
            flowcell="fc2",
            passed_qc=True,
            comment="test_comment",
        )
    )

    ## add specimens
    session.add(
        models.Specimen(
            accession="123test",
            collection_date=date.fromisoformat("2021-01-01"),
            country_sample_taken_code="GBR",
            owner=session.query(models.Owner).first(),
        )
    )

    # commit the added records
    session.commit()

    # Here you can also set up your database schema if needed
    yield session  # Provide the session for the test
    session.close()  # Clean up after the test


@pytest.fixture(autouse=True)
def set_caplog_level(caplog):
    caplog.set_level(logging.INFO, logger="gpas-local")
