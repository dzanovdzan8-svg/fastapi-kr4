from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade():
    op.create_table('products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
    )
    op.execute("INSERT INTO products (title, price, count) VALUES ('Keyboard', 1500.0, 10), ('Mouse', 800.0, 25)")

def downgrade():
    op.drop_table('products')
