"""Qualitative Measurements

Revision ID: 279068d14c7c
Revises: d8229809e79e
Create Date: 2017-01-20 14:55:04.984799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '279068d14c7c'
down_revision = 'd8229809e79e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('visit',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('person_id', sa.Integer, sa.ForeignKey('person.id')),
            sa.Column('visit_code', sa.String, nullable=False),
            sa.Column('visit_date', sa.String, nullable=False),
            sa.Column('comment', sa.Text),
            sa.UniqueConstraint('person_id', 'visit_code', 'visit_date')
    )

    op.create_table('measurement_entity',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String, nullable=False, unique=True)
    )

    op.create_table('measurement_value',
            sa.Column('visit_id', sa.Integer, sa.ForeignKey('visit.id')),
            sa.Column('measurement_entity_id', sa.Integer, sa.ForeignKey('measurement_entity.id')),
            sa.Column('value', sa.String, nullable=False),
            sa.UniqueConstraint('visit_id', 'measurement_entity_id', 'value')
    )


def downgrade():
    for table in ['visit', 'measurement_experiment', 'measurement_entity', 'measurement_value']:
        op.drop_table(table)
