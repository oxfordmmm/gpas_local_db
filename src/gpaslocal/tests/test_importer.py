import pytest
import os
from datetime import date
from sqlalchemy import text
from gpaslocal.upload_models import SpecimensImport
from gpaslocal import models
from gpaslocal.importer import owner, find_run, find_specimen, runs


def test_some_database_interaction(db_session):
    # Use test_session directly here to interact with the database
    result = db_session.execute(text("SELECT * FROM owners"))
    assert result.rowcount >= 0


@pytest.mark.parametrize(
    "index, owner_site, owner_user, dryrun, expected_log, test_id",
    [
        (
            0,
            "SiteA",
            "User1",
            False,
            "Specimens Sheet Row 2: Owner SiteA, User1 does not exist, adding",
            "happy_path_new_owner",
        ),
        (
            1,
            "SiteB",
            "User2",
            True,
            "Specimens Sheet Row 3: Owner SiteB, User2 does not exist",
            "happy_path_dryrun",
        ),
        (2, "SiteC", "User3", False, None, "happy_path_existing_owner"),
    ],
)
def test_owner(
    db_session,
    index,
    owner_site,
    owner_user,
    dryrun,
    expected_log,
    test_id,
    caplog,
):
    # Arrange
    specimen_import = SpecimensImport(
        owner_site=owner_site,
        owner_user=owner_user,
        accession="123test",
        collection_date="2021-01-01",
        country_sample_taken_code="GBR",
    )

    # Act
    result = owner(db_session, index, specimen_import, dryrun)

    # Assert
    assert isinstance(result, models.Owner)
    assert result.site == owner_site
    assert result.user == owner_user
    if expected_log:
        assert expected_log in caplog.text
    else:
        assert caplog.text == ""


def test_find_run(db_session):
    # Arrange
    run_code = "Run1"
    run_site = "SiteA"
    run_sequencing_method = "Illumina"
    run_machine = "Machine1"

    # Act
    result = find_run(db_session, run_code)

    # Assert
    assert isinstance(result, models.Run)
    assert result.code == run_code
    assert result.site == run_site
    assert result.sequencing_method == run_sequencing_method
    assert result.machine == run_machine
    assert result.id == 1
    assert result.created_at
    assert result.updated_at


def test_find_run_not_found(db_session):
    # Arrange
    run_code = "Run2"

    # Act and assert
    with pytest.raises(ValueError):
        find_run(db_session, run_code)


def test_find_specimen(db_session):
    # Arrange
    specimen_accession = "123test"
    specimen_collection_date = date.fromisoformat("2021-01-01")
    specimen_country_sample_taken_code = "GBR"

    result = find_specimen(db_session, specimen_accession, specimen_collection_date)

    assert isinstance(result, models.Specimen)
    assert result.accession == specimen_accession
    assert result.collection_date == specimen_collection_date
    assert result.country_sample_taken_code == specimen_country_sample_taken_code
    assert result.id == 1
    assert result.created_at
    assert result.updated_at


def test_find_specimen_not_found(db_session):
    # Arrange
    specimen_accession = "456test"
    specimen_collection_date = date.fromisoformat("2021-01-01")

    with pytest.raises(ValueError):
        find_specimen(db_session, specimen_accession, specimen_collection_date)


def test_runs_upload_ok_new(db_session, caplog):
    # Arrange
    dir_path = os.path.dirname(os.path.realpath(__file__))
    xl_ok = os.path.join(dir_path, "data", "test_no_errors.xlsm")

    runs(db_session, xl_ok, dryrun=True)

    assert "Sheet Row 2: Run test1 already exists" in caplog.text
    assert "Runs Sheet Row 3: Run test2 does not exist" in caplog.text
