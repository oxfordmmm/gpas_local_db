from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from gpaslocal.config import config
from contextlib import contextmanager
from gpaslocal import __dbrevision__
from gpaslocal.logs import logger

def db_revision_ok(session: Session) -> bool:
    db_revision = session.execute(
        text("SELECT MAX(version_num) FROM alembic_version")
    ).scalar()
    if db_revision != __dbrevision__:
        logger.error(
            f"Database revision {db_revision} does not match the expected revision {__dbrevision__}"
        )
        return False
    return True

class Model(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

@contextmanager
def get_session():
    engine = create_engine(config.DATABASE_URL)
    Session = sessionmaker(engine)
    session = Session()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.commit()
        session.close()
        engine.dispose()
