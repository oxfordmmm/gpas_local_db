from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from gpaslocal import config
from contextlib import contextmanager


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


engine = None
Session = None


def init_db():
    global engine, Session
    engine = create_engine(config.DATABASE_URL)
    Session = sessionmaker(engine)


@contextmanager
def get_session():
    session = Session()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.commit()
        session.close()


def dispose_db():
    global engine
    engine.dispose()
