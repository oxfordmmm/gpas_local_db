from typing import get_args, Optional
from datetime import datetime, date
from sqlalchemy import String, ForeignKey, Text, text, UniqueConstraint, Enum, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column, WriteOnlyMapped, validates
from db import Model
from iso3166 import countries
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from constants import ValueType, SampleCategory, NucleicAcidType, db_user, db_timestamp

class GpasLocalModel(Model):
    __abstract__ = True
    
    created_by: Mapped[db_user]
    created_at: Mapped[db_timestamp]
    updated_by: Mapped[db_user]
    updated_at: Mapped[db_timestamp]

class Owner(GpasLocalModel):
    __tablename__ = 'owners'

    id: Mapped[int] = mapped_column(primary_key=True)
    site: Mapped[str] = mapped_column(String(50), nullable=False)
    user: Mapped[str] = mapped_column(String(50), nullable=False)
    
    specimens: Mapped[list['Specimen']] = relationship('Specimen', backref='owner')
    
    UniqueConstraint(site, user)
    

class Specimen(GpasLocalModel):
    __tablename__ = 'specimens'

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('owners.id'))
    accession: Mapped[str] = mapped_column(String(20), nullable=False)
    collection_date: Mapped[date] = mapped_column(default=datetime.utcnow, nullable=False)
    country_sample_taken: Mapped[str] = mapped_column(String(3), nullable=False)
    specimen_type: Mapped[str] = mapped_column(String(50), nullable=True)
    specimen_qr_code: Mapped[text] = mapped_column(Text, nullable=True)
    bar_code: Mapped[text] = mapped_column(Text, nullable=True)
    
    owner: WriteOnlyMapped[Owner] = relationship('Owner', backref='specimens')
    samples: Mapped[list['Sample']] = relationship('Sample', backref='specimen')
    
    UniqueConstraint(accession, collection_date)
    
    @validates('country_sample_taken')
    def validate_country_sample_taken(self, key, country_sample_taken):
        if country_sample_taken not in countries:
            raise ValueError(f'Invalid country code: {country_sample_taken}')
        return country_sample_taken
    

class Run(GpasLocalModel):
    __tablename__ = 'runs'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    run_date: Mapped[date] = mapped_column(default=datetime.utcnow, nullable=False)
    site: Mapped[str] = mapped_column(String(20), nullable=False)
    sequencing_method: Mapped[str] = mapped_column(String(20), nullable=False)
    machine: Mapped[str] = mapped_column(String(20), nullable=False)
    user: Mapped[str] = mapped_column(String(5), nullable=True)
    number_samples: Mapped[int] = mapped_column(default=0, nullable=True)
    flowcell: Mapped[str] = mapped_column(String(20), nullable=True)
    passed_qc: Mapped[bool] = mapped_column(default=False, nullable=True)
    comment: Mapped[text] = mapped_column(Text, nullable=True)

    samples: Mapped[list['Sample']] = relationship('Sample', backref='run')


class Sample(GpasLocalModel):
    __tablename__ = 'samples'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    specimen_id: Mapped[int] = mapped_column(ForeignKey('specimens.id'))
    run_id: Mapped[int] = mapped_column(ForeignKey('runs.id'))
    guid: Mapped[str] = mapped_column(String(64), unique=True)
    SampleCategory: Mapped[SampleCategory] = mapped_column(Enum(
        *get_args(SampleCategory),
        name='sample_category',
        create_constraint=True,
        validate_strings=True
    ), nullable=True)
    nucleic_acid_type: Mapped[set[NucleicAcidType]] = mapped_column(MutableList.as_mutable(ARRAY(String)), nullable=True)

    run: WriteOnlyMapped['Run'] = relationship('Run', backref='samples')
    specimen: WriteOnlyMapped['Specimen'] = relationship('Specimen', backref='samples')
    details: Mapped[list['SampleDetail']] = relationship('SampleDetail', backref='sample')
    spikes: Mapped[list['Spike']] = relationship('Spike', backref='sample')
    analyses: Mapped[list['Analysis']] = relationship('Analysis', backref='sample')
    
    @validates('nucleic_acid_type')
    def validate_nucleic_acid_type(self, key, nucleic_acid_type):
        if not isinstance(nucleic_acid_type, list):
            raise ValueError('Nucleic acid type must be a list')
        # remove duplicate values
        unique_nucleic_acid_type = list(set(nucleic_acid_type))
        return unique_nucleic_acid_type
    

