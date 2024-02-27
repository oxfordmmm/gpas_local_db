"""Extra sample fields and countries

Revision ID: ac41a312c0cd
Revises: 8c1afc2aa455
Create Date: 2024-02-20 09:31:26.060390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ac41a312c0cd"
down_revision: Union[str, None] = "8c1afc2aa455"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "countries",
        sa.Column("code", sa.String(length=3), nullable=False),
        sa.Column("code2", sa.String(length=2), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column(
            "created_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_countries")),
    )
    op.create_table(
        "countries_version",
        sa.Column("code", sa.String(length=3), autoincrement=False, nullable=False),
        sa.Column("code2", sa.String(length=2), autoincrement=False, nullable=True),
        sa.Column("name", sa.String(length=100), autoincrement=False, nullable=True),
        sa.Column("lat", sa.Float(), autoincrement=False, nullable=True),
        sa.Column("lon", sa.Float(), autoincrement=False, nullable=True),
        sa.Column(
            "created_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "code", "transaction_id", name=op.f("pk_countries_version")
        ),
    )
    with op.batch_alter_table("countries_version", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_countries_version_end_transaction_id"),
            ["end_transaction_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_countries_version_operation_type"),
            ["operation_type"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_countries_version_transaction_id"),
            ["transaction_id"],
            unique=False,
        )

    op.create_table(
        "specimen_detail_types",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "value_type",
            postgresql.ENUM(
                "str",
                "int",
                "float",
                "bool",
                "date",
                "text",
                name="value_type",
                create_type=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_specimen_detail_types")),
    )
    op.create_table(
        "specimen_detail_types_version",
        sa.Column("code", sa.String(length=50), autoincrement=False, nullable=False),
        sa.Column("description", sa.Text(), autoincrement=False, nullable=True),
        sa.Column(
            "value_type",
            postgresql.ENUM(
                "str",
                "int",
                "float",
                "bool",
                "date",
                "text",
                name="value_type",
                create_type=False,
                create_constraint=True,
            ),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "created_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "code", "transaction_id", name=op.f("pk_specimen_detail_types_version")
        ),
    )
    with op.batch_alter_table("specimen_detail_types_version", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_specimen_detail_types_version_end_transaction_id"),
            ["end_transaction_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_specimen_detail_types_version_operation_type"),
            ["operation_type"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_specimen_detail_types_version_transaction_id"),
            ["transaction_id"],
            unique=False,
        )

    op.create_table(
        "specimen_details_version",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("specimen_id", sa.Integer(), autoincrement=False, nullable=True),
        sa.Column(
            "specimen_detail_type_code",
            sa.String(length=50),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "value_str", sa.String(length=50), autoincrement=False, nullable=True
        ),
        sa.Column("value_int", sa.Integer(), autoincrement=False, nullable=True),
        sa.Column("value_float", sa.Float(), autoincrement=False, nullable=True),
        sa.Column("value_bool", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column("value_date", sa.Date(), autoincrement=False, nullable=True),
        sa.Column("value_text", sa.Text(), autoincrement=False, nullable=True),
        sa.Column(
            "created_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "id", "transaction_id", name=op.f("pk_specimen_details_version")
        ),
    )
    with op.batch_alter_table("specimen_details_version", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_specimen_details_version_end_transaction_id"),
            ["end_transaction_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_specimen_details_version_operation_type"),
            ["operation_type"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_specimen_details_version_transaction_id"),
            ["transaction_id"],
            unique=False,
        )

    op.create_table(
        "specimen_details",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("specimen_id", sa.Integer(), nullable=False),
        sa.Column("specimen_detail_type_code", sa.String(length=50), nullable=False),
        sa.Column("value_str", sa.String(length=50), nullable=True),
        sa.Column("value_int", sa.Integer(), nullable=True),
        sa.Column("value_float", sa.Float(), nullable=True),
        sa.Column("value_bool", sa.Boolean(), nullable=True),
        sa.Column("value_date", sa.Date(), nullable=True),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column(
            "created_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_by",
            sa.String(length=50),
            server_default=sa.text("CURRENT_USER"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(precision=3),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["specimen_detail_type_code"],
            ["specimen_detail_types.code"],
            name=op.f(
                "fk_specimen_details_specimen_detail_type_code_specimen_detail_types"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["specimen_id"],
            ["specimens.id"],
            name=op.f("fk_specimen_details_specimen_id_specimens"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_specimen_details")),
    )
    with op.batch_alter_table("specimens", schema=None) as batch_op:
        batch_op.create_foreign_key(
            batch_op.f("fk_specimens_country_sample_taken_code_countries"),
            "countries",
            ["country_sample_taken_code"],
            ["code"],
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("specimens", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_specimens_country_sample_taken_code_countries"),
            type_="foreignkey",
        )

    op.drop_table("specimen_details")
    with op.batch_alter_table("specimen_details_version", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_specimen_details_version_transaction_id"))
        batch_op.drop_index(batch_op.f("ix_specimen_details_version_operation_type"))
        batch_op.drop_index(
            batch_op.f("ix_specimen_details_version_end_transaction_id")
        )

    op.drop_table("specimen_details_version")
    with op.batch_alter_table("specimen_detail_types_version", schema=None) as batch_op:
        batch_op.drop_index(
            batch_op.f("ix_specimen_detail_types_version_transaction_id")
        )
        batch_op.drop_index(
            batch_op.f("ix_specimen_detail_types_version_operation_type")
        )
        batch_op.drop_index(
            batch_op.f("ix_specimen_detail_types_version_end_transaction_id")
        )

    op.drop_table("specimen_detail_types_version")
    op.drop_table("specimen_detail_types")
    with op.batch_alter_table("countries_version", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_countries_version_transaction_id"))
        batch_op.drop_index(batch_op.f("ix_countries_version_operation_type"))
        batch_op.drop_index(batch_op.f("ix_countries_version_end_transaction_id"))

    op.drop_table("countries_version")
    op.drop_table("countries")
    # ### end Alembic commands ###
