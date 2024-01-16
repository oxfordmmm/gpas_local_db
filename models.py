from datetime import datetime, date
from sqlalchemy import String, ForeignKey, Table, Column, Text, func, text, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column, WriteOnlyMapped, validates
from db import Model
from typing import Annotated, Optional
from iso3166 import countries
from sqlalchemy.dialects.mysql import TIMESTAMP

timestamp = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),
]


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
    sample_type: Mapped[str] = mapped_column(String(50))
    
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
    
    UniqueConstraint(accession, collection_date)
    
    @validates('country_sample_taken')
    def validate_country_sample_taken(self, key, country_sample_taken):
        if country_sample_taken not in countries:
            raise ValueError(f'Invalid country code: {country_sample_taken}')
        return country_sample_taken