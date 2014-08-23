"""add ambiguous affiliation flag

Revision ID: 52b38830e4f1
Revises: None
Create Date: 2014-08-23 20:08:30.702574

"""

# revision identifiers, used by Alembic.
revision = '52b38830e4f1'
down_revision = None

from alembic import op  # NOQA
import sqlalchemy as sa  # NOQA


def upgrade():
    op.add_column(
        'publication',
        sa.Column('has_ambiguous_affiliations', sa.Boolean(), nullable=False,
                  server_default=sa.sql.expression.false())
    )


def downgrade():
    op.drop_column('publication', 'has_ambiguous_affiliations')
