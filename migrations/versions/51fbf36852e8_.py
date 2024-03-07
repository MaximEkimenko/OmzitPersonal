"""empty message

Revision ID: 51fbf36852e8
Revises: 
Create Date: 2024-03-04 16:40:50.425786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51fbf36852e8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('alchemy_test1',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('employment_date', sa.String(), nullable=False),
    sa.Column('fired_date', sa.DateTime(), nullable=True),
    sa.Column('fio', sa.String(), nullable=False),
    sa.Column('job_title', sa.String(length=100), nullable=True),
    sa.Column('rank_title', sa.SmallInteger(), nullable=True),
    sa.Column('tabel_number', sa.String(length=20), nullable=True),
    sa.Column('tariff_rate', sa.Integer(), nullable=True),
    sa.Column('division', sa.String(length=30), nullable=True),
    sa.Column('schedule', sa.SmallInteger(), nullable=True),
    sa.Column('shift_hours', sa.SmallInteger(), nullable=True),
    sa.Column('skud_access', sa.SmallInteger(), nullable=True),
    sa.Column('day_start', sa.SmallInteger(), nullable=True),
    sa.Column('boss', sa.String(length=100), nullable=True),
    sa.Column('KTR_category', sa.String(length=50), nullable=True),
    sa.Column('KTR', sa.Float(), nullable=True),
    sa.Column('has_NAX', sa.Boolean(), nullable=True),
    sa.Column('KNAX', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    info={'use_autogenerate': True}
    )
    op.create_table('alchemy_test2',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('employee_id', sa.BigInteger(), nullable=False),
    sa.Column('day_status', sa.String(length=10), nullable=True),
    sa.Column('skud_day_start_1', sa.DateTime(), nullable=True),
    sa.Column('skud_day_end_1', sa.DateTime(), nullable=True),
    sa.Column('skud_day_duration', sa.SmallInteger(), nullable=True),
    sa.Column('skud_night_duration', sa.SmallInteger(), nullable=True),
    sa.Column('is_day_alter', sa.Boolean(), nullable=True),
    sa.Column('altered_day_duration', sa.SmallInteger(), nullable=True),
    sa.Column('altered_night_duration', sa.SmallInteger(), nullable=True),
    sa.Column('is_night_alter', sa.Boolean(), nullable=True),
    sa.Column('skud_error', sa.Boolean(), nullable=True),
    sa.Column('skud_error_query', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['alchemy_test1.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    info={'use_autogenerate': True}
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('alchemy_test2')
    op.drop_table('alchemy_test1')
    # ### end Alembic commands ###
