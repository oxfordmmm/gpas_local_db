from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
    PositiveInt,
    Field,
)
from datetime import date
from iso3166 import countries
import pandas as pd  # type: ignore
from typing import List, Annotated, Optional
from gpaslocal.constants import ExcelStr
from gpaslocal.constants import (
    SequencingMethod,
    SampleCategory,
    NucleicAcidType,
    NoneOrNan,
    ExcelDate,
    OptionalExcelDate,
)
from typing_extensions import Self


class ImportModel(BaseModel):
    def __getitem__(self, item):
        return self.__dict__[item] if item in self.__dict__ else None

    def __setitem__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value


class RunImport(ImportModel):
    code: Annotated[ExcelStr, Field(max_length=20)]
    run_date: ExcelDate[date]
    site: Annotated[ExcelStr, Field(max_length=20)]
    sequencing_method: SequencingMethod
    machine: Annotated[ExcelStr, Field(max_length=20)]
    user: NoneOrNan[Annotated[ExcelStr, Field(max_length=5)]] = None
    number_samples: NoneOrNan[PositiveInt] = None
    flowcell: NoneOrNan[Annotated[ExcelStr, Field(max_length=20)]] = None
    passed_qc: NoneOrNan[bool] = None
    comment: NoneOrNan[ExcelStr] = None


class SpecimensImport(ImportModel):
    owner_site: Annotated[ExcelStr, Field(max_length=50)]
    owner_user: Annotated[ExcelStr, Field(max_length=50)]
    accession: Annotated[ExcelStr, Field(max_length=20)]
    collection_date: ExcelDate[date]
    country_sample_taken_code: Annotated[str, Field(max_length=3, min_length=3)]
    specimen_type: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    specimen_qr_code: NoneOrNan[ExcelStr] = None
    bar_code: NoneOrNan[ExcelStr] = None
    organism: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    host: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    host_diseases: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    isolation_source: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    lat: NoneOrNan[float] = None
    lon: NoneOrNan[float] = None

    model_config = ConfigDict(extra="allow")

    @field_validator("country_sample_taken_code")
    def validate_country_sample_taken_code(cls, v):
        if v not in countries:
            raise ValueError('Country code "{v}" not recognised')
        return v


class SamplesImport(ImportModel):
    run_code: Annotated[ExcelStr, Field(max_length=20)]
    accession: Annotated[ExcelStr, Field(max_length=20)]
    collection_date: ExcelDate[date]
    guid: Annotated[ExcelStr, Field(max_length=64)]
    sample_category: NoneOrNan[SampleCategory] = None
    nucleic_acid_type: NoneOrNan[List[NucleicAcidType]] = None
    dilution_post_initial_concentration: NoneOrNan[bool] = None
    extraction_date: OptionalExcelDate[date] = None
    extraction_method: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    extraction_protocol: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    extraction_user: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    illumina_index: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    input_volume: NoneOrNan[float] = None
    library_pool_concentration: NoneOrNan[float] = None
    ont_barcode: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    dna_amplification: NoneOrNan[bool] = None
    pre_sequence_concentration: NoneOrNan[float] = None
    prep_kit: NoneOrNan[Annotated[ExcelStr, Field(max_length=50)]] = None
    comment: NoneOrNan[ExcelStr] = None

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def split_nucleic_acid_type(cls, values):
        v = values.get("nucleic_acid_type")
        if pd.notna(v):
            # Convert to set and back to list to remove duplicates
            unique_values = list({value.strip() for value in v.split(",")})
            # Validate that each value is a valid NucleicAcidType
            for value in unique_values:
                if value not in NucleicAcidType.__args__:
                    raise ValueError(f"{value} is not a valid NucleicAcidType value")
            values["nucleic_acid_type"] = unique_values
        return values


class StoragesImport(ImportModel):
    accession: Annotated[str, Field(max_length=20)]
    collection_date: ExcelDate[date]
    freezer: Annotated[ExcelStr, Field(max_length=50)]
    shelf: Annotated[ExcelStr, Field(max_length=50)]
    rack: Annotated[ExcelStr, Field(max_length=50)]
    tray: Annotated[ExcelStr, Field(max_length=50)]
    box: Annotated[ExcelStr, Field(max_length=50)]
    box_location: Annotated[ExcelStr, Field(max_length=50)]
    storage_qr_code: ExcelStr
    date_into_storage: ExcelDate[date]
    notes: NoneOrNan[ExcelStr] = None


class GpasSummary(ImportModel):
    sample_name: Annotated[ExcelStr, Field(max_length=20)]
    batch: Annotated[ExcelStr, Field(max_length=20, alias="Batch")]
    main_species: Annotated[ExcelStr, Field(max_length=50, alias="Main Species")]
    species: Optional[str]
    sub_species: Optional[str]
    
    model_config = ConfigDict(extra="allow")
    
    @field_validator("sample_name", mode="before")
    def validate_sample_name(cls, v):
        if pd.isna(v):
            raise ValueError("Sample name not found in mapping file")
        return v
    
    @model_validator(mode="before")
    def split_species(self) -> Self:
        if pd.notna(self['Main Species']):
            split_species = self['Main Species'].split(" ", 1)
            self['species'] = split_species[0]
            self['sub_species'] = split_species[1] if len(split_species) > 1 else None
        else:
            self['species'] = None
            self['sub_species'] = None
        return self