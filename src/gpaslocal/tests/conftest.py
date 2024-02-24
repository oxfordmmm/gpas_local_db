# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from gpaslocal.db import Model
from gpaslocal import models # noqa: F401
from sqlalchemy.pool import NullPool

@pytest.fixture(scope="function")
def test_session(postgresql):
    """Fixture to create a database session for testing."""
    # Create a SQLAlchemy engine using the URL provided by pytest-postgresql
    connection = f'postgresql+psycopg2://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}'
    print(connection)
    engine = create_engine(connection, echo=False, poolclass=NullPool)
    Model.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    # Here you can also set up your database schema if needed
    yield session  # Provide the session for the test
    session.close()  # Clean up after the test