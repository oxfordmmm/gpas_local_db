"""refactor storage

Revision ID: 5ce093d2a6a5
Revises: e045b65392ef
Create Date: 2024-03-13 11:21:31.934900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5ce093d2a6a5"
down_revision: Union[str, None] = "e045b65392ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("storages", schema=None) as batch_op:
        batch_op.add_column(sa.Column("freezer", sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column("shelf", sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column("rack", sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column("tray", sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column("box", sa.String(length=50), nullable=False))
        batch_op.add_column(
            sa.Column("box_location", sa.String(length=50), nullable=False)
        )
        batch_op.add_column(sa.Column("notes", sa.Text(), nullable=True))
        batch_op.drop_column("freezer_sub_compartment")
        batch_op.drop_column("freezer_compartment")
        batch_op.drop_column("freezer_id")

    with op.batch_alter_table("storages_version", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "freezer", sa.String(length=50), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column("shelf", sa.String(length=50), autoincrement=False, nullable=True)
        )
        batch_op.add_column(
            sa.Column("rack", sa.String(length=50), autoincrement=False, nullable=True)
        )
        batch_op.add_column(
            sa.Column("tray", sa.String(length=50), autoincrement=False, nullable=True)
        )
        batch_op.add_column(
            sa.Column("box", sa.String(length=50), autoincrement=False, nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "box_location", sa.String(length=50), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column("notes", sa.Text(), autoincrement=False, nullable=True)
        )
        batch_op.drop_column("freezer_sub_compartment")
        batch_op.drop_column("freezer_compartment")
        batch_op.drop_column("freezer_id")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("storages_version", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "freezer_id", sa.VARCHAR(length=20), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                "freezer_compartment",
                sa.VARCHAR(length=20),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "freezer_sub_compartment",
                sa.VARCHAR(length=20),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.drop_column("notes")
        batch_op.drop_column("box_location")
        batch_op.drop_column("box")
        batch_op.drop_column("tray")
        batch_op.drop_column("rack")
        batch_op.drop_column("shelf")
        batch_op.drop_column("freezer")

    with op.batch_alter_table("storages", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "freezer_id", sa.VARCHAR(length=20), autoincrement=False, nullable=False
            )
        )
        batch_op.add_column(
            sa.Column(
                "freezer_compartment",
                sa.VARCHAR(length=20),
                autoincrement=False,
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "freezer_sub_compartment",
                sa.VARCHAR(length=20),
                autoincrement=False,
                nullable=False,
            )
        )
        batch_op.drop_column("notes")
        batch_op.drop_column("box_location")
        batch_op.drop_column("box")
        batch_op.drop_column("tray")
        batch_op.drop_column("rack")
        batch_op.drop_column("shelf")
        batch_op.drop_column("freezer")

    # ### end Alembic commands ###
