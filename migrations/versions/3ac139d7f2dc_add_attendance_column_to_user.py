"""add attendance column to user

Revision ID: 3ac139d7f2dc
Revises: dffbabff5fdd
Create Date: 2025-04-21 13:57:29.956984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ac139d7f2dc'
down_revision = 'dffbabff5fdd'
branch_labels = None
depends_on = None

def upgrade():
    # Add foreign key constraint with a name
    with op.batch_alter_table('performance', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_performance_user_id', 'user', ['student_id'], ['id'])

    # Add attendance column to user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('attendance', sa.Float(), nullable=True))

def downgrade():
    # Remove attendance column from user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('attendance')

    # Drop foreign key constraint by name
    with op.batch_alter_table('performance', schema=None) as batch_op:
        batch_op.drop_constraint('fk_performance_user_id', type_='foreignkey')

    # ### end Alembic commands ###
