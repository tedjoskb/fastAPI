"""add apartment number col

Revision ID: a1d738631713
Revises: 2c0d910f3cbf
Create Date: 2023-08-24 22:41:43.820832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1d738631713'
down_revision: Union[str, None] = '2c0d910f3cbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('address', sa.Column('apt_num', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('address','apt_num')
