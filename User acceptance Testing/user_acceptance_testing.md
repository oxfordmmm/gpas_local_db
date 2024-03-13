# User acceptance testing

This document describes what should be tested before the system is accepted by the users. When referring to a cell in the Excel workbook the following convention is used excel_sheet_name.`excel_column_name`

## Excel Workbook

The main input into the system is an MS Excel workbook, with currently six worksheets. Currently there is no protection applied to the workbook and the AdminLookup sheet is available. Having the excel workbook unprotected is for testing purposes.

### Overview Excel worksheet

This worksheet provides an overview of the four data entry worksheets, Runs, Specimens, Samples and Storage.

- [ ] Check that the description of each Excel data entry worksheet is correct and is an accurate description
- [ ] Check the description of the columns is correct.
- [ ] Make sure that the compulsory columns are correct and no others are needed

### Runs Excel worksheet

Allows the entry and update of runs. Go through each of the columns and make sure that the data validation and if applicable dropdowns are working. E.g. for a date field make sure that only a date can be entered.

- [ ] `Code` column has to be unique for each run. If you enter a duplicate code it will overwrite the previous one. Allows free form text with a length of up to 20 characters
- [ ] `run_date` column has to be a valid date.
- [ ] `site` provides a lookup dropdown populated from AdminLookup.`run_site`
  - [ ] Check that only values from AdminLookup.`run_site` can be entered
  - [ ] It should be possible to enter a blank value, although when the workbook is uploaded an error will be thrown if this is left blank for a entered row
- [ ] `sequencing_method` provides a lookup dropdown populated from AdminLookup.`sequencing_method`
  - [ ] Check that only values from the AdminLookup.`sequencing_method` can be entered
  - [ ] It should be possible to enter a blank value, although when the workbook is uploaded an error will be thrown if this is left blank for a entered row
- [ ] `machine` is a free form text field.
  - [ ] It should be possible to enter a blank value, although when the workbook is uploaded an error will be thrown if this is left blank for a entered row
  - [ ] Limited to a length of 20 characters
- [ ] `user` is a free form text field limited to 5 characters length
- [ ] `number_of_samples` is limited to an integer value (no decimal part)
- [ ] `flowcell` is a free form text field limited to 20 characters length
- [ ] `passed_qc` is limited to yes or no values. The yes or no values are taken from AdminLookup.`yes_no`
  - [ ] It should be possible to enter a blank value, although when the workbook is uploaded an error will be thrown if this is left blank for a entered row.
