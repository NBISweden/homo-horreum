"""metabolomics_analysis

Revision ID: 093b4c3e30c7
Revises: 332835b86836
Create Date: 2017-11-21 13:20:53.415880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '093b4c3e30c7'
down_revision = '332835b86836'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('metabolomics_analysis',
        sa.Column('id', sa.Integer, primary_key=1),
        sa.Column('metabolite_id', sa.Integer, sa.ForeignKey('metabolomics_entity.id')),
        sa.Column('technology', sa.Text(), nullable=True),
        sa.Column('tissue', sa.Text(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('date', sa.DateTime(), server_default=sa.sql.func.now())
    )
    op.create_table('test_type',
        sa.Column('id', sa.Integer, primary_key=1),
        sa.Column('test', sa.Text(), nullable=True)
    )
    op.create_table('test_value',
        sa.Column('metabolomics_analysis_id', sa.Integer, sa.ForeignKey('metabolomics_analysis.id')),
        sa.Column('test_type_id', sa.Integer, sa.ForeignKey('test_type.id')),
        sa.Column('value', sa.Float())
    )


def downgrade():
    op.drop_table('metabolomics_analysis')
    op.drop_table('test_type')
    op.drop_table('test_value')
