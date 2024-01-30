from pydantic import BaseModel, ConfigDict, condate, validator, constr, PositiveInt, conset
from datetime import date
from iso3166 import countries
from constants import SequencingMethod, SampleCategory, NucleicAcidType, NoneOrNan


class RunImport(BaseModel):
    code: constr(strip_whitespace=True, max_length=20)
    run_date: condate(ge=date(2020, 1, 1))
    site: constr(strip_whitespace=True, max_length=20)
    sequencing_method: SequencingMethod
    machine: constr(strip_whitespace=True, max_length=20)
    user: NoneOrNan[constr(strip_whitespace=True, max_length=5)] = None
    number_samples: NoneOrNan[PositiveInt] = None
    flowcell: NoneOrNan[constr(strip_whitespace=True, max_length=20)] = None
    passed_qc: NoneOrNan[bool] = None
    comment: NoneOrNan[str] = None
    

class SpecimensImport(BaseModel):
    owner_site: constr(strip_whitespace=True, max_length=50)
    owner_user: constr(strip_whitespace=True, max_length=50)
    accession: constr(strip_whitespace=True, max_length=20)
    collection_date: condate(ge=date(2020, 1, 1))
    country_sample_taken_code: constr(strip_whitespace=True, min_length=3, max_length=3)
    specimen_type: NoneOrNan[constr(strip_whitespace=True, max_length=50)] = None
    speciment_qr_code: NoneOrNan[str] = None
    bar_code: NoneOrNan[str] = None

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
    nucler_acid_type: NoneOrNan[conset(NucleicAcidType, max_length=3)] = None
    dilution_post_initial_concentration: NoneOrNan[bool] = None
    extraction_date: NoneOrNan[condate(ge=date(2020, 1, 1))] = None
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
    