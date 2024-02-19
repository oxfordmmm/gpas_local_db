import sys
import click
import click_log  # type: ignore
from gpaslocal.config import config
from gpaslocal.importer import import_data
from gpaslocal.logs import logger


def verify_configuration():
    if missing := [
        item for item in config.REQUIRED_KEYS if getattr(config, item, None) is None
    ]:
        click.echo(
            "Error:: Missing configuration keys. "
            "Ensure the following envirionment variables are set: "
            f"{', '.join(missing)}"
        )
        return False
    return True


@click.group()
@click.option("--user", default=config.DATABASE_USER, help="Database user name")
@click.option(
    "--password",
    default=config.DATABASE_PASSWORD,
    help="Database password for the user",
)
@click.option(
    "--host", default=config.DATABASE_HOST, help="Database server IP or hostname"
)
@click.option("--port", default=config.DATABASE_PORT, help="Database server port")
@click.option("--database", default=config.DATABASE_NAME, help="Database name")
@click_log.simple_verbosity_option(logger)
def cli(user: str, password: str, host: str, port: str, database: str):
    config.DATABASE_USER = user
    config.DATABASE_PASSWORD = password
    config.DATABASE_HOST = host
    config.DATABASE_PORT = port
    config.DATABASE_NAME = database
    if not verify_configuration():
        sys.exit(1)


@cli.command()
@click.argument("excel_sheet", type=click.Path(exists=True))
@click.option("--dryrun", is_flag=True)
def upload(excel_sheet: str, dryrun: bool):
    """Upload data from an excel sheet"""
    if dryrun:
        logger.info("Dry run mode, no data will be uploaded")
    import_data(excel_sheet, dryrun=dryrun)


if __name__ == "__main__":
    cli()
