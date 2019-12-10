"""empty message

Revision ID: 2931bfcd881b
Revises: cd408fe6007a
Create Date: 2019-11-29 19:58:21.747778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2931bfcd881b'
down_revision = 'cd408fe6007a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres', sa.String(length=80), nullable=True))
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('venue', sa.Column('website', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'website')
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'seeking_description')
    op.drop_column('venue', 'genres')
    # ### end Alembic commands ###