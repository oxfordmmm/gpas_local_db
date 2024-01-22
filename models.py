from typing import Annotated, Literal, get_args, Optional
from datetime import datetime, date
from sqlalchemy import String, ForeignKey, Table, Column, Text, func, text, UniqueConstraint, Enum, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column, WriteOnlyMapped, validates
from db import Model
from iso3166 import countries
from sqlalchemy.dialects.mysql import TIMESTAMP, SET

timestamp = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),
]

ValueType = Literal['str', 'int', 'float', 'bool', 'date', 'text']
SequenceType = Literal["Isolate", "Metagenome"]

class Owner(Model):
    __tablename__ = 'owners'

    id: Mapped[int] = mapped_column(primary_key=True)
    site: Mapped[str] = mapped_column(String(50))
    user: Mapped[str] = mapped_column(String(50))
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    specimens: Mapped[list['Specimen']] = relationship('Specimen', backref='owner')
    
    UniqueConstraint(site, user)
    

class Specimen(Model):
    __tablename__ = 'specimens'

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('owners.id'))
    accession: Mapped[str] = mapped_column(String(20))
    collection_date: Mapped[date] = mapped_column(default=datetime.utcnow)
    country_sample_taken: Mapped[str] = mapped_column(String(3))
    collection_site: Mapped[str] = mapped_column(String(50))
    specimen_type: Mapped[str] = mapped_column(String(50))
    qr_code: Mapped[text] = mapped_column(Text)
    bar_code: Mapped[text] = mapped_column(Text)
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    owner: WriteOnlyMapped[Owner] = relationship('Owner', backref='specimens')
    samples: Mapped[list['Sample']] = relationship('Sample', backref='specimen')
    
    UniqueConstraint(accession, collection_date)
    
    @validates('country_sample_taken')
    def validate_country_sample_taken(self, key, country_sample_taken):
        if country_sample_taken not in countries:
            raise ValueError(f'Invalid country code: {country_sample_taken}')
        return country_sample_taken
    

class Run(Model):
    __tablename__ = 'runs'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20))
    run_date: Mapped[date] = mapped_column(default=datetime.utcnow)
    site: Mapped[str] = mapped_column(String(20))
    sequencing_method: Mapped[str] = mapped_column(String(20))
    machine: Mapped[str] = mapped_column(String(20))
    user: Mapped[str] = mapped_column(String(5))
    number_samples: Mapped[int] = mapped_column(default=0)
    flowcell: Mapped[str] = mapped_column(String(20))
    passed_qc: Mapped[bool] = mapped_column(default=False)
    comment: Mapped[text] = mapped_column(Text)
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    samples: Mapped[list['Sample']] = relationship('Sample', backref='run')


class Sample(Model):
    __tablename__ = 'samples'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    specimen_id: Mapped[int] = mapped_column(ForeignKey('specimens.id'))
    run_id: Mapped[int] = mapped_column(ForeignKey('runs.id'))
    guid: Mapped[str] = mapped_column(String(50), unique=True)
    sequence_type: Mapped[SequenceType] = mapped_column(Enum(
        *get_args(SequenceType),
        name='sequence_type',
        create_constraint=True,
        validate_strings=True
    ), nullable=True)
    nucleic_acid_type: Mapped[set[str]] = mapped_column(SET("DNA", "RNA", "cDNA"), nullable=True)
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    run: WriteOnlyMapped['Run'] = relationship('Run', backref='samples')
    specimen: WriteOnlyMapped['Specimen'] = relationship('Specimen', backref='samples')
    details: Mapped[list['SampleDetail']] = relationship('SampleDetail', backref='sample')
    spikes: Mapped[list['Spike']] = relationship('Spike', backref='sample')
    analyses: Mapped[list['Analysis']] = relationship('Analysis', backref='sample')
    

