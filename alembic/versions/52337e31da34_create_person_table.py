"""Create person table

Revision ID: 52337e31da34
Revises: 
Create Date: 2017-01-19 16:13:20.650248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52337e31da34'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'person',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('identifier', sa.String, nullable=False),
        sa.Column('group', sa.String, nullable=False),
        sa.Column('sex', sa.Enum('M','F'), nullable=False)
    )


def downgrade():
    pass
