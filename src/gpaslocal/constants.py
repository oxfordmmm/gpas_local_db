from typing import Annotated, Literal, Any, TypeVar, Optional
from math import isnan
import pandas as pd  # type: ignore
from datetime import datetime
from dateutil.parser import parse
from sqlalchemy import String, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP
from pydantic import BeforeValidator


db_timestamp = Annotated[
    datetime,
    mapped_column(TIMESTAMP(precision=3), server_default=text("NOW()"), nullable=False),
]

db_user = Annotated[
    str,
    mapped_column(String(50), server_default=text("CURRENT_USER"), nullable=False),
]

ValueType = Literal["str", "int", "float", "bool", "date", "text"]
SampleCategory = Literal["culture", "unclutured"]
NucleicAcidType = Literal["DNA", "RNA", "cDNA"]
SequencingMethod = Literal["illumina", "ont", "pacbio"]


def coerce_nan_to_none(x: Any) -> Any:
    return None if isinstance(x, float) and isnan(x) else x


def coerce_nat_to_none(x: Any) -> Any:
    if isinstance(x, str) and not x.strip():
        return None
    elif isinstance(x, str):
        return parse(x).date()
    return None if pd.isnull(x) else x


def coerce_to_str(x: Any) -> str:
    return str(x).strip()


T = TypeVar("T")

NoneOrNan = Annotated[Optional[T], BeforeValidator(coerce_nan_to_none)]
ExcelDate = Annotated[T, BeforeValidator(coerce_nat_to_none)]
ExcelStr = Annotated[str, BeforeValidator(coerce_to_str)]
OptionalExcelDate = Annotated[Optional[T], BeforeValidator(coerce_nat_to_none)]
