import defopt # type: ignore
import pandas as pd
import sys
from upload_models import RunImport
from pydantic import ValidationError
import logging
import errorhandler

logger = logging.getLogger()
error_handler = errorhandler.ErrorHandler()

log_format = logging.Formatter('%(levelname)s: %(message)s')
sh = logging.StreamHandler(stream=sys.stderr)
sh.setFormatter(log_format)

logger.addHandler(sh)
logger.setLevel(logging.INFO)

def import_sample_data(excel_sheet: str) -> None:
    print("Importing sample data from", excel_sheet)
    
    try:
        df = pd.read_excel(excel_sheet, sheet_name='Runs')
        
        for index, row in df.iterrows():
            try:
                run_import = RunImport(**row)
            except ValidationError as err:
                for error in err.errors():
                    logger.error(f"Row {index} {error['loc']} : {error['msg']}")
            # print(run_import)
            
    except Exception as e:
        raise e

    if error_handler.fired:
        logger.error("Validation failed, please see log messages for details")

def main() -> None:
    defopt.run(
        {
            "upload": import_sample_data,
        },
        no_negated_flags=True,
        strict_kwonly=True,
        short={},
    )
    
if __name__ == '__main__':
    main()