class SampleDetail(GpasLocalModel):
    __tablename__ = 'sample_details'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey('samples.id'))
    sample_detail_type_code: Mapped[str] = mapped_column(ForeignKey('sample_detail_types.code'))
    value_str: Mapped[str] = mapped_column(String(50), nullable=True)
    value_int: Mapped[int] = mapped_column(nullable=True)
    value_float: Mapped[float] = mapped_column(nullable=True)
    value_bool: Mapped[bool] = mapped_column(nullable=True)
    value_date: Mapped[date] = mapped_column(nullable=True)
    value_text: Mapped[text] = mapped_column(Text, nullable=True)

    sample: WriteOnlyMapped['Sample'] = relationship('Sample', backref='details')
    sample_detail_type: WriteOnlyMapped['SampleDetailType'] = relationship('SampleDetailType', backref='details')
    
    

class SampleDetailType(GpasLocalModel):
    __tablename__ = 'sample_detail_types'
    
    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[text] = mapped_column(Text, nullable=True)
    value_type: Mapped[ValueType] = mapped_column(Enum(
        *get_args(ValueType),
        name='value_type',
        create_constraint=True,
        validate_strings=True
    ))

    details: Mapped[list['SampleDetail']] = relationship('SampleDetail', backref='sample_detail_type')
    
    
class Spike(GpasLocalModel):
    __tablename__ = 'spikes'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey('samples.id'))
    name: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[str] = mapped_column(String(20))

    sample: WriteOnlyMapped['Sample'] = relationship('Sample', backref='spikes')
    
    
class Analysis(GpasLocalModel):
    __tablename__ = 'analyses'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey('samples.id'))
    assay_system: Mapped[str] = mapped_column(String(20))

    sample: WriteOnlyMapped['Sample'] = relationship('Sample', backref='analyses')
    speciations: Mapped[list['Speciation']] = relationship('Speciation', backref='analysis')
    others: Mapped[list['Other']] = relationship('Other', backref='analysis')
    drug_resistances: Mapped[list['DrugResistance']] = relationship('DrugResistance', backref='analysis')
    
    
class Speciation(GpasLocalModel):
    __tablename__ = 'speciations'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey('analyses.id'))
    species_number: Mapped[int] = mapped_column()
    species: Mapped[str] = mapped_column(String(100))
    sub_species: Mapped[str] = mapped_column(String(100))
    analysis_date: Mapped[date] = mapped_column(default=datetime.utcnow)
    data: Mapped[Optional[dict|list]] = mapped_column(type_=JSON, nullable=True)
    
    analysis: WriteOnlyMapped['Analysis'] = relationship('Analysis', backref='speciations')
    
    UniqueConstraint(analysis_id, species_number)
    
    
class Other(GpasLocalModel):
    __tablename__ = 'others'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey('analyses.id'))
    other_type_code: Mapped[str] = mapped_column(ForeignKey('other_types.code'))
    value_str: Mapped[str] = mapped_column(String(50), nullable=True)
    value_int: Mapped[int] = mapped_column(nullable=True)
    value_float: Mapped[float] = mapped_column(nullable=True)
    value_bool: Mapped[bool] = mapped_column(nullable=True)
    value_date: Mapped[date] = mapped_column(nullable=True)
    value_text: Mapped[text] = mapped_column(Text, nullable=True)
    
    analysis: WriteOnlyMapped['Analysis'] = relationship('Analysis', backref='others')
    other_type: WriteOnlyMapped['OtherType'] = relationship('OtherType', backref='others')
    

class OtherType(GpasLocalModel):
    __tablename__ = 'other_types'
    
    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[text] = mapped_column(Text, nullable=True)
    value_type: Mapped[ValueType] = mapped_column(Enum(
        *get_args(ValueType),
        name='value_type',
        create_constraint=True,
        validate_strings=True
    ))
    
    others: Mapped[list['Other']] = relationship('Other', backref='other_type')


class DrugResistance(GpasLocalModel):
    __tablename__ = 'drug_resistances'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey('analyses.id'))
    antibiotic: Mapped[str] = mapped_column(String(20))
    drug_resistance_result_type_code: Mapped[str] = mapped_column(ForeignKey('drug_resistance_result_types.code'))
    
    analysis: WriteOnlyMapped['Analysis'] = relationship('Analysis', backref='drug_resistances')
    drug_resistance_result_type: WriteOnlyMapped['DrugResistanceResultType'] = relationship('DrugResistanceResultType', backref='drug_resistances')
    
    UniqueConstraint(analysis_id, antibiotic)
    

class DrugResistanceResultType(GpasLocalModel):
    __tablename__ = 'drug_resistance_result_types'
    
    code: Mapped[str] = mapped_column(String(1), primary_key=True)
    description: Mapped[text] = mapped_column(Text, nullable=True)
    
    drug_resistances: Mapped[list['DrugResistance']] = relationship('DrugResistance', backref='drug_resistance_result_type')