"""create phone number for user col

Revision ID: 9e3531a1e4ac
Revises: 00d7c75ac123
Create Date: 2023-08-23 17:33:46.050357

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e3531a1e4ac'
down_revision: Union[str, None] = '00d7c75ac123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number',sa.String(),nullable=True))


def downgrade() -> None:
    op.drop_column('users','phone_number')