class SampleDetail(Model):
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
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    sample: WriteOnlyMapped['Sample'] = relationship('Sample', backref='details')
    sample_detail_type: WriteOnlyMapped['SampleDetailType'] = relationship('SampleDetailType', backref='details')
    
    

class SampleDetailType(Model):
    __tablename__ = 'sample_detail_types'
    
    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[text] = mapped_column(Text, nullable=True)
    value_type: Mapped[ValueType] = mapped_column(Enum(
        *get_args(ValueType),
        name='value_type',
        create_constraint=True,
        validate_strings=True
    ))
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    details: Mapped[list['SampleDetail']] = relationship('SampleDetail', backref='sample_detail_type')
    
    
class Spike(Model):
    __tablename__ = 'spikes'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey('samples.id'))
    name: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[str] = mapped_column(String(20))
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    sample: WriteOnlyMapped['Sample'] = relationship('Sample', backref='spikes')
    
    
class Analysis(Model):
    __tablename__ = 'analyses'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[int] = mapped_column(ForeignKey('samples.id'))
    assay_system: Mapped[str] = mapped_column(String(20))
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    sample: WriteOnlyMapped['Sample'] = relationship('Sample', backref='analyses')
    speciations: Mapped[list['Speciation']] = relationship('Speciation', backref='analysis')
    others: Mapped[list['Other']] = relationship('Other', backref='analysis')
    drug_resistances: Mapped[list['DrugResistance']] = relationship('DrugResistance', backref='analysis')
    
    
class Speciation(Model):
    __tablename__ = 'speciations'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey('analyses.id'))
    species_number: Mapped[int] = mapped_column()
    species: Mapped[str] = mapped_column(String(100))
    sub_species: Mapped[str] = mapped_column(String(100))
    analysis_date: Mapped[date] = mapped_column(default=datetime.utcnow)
    data: Mapped[Optional[dict|list]] = mapped_column(type_=JSON, nullable=True)
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    analysis: WriteOnlyMapped['Analysis'] = relationship('Analysis', backref='speciations')
    
    UniqueConstraint(analysis_id, species_number)
    
    
class Other(Model):
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
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    analysis: WriteOnlyMapped['Analysis'] = relationship('Analysis', backref='others')
    other_type: WriteOnlyMapped['OtherType'] = relationship('OtherType', backref='others')
    

class OtherType(Model):
    __tablename__ = 'other_types'
    
    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[text] = mapped_column(Text, nullable=True)
    value_type: Mapped[ValueType] = mapped_column(Enum(
        *get_args(ValueType),
        name='value_type',
        create_constraint=True,
        validate_strings=True
    ))
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False 
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    others: Mapped[list['Other']] = relationship('Other', backref='other_type')


class DrugResistance(Model):
    __tablename__ = 'drug_resistances'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey('analyses.id'))
    antibiotic: Mapped[str] = mapped_column(String(20))
    drug_resistance_result_type_code: Mapped[str] = mapped_column(ForeignKey('drug_resistance_result_types.code'))
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    analysis: WriteOnlyMapped['Analysis'] = relationship('Analysis', backref='drug_resistances')
    drug_resistance_result_type: WriteOnlyMapped['DrugResistanceResultType'] = relationship('DrugResistanceResultType', backref='drug_resistances')
    
    UniqueConstraint(analysis_id, antibiotic)
    

class DrugResistanceResultType(Model):
    __tablename__ = 'drug_resistance_result_types'
    
    code: Mapped[str] = mapped_column(String(1), primary_key=True)
    description: Mapped[text] = mapped_column(Text, nullable=True)
    
    created_by: Mapped[str] = mapped_column(
        String(50), 
        server_default=text("(USER())"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        String(50),
        server_default=text("(USER())"),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(fsp=3),
        server_default=text("CURRENT_TIMESTAMP(3)"),
        nullable=False
    )
    
    drug_resistances: Mapped[list['DrugResistance']] = relationship('DrugResistance', backref='drug_resistance_result_type')