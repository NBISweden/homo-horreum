"""Metabolomics measurements tables

Revision ID: d8229809e79e
Revises: 9512e61c9f2b
Create Date: 2017-01-20 14:25:43.809645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8229809e79e'
down_revision = '9512e61c9f2b'
branch_labels = None
depends_on = '52337e31da34'


def upgrade():
    op.create_table('metabolomics_experiment',
            sa.Column('id', sa.Integer, primary_key=1),
            sa.Column('person_id', sa.Integer, sa.ForeignKey('person.id')),
            sa.Column('note', sa.Text(), nullable=True)
        )

    op.create_table('metabolomics_entity',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String, nullable=False)
        )

    op.create_table('metabolomics_value',
            sa.Column('metabolomics_experiment_id', sa.Integer, sa.ForeignKey('metabolomics_experiment.id')),
            sa.Column('metabolomics_entity_id', sa.Integer, sa.ForeignKey('metabolomics_entity.id')),
            sa.Column('value', sa.Float(), nullable=False)
        )

    op.create_table('metabolomics_entity_info',
            sa.Column('metabolomics_entity_id', sa.Integer, sa.ForeignKey('metabolomics_entity.id')),
            sa.Column('name', sa.String, nullable=False),
            sa.Column('value', sa.String, nullable=False),
        )


def downgrade():
    op.drop_table('metabolomics_entity')
    op.drop_table('metabolomics_experiment')
    op.drop_table('metabolomics_value')
    op.drop_table('metabolomics_entity_info')
