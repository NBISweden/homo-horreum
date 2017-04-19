"""Variant tables

Revision ID: 9512e61c9f2b
Revises: 52337e31da34
Create Date: 2017-01-20 10:45:52.627849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9512e61c9f2b'
down_revision = '52337e31da34'
branch_labels = None
depends_on = '52337e31da34'


def upgrade():
    op.create_table('variant',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('chromosome', sa.String(2), nullable=False),
            sa.Column('pos', sa.Integer, nullable=False),
            sa.Column('identifier', sa.String(), nullable=False),
            sa.Column('ref', sa.String(), nullable=False),
            sa.Column('alt', sa.String(), nullable=False),
            sa.Column('qual', sa.String(), nullable=False),
            sa.Column('filter', sa.String(), nullable=False),
            sa.Column('info', sa.String(), nullable=False),
            sa.Column('format', sa.String(), nullable=False)
    )

    op.create_table('variant_extra_fields',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.Text, nullable=False)
    )

    op.create_table('variant_extra',
            sa.Column('variant_id', sa.Integer, sa.ForeignKey('variant.id')),
            sa.Column('field_id', sa.Integer, sa.ForeignKey('variant_extra_fields.id')),
            sa.Column('value', sa.Text, nullable=False)
    )

    op.create_table('person_variant',
            sa.Column('person_id', sa.Integer, sa.ForeignKey('person.id')),
            sa.Column('variant_id', sa.Integer, sa.ForeignKey('variant.id')),
            sa.Column('variant_type', sa.Text)
    )



def downgrade():
    op.drop_table('variant')
    op.drop_table('variant_extra_fields')
    op.drop_table('variant_extra')
    op.drop_table('person_variant')
