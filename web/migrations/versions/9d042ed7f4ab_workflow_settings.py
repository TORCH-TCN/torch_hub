"""workflow settings

Revision ID: 9d042ed7f4ab
Revises: fdf9f20902f2
Create Date: 2022-05-30 01:38:58.747755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d042ed7f4ab'
down_revision = 'fdf9f20902f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('workflow_file_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workflow_id', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(length=150), nullable=True),
    sa.Column('label', sa.String(length=150), nullable=True),
    sa.Column('name', sa.String(length=150), nullable=True),
    sa.Column('file_regex', sa.String(length=150), nullable=True),
    sa.Column('output_sub_path', sa.String(length=150), nullable=True),
    sa.ForeignKeyConstraint(['workflow_id'], ['workflow.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('workflow_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workflow_id', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(length=150), nullable=True),
    sa.Column('label', sa.String(length=150), nullable=True),
    sa.Column('name', sa.String(length=150), nullable=True),
    sa.Column('value', sa.String(length=150), nullable=True),
    sa.ForeignKeyConstraint(['workflow_id'], ['workflow.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('workflow_settings')
    op.drop_table('workflow_file_type')
    # ### end Alembic commands ###
