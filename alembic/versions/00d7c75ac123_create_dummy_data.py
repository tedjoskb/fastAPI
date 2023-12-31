"""Add Dummy Data to Users and Todos Tables

Revision ID: 00d7c75ac123
Revises:
Create Date: 2023-08-22 22:23:21.058444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00d7c75ac123'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Tambahkan perintah untuk menambahkan dummy data ke tabel users
    op.bulk_insert(
        sa.table('users'),
        [
            {"email": "user1@example.com", "username": "user1", "first_name": "User", "last_name": "One", "hashed_password": "hashed_password", "is_active": True, "role": "user"},
            # Tambahkan data dummy lainnya
        ]
    )

    # Tambahkan perintah untuk menambahkan dummy data ke tabel todos
    op.bulk_insert(
        sa.table('todos'),
        [
            {"title": "Task 1", "description": "Description 1", "priority": 1, "complete": False, "owner_id": 1},
            # Tambahkan data dummy lainnya
        ]
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Hapus data dummy yang sudah ditambahkan
    op.execute("DELETE FROM users WHERE email = 'user1@example.com'")
    op.execute("DELETE FROM todos WHERE title = 'Task 1'")
    # ### end Alembic commands ###
