# import sys
# from pathlib import Path

# # Get the directory containing this script
# script_dir = Path(__file__).resolve().parent

# # Get the project root directory, which is the parent of the 'migrations' directory
# project_root_dir = script_dir.parent

# # Add the 'src' directory to the Python path
# sys.path.append(str(project_root_dir / 'src'))

from logging.config import fileConfig

from alembic import context

from gpaslocal.db import Model, init_db, dispose_db, get_session
import gpaslocal.models as models  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Model.metadata
init_db()

from gpaslocal.db import engine  # noqa: E402

config.set_main_option(
    "sqlalchemy.url", engine.url.render_as_string(hide_password=False)
)

# config.set_main_option(
#     "sqlalchemy.url", DATABASE_URL
# )

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    with get_session() as session:
        connection = session.connection()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


try:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
finally:
    # Dispose of the engine when migrations are done
    dispose_db()
