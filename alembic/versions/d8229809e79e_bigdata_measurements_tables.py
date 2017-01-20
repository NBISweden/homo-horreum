"""BigData measurements tables

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
depends_on = None


def upgrade():
    for type in ['expression', 'proteomics', 'metabolomics']:
        op.create_table('{}_entity'.format(type),
                sa.Column('id', sa.Integer, primary_key=True),
                sa.Column('name', sa.String, nullable=False)
        )
    
        op.create_table('{}_experiment'.format(type),
                sa.Column('id', sa.Integer, primary_key=1),
                sa.Column('person_id', sa.Integer, sa.ForeignKey('person.id')),
                sa.Column('note', sa.Text(), nullable=True)
        )

        op.create_table('{}_value'.format(type),
                sa.Column('{}_experiment_id'.format(type), sa.Integer, sa.ForeignKey('{}_experiment.id'.format(type))),
                sa.Column('{}_entity_id'.format(type), sa.Integer, sa.ForeignKey('{}_transcript.id'.format(type))),
                sa.Column('value', sa.Float(), nullable=False)
        )


def downgrade():
    for type in ['expression', 'proteomics', 'metabolomics']:
        op.drop_table('{}_entity'.format(type))
        op.drop_table('{}_experiment'.format(type))
        op.drop_table('{}_value'.format(type))
