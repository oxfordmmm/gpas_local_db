import ast
import astor  # type: ignore
from logging.config import fileConfig

from alembic import context
from alembic.script import ScriptDirectory

from gpaslocal.db import Model, get_session
import gpaslocal.models as models  # noqa: F401
from gpaslocal.config import config as app_config

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

# to keep mypy quiet do an assert
config.set_main_option("sqlalchemy.url", app_config.DATABASE_URL)


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

    head_revision = ScriptDirectory.from_config(config).as_revision_number("head")
    with open("src/gpaslocal/__init__.py", "r") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__dbrevision__"
        ):
            node.value = ast.Str(s=head_revision)

    with open("src/gpaslocal/__init__.py", "w") as f:
        f.write(astor.to_source(tree))


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
