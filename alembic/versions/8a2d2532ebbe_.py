"""empty message

Revision ID: 8a2d2532ebbe
Revises: 196f0ee9f44b
Create Date: 2024-06-06 10:43:08.148158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8a2d2532ebbe'
down_revision: Union[str, None] = '196f0ee9f44b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('employee_test', sa.Column('KVL_last_month', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('employee_test', 'KVL_last_month')
