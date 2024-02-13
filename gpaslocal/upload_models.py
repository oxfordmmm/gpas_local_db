from pydantic import BaseModel, ConfigDict, validator, constr, PositiveInt
from datetime import date
from iso3166 import countries
import pandas as pd # type: ignore
from typing import List
from gpaslocal.constants import SequencingMethod, SampleCategory, NucleicAcidType, NoneOrNan, ExcelDate, OptionalExcelDate


class ImportModel(BaseModel):
    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

class RunImport(ImportModel):
    code: constr(strip_whitespace=True, max_length=20)
    run_date: ExcelDate[date]
    site: constr(strip_whitespace=True, max_length=20)
    sequencing_method: SequencingMethod
    machine: constr(strip_whitespace=True, max_length=20)
    user: NoneOrNan[constr(strip_whitespace=True, max_length=5)] = None
    number_samples: NoneOrNan[PositiveInt] = None
    flowcell: NoneOrNan[constr(strip_whitespace=True, max_length=20)] = None
    passed_qc: NoneOrNan[bool] = None
    comment: NoneOrNan[str] = None
    
class SpecimensImport(ImportModel):
    owner_site: constr(strip_whitespace=True, max_length=50)
    owner_user: constr(strip_whitespace=True, max_length=50)
    accession: constr(strip_whitespace=True, max_length=20)
    collection_date: ExcelDate[date]
    country_sample_taken_code: constr(strip_whitespace=True, min_length=3, max_length=3)
    specimen_type: NoneOrNan[constr(strip_whitespace=True, max_length=50)] = None
    specimen_qr_code: NoneOrNan[str] = None
    bar_code: NoneOrNan[str] = None

    @validator('country_sample_taken_code')
    def validate_country_sample_taken_code(cls, v):
        if v not in countries:
            raise ValueError('Country code "{v}" not recognised')
        return v

class SamplesImport(ImportModel):
    run_code: constr(strip_whitespace=True, max_length=20)
    accession: constr(strip_whitespace=True, max_length=20)
    collection_date: ExcelDate[date]
    guid: constr(strip_whitespace=True, max_length=64)
    sample_category: SampleCategory
    nucleic_acid_type: NoneOrNan[List[NucleicAcidType]] = None
    # nucleic_acid_type: NoneOrNan[conset(NucleicAcidType, max_length=3)] = None
    dilution_post_initial_concentration: NoneOrNan[bool] = None
    extraction_date: OptionalExcelDate[date] = None
    extraction_method: NoneOrNan[constr(strip_whitespace=True, max_length=50)] = None
    extraction_protocol: NoneOrNan[constr(strip_whitespace=True, max_length=50)] = None
    extraction_user: NoneOrNan[constr(strip_whitespace=True, max_length=50)] = None
    illumina_index: NoneOrNan[constr(strip_whitespace=True, max_length=50)] = None
    input_volume: NoneOrNan[float] = None
    library_pool_concentration: NoneOrNan[float] = None
    ont_barcode: NoneOrNan[constr(strip_whitespace=True, max_length=50)] = None
    dna_amplification: NoneOrNan[bool] = None
    pre_sequence_concentration: NoneOrNan[float] = None
    prep_kit: NoneOrNan[constr(strip_whitespace=True, max_length=50)] = None
    comment: NoneOrNan[str] = None

    model_config = ConfigDict(extra='allow')
    
    @validator('nucleic_acid_type', pre=True)
    def split_nucleic_acid_type(cls, v):
        if pd.notna(v):
            # Convert to set and back to list to remove duplicates
            unique_values = list(set(value.strip() for value in v.split(',')))
            # Validate that each value is a valid NucleicAcidType
            for value in unique_values:
                if value not in NucleicAcidType.__args__:
                    raise ValueError(f"{value} is not a valid NucleicAcidType value")
            return unique_values
        return v
    