"""add language to posts

Revision ID: 86af51fa9348
Revises: c8ac010988cb
Create Date: 2019-10-11 21:54:21.443005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86af51fa9348'
down_revision = 'c8ac010988cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('language', sa.String(length=5), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'language')
    # ### end Alembic commands ###
