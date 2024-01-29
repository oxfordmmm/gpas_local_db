from typing import Annotated, Literal
from datetime import datetime
from sqlalchemy import String, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP

db_timestamp = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(precision=3),
        server_default=text("NOW()"),
        nullable=False
    ),
]

db_user = Annotated[
    str,
    mapped_column(
        String(50), 
        server_default=text("CURRENT_USER"), 
        nullable=False
    ),
]

ValueType = Literal['str', 'int', 'float', 'bool', 'date', 'text']
SequenceCategory = Literal["culture", "unclutured"]
NucleicAcidType = Literal["DNA", "RNA", "cDNA"]
SequencingMethod = Literal["illumina", "ont", "pacbio"]