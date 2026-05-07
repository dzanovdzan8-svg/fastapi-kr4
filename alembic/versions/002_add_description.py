from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'

def upgrade():
    op.add_column('products', sa.Column('description', sa.String(), nullable=False, server_default=''))
    op.execute("UPDATE products SET description = 'Standard product'")

def downgrade():
    op.drop_column('products', 'description')
