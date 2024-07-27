"""Add Plant

Revision ID: 0533ac5f2ec2
Revises: 4764c84a42de
Create Date: 2024-07-27 09:52:53.433881

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0533ac5f2ec2"
down_revision = "4764c84a42de"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "plant",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("light_conditions", sa.String(length=64), nullable=True),
        sa.Column("watering_frequency", sa.String(length=64), nullable=True),
        sa.Column("fertilizing_frequency", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.String(length=256), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("plant")
    # ### end Alembic commands ###
