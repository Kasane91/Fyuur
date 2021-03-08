"""empty message

Revision ID: bfca50196e86
Revises: 1e19977eccdb
Create Date: 2021-02-01 12:28:30.575673

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfca50196e86'
down_revision = '1e19977eccdb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('website', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'website')
    # ### end Alembic commands ###