- [ ] `comment` free form text field, limited to 32,767 characters (Excel's limit of characters per cell)

### Specimens Excel Worksheet

Allows the entry and update of runs. Go through each of the columns and make sure that the data validation and if applicable dropdowns are working. E.g. for a date field make sure that only a date can be entered.

- [ ] `owner_site` provides a free form text field with maximum length of 50 characters. This value is mandatory for an entered row.
- [ ] `owner_user` provides a free form text field with a maximum length of 50 characters. This value is mandatory for an entered row.
- [ ] `accession` a free form text field with a maximum length of 20 characters. This value is mandatory for an entered row. Each specimen has to have a unique `accession` and `collection_date`.
- [ ] `collection_date` requires a valid date to be entered. This value is mandatory for an entered row. Each specimen has to have a unique `accession` and `collection_date`.
- [ ] `country_sample_taken` is the name of the country where the sample taken, provided as a lookup dropdown. The list is populated from AdminLookup.`country_names`. This follows the ISO3166 standard, and needs to be a valid country name. This value is mandatory for an entered row.
- [ ] `country_sample_taken_code` is populated when `country_sample_taken` is set. It is not meant to be edited by the user. Currently it can be modified because no protection is enabled on the Excel Worksheet. This is 3 digit code compliant with ISO3166.
- [ ] `specimen_type` is a free form text field with a maximum length of 50 characters.
- [ ] `specimen_qr_code` is a free form text field only limited in length by the excel limit of 32,767 characters
- [ ] `bar_code` is a free form text field only limited in length by the excel limit of 32,767 characters
- [ ] `organism` is a free form text field with a maximum length of 50 characters.
- [ ] `host` is a free form text field with a maximum length of 50 characters.
- [ ] `host_diseases` is a free form text field with a maximum length of 50 characters.
- [ ] `isolation_source` is a free form text field with a maximum length of 50 characters.
- [ ] `lat` requires a floating point value in the range -90 to +90.
- [ ] `lon` requires a floating point value in the range -90 to +90.

### Samples Excel worksheet

Allows the entry and update of samples. Go through each of the columns and make sure that the data validation and if applicable dropdowns are working. E.g. for a date field make sure that only a date can be entered.

- [ ] `run_code` a valid code of a run. Must either be in the Run sheet or already exist in the system. Allows free form text with a length of up to 20 characters.
- [ ] `accession` a valid accession of a specimen combined with the `collection_date`. The combination of `accession` and `collection_date` must exist in either the Specimens worksheet or already be in the database. A free form text field with a maximum length of 20 characters.
- [ ] `collection_date` a valid date. The combination of `accession` and `collection_date` must exist in either the Specimens worksheet or already be in the database.
- [ ] `guid` a free form text field with a maximum length of 64 characters. This is the unique identifier for the sample.
- [ ] `sample_category` a lookup dropdown. The list is populated from AdminLookup.`sample_category`
- [ ] `nucleic_acid_type` a lookup dropdown. The list is populated from AdminLookup.`nucleic_acid_type`.nucleic_acid_type
- [ ] `dilution_post_initial_concentration` a lookup dropdown. The list is populated from AdminLookup.`nucleic_acid_type`
- [ ] `extraction_date` a valid date. Can be blank
- [ ] `extraction_method` a free form text field with maximum length of 50 characters.
- [ ] `extraction_protocol` a free form text field with maximum length of 50 characters.
- [ ] `extraction_user` a free form text field with maximum length of 50 characters.
- [ ] `illumina_index` a free form text field with maximum length of 50 characters.
- [ ] `input_volume` a floating point number. Ranges from 0.1 to 30
- [ ] `library_pool_concentration` a floating point number. Ranges from 0.1 to 10
- [ ] `ont_barcode` is a free form text field only limited in length by the excel limit of 32,767 characters
- [ ] `phl_amplification` True or False
- [ ] `pre_sequence_concentration` a floating point number. Ranges from 01. to 1000
- [ ] `prep_kit` a free form text field with maximum length of 50 characters.
- [ ] `comment` is a free form text field only limited in length by the excel limit of 32,767 characters
- [ ] `spike_name_#` a free form text field with a maximum length of 50 characters. The hash is replaced with a number. The spike name and spike quantity fields are paired e.g. `spike_name_1` and `spike_quantity_1`.
- [ ] `spike_quantity_#` a floating point number. with a maximum value of 20

### Storage Excel worksheet

The worksheet holds the details of where the specimens are held. Go through each of the columns and make sure that the data validation and if applicable dropdowns are working. E.g. for a date field make sure that only a date can be entered.

All fields are mandatory, except for the `notes` cell in the storage sheet

- [ ] `accession` a valid accession of a specimen combined with the `collection_date`. The combination of `accession` and `collection_date` must exist in either the Specimens worksheet or already be in the database. A free form text field with a maximum length of 20 characters.
- [ ] `collection_date` a valid date. The combination of `accession` and `collection_date` must exist in either the Specimens worksheet or already be in the database.
- [ ] `freezer` free form text with a maximum length of 50
- [ ] `shelf` free form text with a maximum length of 50
- [ ] `rack` free form text with a maximum length of 50
- [ ] `tray` free form text with a maximum length of 50
- [ ] `box` free form text with a maximum length of 50
- [ ] `box_location` free form text with a maximum length of 50
- [ ] `storage_qr_code` is a free form text field only limited in length by the excel limit of 32,767 characters
- [ ] `date_into_storage` valid date
- [ ] `notes` is a free form text field only limited in length by the excel limit of 32,767 characters

## Upload command line program

The CLI command line program allows the upload of the Excel Workbook into the database on the local hospital network. Instructions for it's installation and use are in the [README.md](https://github.com/oxfordmmm/gpas_local_db).

As detailed in the `README.md` usage instructions, it is possible to use the `--dryrun` option to test the spreadsheet against the database. This is suggested for most of the testing.

When the contents of the database needs to be checked, you may not have access to the database, please ask the database administrator.

### For each of the Excel worksheets test

- [ ] mandatory cells are required and the upload program logs an error if not entered
- [ ] for non-mandatory fields check that a blank cell value is allowed

### For the Runs worksheet try entering and uploading:

- [ ] Blank and valid values for the mandatory cells in combination. If one of the mandatory cells is blank you should get an error. The mandatory columns are:
  - [ ] code
  - [ ] run_date
  - [ ] site
  - [ ] sequencing_method
  - [ ] machine
- [ ] For the following non mandatory fields enter both blanks and valid values. Ask the database admin to confirm they are uploaded correctly into the database when not using `--dryrun`
  - [ ] user
  - [ ] number_samples
  - [ ] flowcell
  - [ ] passed_qc
  - [ ] comment
- [ ] Enter two rows with the same 'code', not already in the database. You should get a message for the first stating that it does not exist, and a message for the second saying it does exist.

### For the Specimens worksheet try entering and uploading:

- [ ] Blank and valid values for the mandatory cells in combination. If one of the mandatory cells is blank you should get an error. The mandatory columns are:
  - [ ] owner_site
  - [ ] owner_user
  - [ ] accession
  - [ ] collection_date
  - [ ] country_sample_taken
- [ ] When entering the `country_sample_taken` the `country_sample_taken_code` should be automatically updated. Currently because the Excel workbook is not protected, it is possible to edit `country_sample_taken_code`, but you should not.
- [ ] For the following non mandatory fields try entering both blanks and valid values. Ask the database admin to confirm they are entered correctly into the database when not using `--dryrun`
  - [ ] specimen_type
  - [ ] specimen_qr_code
  - [ ] bar_code
  - [ ] organism
  - [ ] host
  - [ ] host_diseases
  - [ ] isolation_source
  - [ ] lat
  - [ ] lon

### For the Samples worksheet try entering and uploading:

- [ ] a `run_code` that does not exist in the run sheet or the database. You should get an error when uploading
- [ ] an `accession` and `collection_date` combination that does not exist either in the specimen sheet or the database. You should get an error
- [ ] a blank `accession`. You should get an error.
- [ ] a blank `collection_date`. You should should get an error.
- [ ] Enter two rows with the same `guid`, not already in the database. You should get a message for the first stating that it does not exist, and a message for the second saying it does exist.
- [ ] For the following non mandatory fields try entering both blanks and valid values. Ask the database admin to confirm they are entered correctly into the database when not using `--dryrun`
  - [ ] nucleic_acid_type
  - [ ] dilution_post_initial_concentration
  - [ ] extraction_date
  - [ ] extraction_method
  - [ ] extraction_protocol
  - [ ] extraction_user
  - [ ] illumina_index
  - [ ] input_volume
  - [ ] library_pool_concentration
  - [ ] ont_barcode
  - [ ] dna_amplification
  - [ ] pre_sequence_concentration
  - [ ] prep_kit
  - [ ] comment

### For the Storage worksheet try entering and uploading

- [ ] an `accession` and `collection_date` combination that does not exist either in the specimen sheet or the database. You should get an error
- [ ] Try combination of blanks and valid values for the following fields. Any blanks should return an error
  - [ ] freezer
  - [ ] shelf
  - [ ] rack
  - [ ] tray
  - [ ] box
  - [ ] box_location
  - [ ] storage_qr_code
  - [ ] date_into_storage
  - [ ] this field is optional, and can except freeform text, trying blank and free form text, no errors should be raised for this.
