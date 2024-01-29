from typing import get_args
from pydantic import BaseModel, ConfigDict, condate, validator, constr, PositiveInt, Optional, conset
from datetime import date
from src.gpas.constants import SequencingMethod, SampleCategory, NucleicAcidType
from iso3166 import countries


class RunImport(BaseModel):
    code: constr(strip_whitespace=True, max_length=20)
    run_date: condate(ge=date(2020, 1, 1))
    site: constr(strip_whitespace=True, max_length=20)
    sequencing_method: SequencingMethod
    machine: constr(strip_whitespace=True, max_length=20)
    user: Optional(constr(strip_whitespace=True, max_length=5)) = None
    number_samples: Optional(PositiveInt) = None
    flowcell: Optional(constr(strip_whitespace=True, max_length=20)) = None
    passed_qc: Optional(bool) = None
    comment: Optional(str) = None
    

class SpecimensImport(BaseModel):
    owner_site: constr(strip_whitespace=True, max_length=50)
    owner_user: constr(strip_whitespace=True, max_length=50)
    accession: constr(strip_whitespace=True, max_length=20)
    collection_date: condate(ge=date(2020, 1, 1))
    country_sample_taken_code: constr(strip_whitespace=True, min_length=3, max_length=3)
    specimen_type: Optional(constr(strip_whitespace=True, max_length=50)) = None
    speciment_qr_code: Optional[str] = None
    bar_code: Optional[str] = None

    @validator('country_sample_taken_code')
    def validate_country_sample_taken_code(cls, v):
        if v not in countries:
            raise ValueError('Country code "{v}" not recognised')
        return v

class SamplesImport(BaseModel):
    run_code: constr(strip_whitespace=True, max_length=20)
    accession: constr(strip_whitespace=True, max_length=20)
    collection_date: condate(ge=date(2020, 1, 1))
    guid: constr(strip_whitespace=True, max_length=64)
    sample_category: SampleCategory
    nucler_acid_type: Optional(conset(NucleicAcidType, max_items=3)) = None
    dilution_post_initial_concentration: Optional(bool) = None
    extraction_date: Optional[condate(ge=date(2020, 1, 1))] = None
    extraction_method: Optional[constr(strip_whitespace=True, max_length=50)] = None
    extraction_protocol: Optional[constr(strip_whitespace=True, max_length=50)] = None
    extraction_user: Optional[constr(strip_whitespace=True, max_length=50)] = None
    illumina_index: Optional[constr(strip_whitespace=True, max_length=50)] = None
    input_volume: Optional[float] = None
    library_pool_concentration: Optional[float] = None
    ont_barcode: Optional[constr(strip_whitespace=True, max_length=50)] = None
    dna_amplification: Optional[bool] = None
    pre_sequence_concentration: Optional[float] = None
    prep_kit: Optional[constr(strip_whitespace=True, max_length=50)] = None
    comment: Optional[str] = None

    model_config = ConfigDict(extra='allow')
    