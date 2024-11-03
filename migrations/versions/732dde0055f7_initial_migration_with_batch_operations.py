"""Initial migration with batch operations

Revision ID: 732dde0055f7
Revises: 
Create Date: 2024-11-01 17:36:37.492698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '732dde0055f7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'todo_item', type_='foreignkey')
    op.drop_constraint(None, 'todo_item', type_='foreignkey')
    op.create_foreign_key('fk_todoitem_list', 'todo_item', 'todo_list', ['list_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_todoitem_parent', 'todo_item', 'todo_item', ['parent_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_todoitem_parent', 'todo_item', type_='foreignkey')
    op.drop_constraint('fk_todoitem_list', 'todo_item', type_='foreignkey')
    op.create_foreign_key(None, 'todo_item', 'todo_item', ['parent_id'], ['id'])
    op.create_foreign_key(None, 'todo_item', 'todo_list', ['list_id'], ['id'])
    # ### end Alembic commands ###
