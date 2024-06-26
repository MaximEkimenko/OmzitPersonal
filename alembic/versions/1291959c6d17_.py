"""empty message

Revision ID: 1291959c6d17
Revises: d42878f753f7
Create Date: 2024-05-02 11:35:29.838647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1291959c6d17'
down_revision: Union[str, None] = 'd42878f753f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('employee_test', sa.Column('new_field', sa.String(length=50), nullable=True))
    op.create_index(op.f('ix_employee_test_id'), 'employee_test', ['id'], unique=False)
    op.create_index(op.f('ix_timesheet_test_id'), 'timesheet_test', ['id'], unique=False)
    op.drop_column('timesheet_test', 'new_test_field')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('timesheet_test', sa.Column('new_test_field', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_timesheet_test_id'), table_name='timesheet_test')
    op.drop_index(op.f('ix_employee_test_id'), table_name='employee_test')
    op.drop_column('employee_test', 'new_field')
    # ### end Alembic commands ###
