"""tirggers for updated_by, updated_at

Revision ID: 97e10106ecf4
Revises: 717f1cee6d7f
Create Date: 2024-01-17 14:30:20.626536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '97e10106ecf4'
down_revision: Union[str, None] = '717f1cee6d7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tables: Sequence[str] = [
    'drug_resistance_result_types',
    'other_types',
    'owners', 
    'runs', 
    'sample_detail_types', 
    'specimens', 
    'samples', 
    'analyses', 
    'sample_details', 
    'spikes', 
    'drug_resistances', 
    'others', 
    'speciations'
]


def upgrade() -> None:
    for table in tables:
        op.execute(
        f"""
        CREATE TRIGGER before_update_trigger_{table}
        BEFORE UPDATE ON {table}
        FOR EACH ROW
        BEGIN
            SET NEW.updated_by = USER();
            SET NEW.updated_at = CURRENT_TIMESTAMP(3);
        END;
        """
        )


def downgrade() -> None:
    for table in tables:
        op.execute(
        f"""
        DROP TRIGGER before_update_trigger_{table};
        """
        )
