"""create total profit by block table

Revision ID: a5a44a7c854d
Revises: 5c5375de15fd
Create Date: 2022-12-12 02:46:57.125040

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5a44a7c854d'
down_revision = '5c5375de15fd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "total_profit_by_block",
        sa.Column("block_number", sa.Numeric, primary_key=True),
        sa.Column("transaction_hash", sa.String(66), nullable=False),
        sa.Column("token_debt", sa.String(66), nullable=True),
        sa.Column("amount_debt", sa.Numeric, nullable=False),
        sa.Column("token_received", sa.String(66), nullable=False),
        sa.Column("amount_received", sa.Numeric, nullable=False),
    )


def downgrade():
    op.drop_table("total_profit_by_block")