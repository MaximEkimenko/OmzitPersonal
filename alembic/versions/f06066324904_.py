"""empty message

Revision ID: f06066324904
Revises: c9ce9aa277d1
Create Date: 2024-06-10 14:07:20.366506

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f06066324904'
down_revision: Union[str, None] = 'c9ce9aa277d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('calendar_days', sa.Column('day_type', sa.String(), nullable=True))
    op.drop_column('calendar_days', 'day_status')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('calendar_days', sa.Column('day_status', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('calendar_days', 'day_type')
