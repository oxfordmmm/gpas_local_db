# gpas_local_db

Database to be hosted locally in the hospital, holding GPAS sourced data plus others.

## Installation instructions

To install the Python Client on your local machine download the executable from [https://github.com/oxfordmmm/gpas_local_db/releases](https://github.com/oxfordmmm/gpas_local_db/releases), choosing the executable that matches your platform. Put the executable into a folder on your computer. Also download the following two files and put them into the same directory as the executable.

[https://github.com/oxfordmmm/gpas_local_db/blob/main/ExcelSheets/RunSampleImport.xlsm](https://github.com/oxfordmmm/gpas_local_db/blob/main/ExcelSheets/RunSampleImport.xlsm)
[https://github.com/oxfordmmm/gpas_local_db/blob/main/env_template](https://github.com/oxfordmmm/gpas_local_db/blob/main/env_template)

Note: The download button looks like an arrow putting downward into a box.

Rename the `env_template` file to `.env` and edit using a plain text editor (not MS Word). The contents of the `.env` file should look like the following

```env
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = '5432'
DATABASE_NAME = ''
```

Your system administrator should be able to give you the values to enter into the `.env` file. Please do not share these values or the file with anyone. Please also do not upload the file to any kind of sharing site.

You will only need to setup the `.env` file when first downloading the file.

### Mac code signing

Modern Macs require executables to be code signed. The executable you downloaded is currently not code signed, so you will need to tell the system that this is ok. You should only do this if you are happy of the provenance of the executable.

Open a terminal and cd into the directory where you have downloaded the files. You may need to make the file executable using a command similar to the following:

```bash
chmod +x ./gpaslocal-v0.0.15-macOS-arm64
```

You will then need to release the file from quarritine using a command similar to the following:

```bash
xattr -d com.apple.quarantine ./gpaslocal-v0.0.15-macOS-arm64
```

### Entering the data

Use the Excel spreadsheet that you download as a template. When opening the spreadsheet, you will get a warning about macros, please click the enable macros button if you are happy with the provenance of the Excel Workbook. Using Excel enter you data into the four worksheets Runs, Specimens, Samples and Storage.

### Running the application

To run the use a command similar to the following for Mac and Linux

```bash
./gpaslocal-v0.0.15-macOS-arm64 upload <spreadsheet_name> --dryrun
```

and for Windows

```cmd
what is this???
```

Replacing the executable name with the one you download (the version number will probably be different), and replace `<spreadsheet_name>` with the name of your spreadsheet.

You will probably get errors, so if they relate to the data entered, you can fix them in the spreadsheet. Otherwise contact you system admninistrator for advice.

Keep running with the `--dryrun` flag until you get no errors. You can then remove the `--dryrun` flag to apply the data to the database.

## Running in development mode

Clone the repo to your local machine. You will need to setup the `.env` file as detailed above. You will need to create a blank database and a database user that has permissions to that database. Put this information in the `.env` file. To make changes to the Python program or the structure of the database, make sure that you are running inside a virtual environment and use the following command to setup the Python program.

```bash
pip install .[dev]
```

### Updating the database

We use Alembic to handle the changes to the database (migrations), this is only available when running in Development mode. Use the following command to update the attached database to the latest version.

```bash
alembic upgrade head
```

If you have made changes to the database models, you will need to generate a new migration using the following command.

```bash
alembic revision --autogenerate -m "message"
```

Replacing the message with something suitable. It is important to check the migration that is generated, to make sure it is sensible. Migrations are stored in the `migrations/versions` folder.

Please note when running migrations the `__dbrevision__` variable in `src\gpaslocal\__init__.py` will be updated to the
new head revision. Please remember to commit this file in addition to your bd migration files.
