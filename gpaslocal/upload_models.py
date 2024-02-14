from pydantic import BaseModel, ConfigDict, validator, PositiveInt, Field
from datetime import date
from iso3166 import countries
import pandas as pd # type: ignore
from typing import List, Annotated
from gpaslocal.constants import SequencingMethod, SampleCategory, NucleicAcidType, NoneOrNan, ExcelDate, OptionalExcelDate


class ImportModel(BaseModel):
    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

class RunImport(ImportModel):
    code: Annotated[str, Field(max_length=20, strip_whitespace=True)]
    run_date: ExcelDate[date]
    site: Annotated[str, Field(max_length=20, strip_whitespace=True)]
    sequencing_method: SequencingMethod
    machine: Annotated[str, Field(max_length=20, strip_whitespace=True)]
    user: NoneOrNan[Annotated[str, Field(max_length=5, strip_whitespace=True)]] = None
    number_samples: NoneOrNan[PositiveInt] = None
    flowcell: NoneOrNan[Annotated[str, Field(max_length=20, strip_whitespace=True)]] = None
    passed_qc: NoneOrNan[bool] = None
    comment: NoneOrNan[str] = None
    
class SpecimensImport(ImportModel):
    owner_site: Annotated[str, Field(max_length=50, strip_whitespace=True)]
    owner_user: Annotated[str, Field(max_length=50, strip_whitespace=True)]
    accession: Annotated[str, Field(max_length=20, strip_whitespace=True)]
    collection_date: ExcelDate[date]
    country_sample_taken_code: Annotated[str, Field(max_length=3, min_length=3, strip_whitespace=True)]
    specimen_type: NoneOrNan[Annotated[str, Field(max_length=50, strip_whitespace=True)]] = None
    specimen_qr_code: NoneOrNan[str] = None
    bar_code: NoneOrNan[str] = None

    @validator('country_sample_taken_code')
    def validate_country_sample_taken_code(cls, v):
        if v not in countries:
            raise ValueError('Country code "{v}" not recognised')
        return v

class SamplesImport(ImportModel):
    run_code: Annotated[str, Field(max_length=20, strip_whitespace=True)]
    accession: Annotated[str, Field(max_length=20, strip_whitespace=True)]
    collection_date: ExcelDate[date]
    guid: Annotated[str, Field(max_length=64, strip_whitespace=True)]
    sample_category: SampleCategory
    nucleic_acid_type: NoneOrNan[List[NucleicAcidType]] = None
    dilution_post_initial_concentration: NoneOrNan[bool] = None
    extraction_date: OptionalExcelDate[date] = None
    extraction_method: NoneOrNan[Annotated[str, Field(max_length=50, strip_whitespace=True)]] = None
    extraction_protocol: NoneOrNan[Annotated[str, Field(max_length=50, strip_whitespace=True)]] = None
    extraction_user: NoneOrNan[Annotated[str, Field(max_length=50, strip_whitespace=True)]] = None
    illumina_index: NoneOrNan[Annotated[str, Field(max_length=50, strip_whitespace=True)]] = None
    input_volume: NoneOrNan[float] = None
    library_pool_concentration: NoneOrNan[float] = None
    ont_barcode: NoneOrNan[Annotated[str, Field(max_length=50, strip_whitespace=True)]] = None
    dna_amplification: NoneOrNan[bool] = None
    pre_sequence_concentration: NoneOrNan[float] = None
    prep_kit: NoneOrNan[Annotated[str, Field(max_length=50, strip_whitespace=True)]] = None
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


class StoragesImport(ImportModel):
    accession: Annotated[str, Field(max_length=20, strip_whitespace=True)]
    collection_date: ExcelDate[date]
    freezer_id: Annotated[str, Field(max_length=20, strip_whitespace=True)]
    freezer_compartment: Annotated[str, Field(max_length=20, strip_whitespace=True)]
    freezer_sub_compartment: Annotated[str, Field(max_length=20, strip_whitespace=True)]
    storage_qr_code: str
    date_into_storage: ExcelDate[date]