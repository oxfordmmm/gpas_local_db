# gpas_local_db

Database to be hosted locally in the hospital, holding GPAS sourced data plus others.

## Installation instructions

To install the python application that allows uploading of the Excel Spreadsheet containing Specimen, Samples, Storage and Runs to the Local Hospital Database, the following are required:

* Python version 3.11 or greater
* Access the OxfordMMM organisation in GitHub, including access to GitHub from the cli git application.

Clone the GitHub repository to you local machine

```bash
git clone git@github.com:oxfordmmm/gpas_local_db.git
```

It is suggested that you setup a Python virtual environment to host the program. There are multiple ways of doing this, below is one way:

```bash
cd gpas_local_db
python3.11 -m venv .venv
```

This will create the virtual environment under you project directory in the `.venv` folder.

Activate the virutal environment using the following command:

```bash
source .venv/bin/activate
```

You will need to specify the database connection information. This is possible using 3 different methods. Environmental variables, a `.env` file or options added to the `gpaslocal` command. The recommended way is to have a `.env` file with the following structure:

```bash
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = '5432'
DATABASE_NAME = 'gpas-local'
```

The values for the entries will be provided by your local administrator. A template file is provided, which can be copied using the following command:

```bash
cp env_template .env
```

Do not share your `.env` file with anybody or upload it to any sharing site.

To setup the Python program run the setup using `pip`:

```bash
pip install .
```

From here and whilst the virtual environment is active, you can run the `gpaslocal` command to test and upload spreadsheets.

To exit the virutal environment, use the `deactivate` command. You only need to run the setup the first time or when there is an update to the Python program.

## Updating the Python program

Activate your virtual environment using the relevant command e.g. `source .venv/bin/activate`. Pull down the latest version of the software and run the setup again:

```bash
git pull
pip install .
```

## Running the GpasLocal Python program

Use the `gpaslocal` command to upload spreadsheets based on the Excel Spreadsheet template provided. Use the `--dryrun` option to test if there are any errors with the import. The location of any errors should be reported. It is a good idea to use the `--dryrun` option until the import is clean.

## Running in development mode

To make changes to the Python program or the structure of the database, make sure that you are running inside a virtual environment and use the following command to setup the Python program instead of the one detailed above.

```bash
pip install .[dev]
```

### Updating the database

We use Alembic to handle the changes to the database (migrations), this is only available when running in Development mode. Use the following command to update the attached database to the latest version.

```bash
alembic upgrade head
```

If you have mode changes to the database models, you will need to generate a new migration using the following command.

```bash
alembic revision --autogenerate -m "message"
```

Replacing the message with something suitable. It is important to check the migration that is generated, to make sure it is sensible. Migrations are stored in the `migrations/versions` folder.
