"""empty message

Revision ID: 0bd6fd83b781
Revises: 7b0c727c0201
Create Date: 2024-10-23 18:30:22.821928

"""

from datetime import datetime

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "0bd6fd83b781"
down_revision = "7b0c727c0201"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("jira_tasks", schema=None) as batch_op:
        # ### Use a raw sql comment to add USING clause ###
        conn = op.get_bind()
        conn.execute(
            text("""
            ALTER TABLE jira_tasks 
            ALTER COLUMN created_at 
            TYPE TIMESTAMP WITH TIME ZONE
            USING created_at::timestamp with time zone;
        """)
        )


def downgrade():
    with op.batch_alter_table("jira_tasks", schema=None) as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            type_=sa.VARCHAR(),
            nullable=True,
        )
