"""Increase length of password_hash to 256

Revision ID: 4764c84a42de
Revises: 0dff5c41ed67
Create Date: 2024-07-27 08:28:44.033145

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "4764c84a42de"
down_revision = "0dff5c41ed67"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=mysql.VARCHAR(length=128),
            type_=sa.String(length=256),
            existing_nullable=True,
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=256),
            type_=mysql.VARCHAR(length=128),
            existing_nullable=True,
        )

    # ### end Alembic commands ###
