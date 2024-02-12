"""start

Revision ID: 3fa077bb79a8
Revises: 
Create Date: 2024-01-26 11:01:14.003384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3fa077bb79a8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('drug_resistance_result_types',
    sa.Column('code', sa.String(length=1), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_drug_resistance_result_types'))
    )
    op.create_table('other_types',
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('value_type', sa.Enum('str', 'int', 'float', 'bool', 'date', 'text', name='value_type', create_constraint=True), nullable=False),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_other_types'))
    )
    op.create_table('owners',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('site', sa.String(length=50), nullable=False),
    sa.Column('user', sa.String(length=50), nullable=False),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_owners')),
    sa.UniqueConstraint('site', 'user', name=op.f('uq_owners_site'))
    )
    op.create_table('runs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('run_date', sa.Date(), nullable=False),
    sa.Column('site', sa.String(length=20), nullable=False),
    sa.Column('sequencing_method', sa.String(length=20), nullable=False),
    sa.Column('machine', sa.String(length=20), nullable=False),
    sa.Column('user', sa.String(length=5), nullable=True),
    sa.Column('number_samples', sa.Integer(), nullable=True),
    sa.Column('flowcell', sa.String(length=20), nullable=True),
    sa.Column('passed_qc', sa.Boolean(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_runs')),
    sa.UniqueConstraint('code', name=op.f('uq_runs_code'))
    )
    op.create_table('sample_detail_types',
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('value_type', sa.Enum('str', 'int', 'float', 'bool', 'date', 'text', name='value_type', create_constraint=True), nullable=False),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_sample_detail_types'))
    )
    op.create_table('specimens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('accession', sa.String(length=20), nullable=False),
    sa.Column('collection_date', sa.Date(), nullable=False),
    sa.Column('country_sample_taken_code', sa.String(length=3), nullable=False),
    sa.Column('specimen_type', sa.String(length=50), nullable=True),
    sa.Column('specimen_qr_code', sa.Text(), nullable=True),
    sa.Column('bar_code', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['owners.id'], name=op.f('fk_specimens_owner_id_owners')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_specimens')),
    sa.UniqueConstraint('accession', 'collection_date', name=op.f('uq_specimens_accession'))
    )
    op.create_table('samples',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('specimen_id', sa.Integer(), nullable=False),
    sa.Column('run_id', sa.Integer(), nullable=False),
    sa.Column('guid', sa.String(length=64), nullable=False),
    sa.Column('sample_category', sa.Enum('culture', 'unclutured', name='sample_category', create_constraint=True), nullable=True),
    sa.Column('nucleic_acid_type', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['run_id'], ['runs.id'], name=op.f('fk_samples_run_id_runs')),
    sa.ForeignKeyConstraint(['specimen_id'], ['specimens.id'], name=op.f('fk_samples_specimen_id_specimens')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_samples')),
    sa.UniqueConstraint('guid', name=op.f('uq_samples_guid'))
    )
    op.create_table('analyses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sample_id', sa.Integer(), nullable=False),
    sa.Column('assay_system', sa.String(length=20), nullable=False),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['sample_id'], ['samples.id'], name=op.f('fk_analyses_sample_id_samples')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_analyses'))
    )
    op.create_table('sample_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sample_id', sa.Integer(), nullable=False),
    sa.Column('sample_detail_type_code', sa.String(length=50), nullable=False),
    sa.Column('value_str', sa.String(length=50), nullable=True),
    sa.Column('value_int', sa.Integer(), nullable=True),
    sa.Column('value_float', sa.Float(), nullable=True),
    sa.Column('value_bool', sa.Boolean(), nullable=True),
    sa.Column('value_date', sa.Date(), nullable=True),
    sa.Column('value_text', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['sample_detail_type_code'], ['sample_detail_types.code'], name=op.f('fk_sample_details_sample_detail_type_code_sample_detail_types')),
    sa.ForeignKeyConstraint(['sample_id'], ['samples.id'], name=op.f('fk_sample_details_sample_id_samples')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sample_details'))
    )
    op.create_table('spikes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sample_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('quantity', sa.String(length=20), nullable=False),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['sample_id'], ['samples.id'], name=op.f('fk_spikes_sample_id_samples')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_spikes'))
    )
    op.create_table('drug_resistances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('analysis_id', sa.Integer(), nullable=False),
    sa.Column('antibiotic', sa.String(length=20), nullable=False),
    sa.Column('drug_resistance_result_type_code', sa.String(length=1), nullable=False),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], name=op.f('fk_drug_resistances_analysis_id_analyses')),
    sa.ForeignKeyConstraint(['drug_resistance_result_type_code'], ['drug_resistance_result_types.code'], name=op.f('fk_drug_resistances_drug_resistance_result_type_code_drug_resistance_result_types')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_drug_resistances')),
    sa.UniqueConstraint('analysis_id', 'antibiotic', name=op.f('uq_drug_resistances_analysis_id'))
    )
    op.create_table('others',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('analysis_id', sa.Integer(), nullable=False),
    sa.Column('other_type_code', sa.String(length=50), nullable=False),
    sa.Column('value_str', sa.String(length=50), nullable=True),
    sa.Column('value_int', sa.Integer(), nullable=True),
    sa.Column('value_float', sa.Float(), nullable=True),
    sa.Column('value_bool', sa.Boolean(), nullable=True),
    sa.Column('value_date', sa.Date(), nullable=True),
    sa.Column('value_text', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], name=op.f('fk_others_analysis_id_analyses')),
    sa.ForeignKeyConstraint(['other_type_code'], ['other_types.code'], name=op.f('fk_others_other_type_code_other_types')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_others'))
    )
    op.create_table('speciations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('analysis_id', sa.Integer(), nullable=False),
    sa.Column('species_number', sa.Integer(), nullable=False),
    sa.Column('species', sa.String(length=100), nullable=False),
    sa.Column('sub_species', sa.String(length=100), nullable=False),
    sa.Column('analysis_date', sa.Date(), nullable=False),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('created_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.Column('updated_by', sa.String(length=50), server_default=sa.text('CURRENT_USER'), nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(precision=3), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], name=op.f('fk_speciations_analysis_id_analyses')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_speciations')),
    sa.UniqueConstraint('analysis_id', 'species_number', name=op.f('uq_speciations_analysis_id'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('speciations')
    op.drop_table('others')
    op.drop_table('drug_resistances')
    op.drop_table('spikes')
    op.drop_table('sample_details')
    op.drop_table('analyses')
    op.drop_table('samples')
    op.drop_table('specimens')
    op.drop_table('sample_detail_types')
    op.drop_table('runs')
    op.drop_table('owners')
    op.drop_table('other_types')
    op.drop_table('drug_resistance_result_types')
    # ### end Alembic commands ###
