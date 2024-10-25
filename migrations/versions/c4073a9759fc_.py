"""empty message

Revision ID: c4073a9759fc
Revises: 28a719de7ec9
Create Date: 2024-08-28 09:39:29.684677

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4073a9759fc"
down_revision = "28a719de7ec9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("team", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column("department", sa.String(), nullable=True)
        )
        batch_op.add_column(sa.Column("hrc_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("job_title", sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("job_title")
        batch_op.drop_column("hrc_id")
        batch_op.drop_column("department")
        batch_op.drop_column("team")

    # ### end Alembic commands ###
