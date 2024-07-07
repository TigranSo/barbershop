"""Initial migration.

Revision ID: b872365f964a
Revises: 
Create Date: 2024-05-18 12:43:36.895793

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b872365f964a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('barbershop',
    sa.Column('id_barbershop', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('image', sa.String(length=200), nullable=True),
    sa.Column('worktime_start', sa.Time(), nullable=False),
    sa.Column('worktime_end', sa.Time(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=False),
    sa.Column('namecity', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id_barbershop')
    )
    op.create_table('service',
    sa.Column('id_service', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id_service')
    )
    op.create_table('user',
    sa.Column('id_user', sa.Integer(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('city', sa.String(length=20), nullable=True),
    sa.Column('gender', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id_user'),
    sa.UniqueConstraint('email')
    )
    op.create_table('barber',
    sa.Column('id_barber', sa.Integer(), nullable=False),
    sa.Column('id_barbershop', sa.Integer(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['id_barbershop'], ['barbershop.id_barbershop'], ),
    sa.PrimaryKeyConstraint('id_barber')
    )
    op.create_table('barbershop_service',
    sa.Column('id_barbershop_service', sa.Integer(), nullable=False),
    sa.Column('id_barbershop', sa.Integer(), nullable=False),
    sa.Column('id_service', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['id_barbershop'], ['barbershop.id_barbershop'], ),
    sa.ForeignKeyConstraint(['id_service'], ['service.id_service'], ),
    sa.PrimaryKeyConstraint('id_barbershop_service')
    )
    op.create_table('appointment',
    sa.Column('id_appointment', sa.Integer(), nullable=False),
    sa.Column('id_barber', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['id_barber'], ['barber.id_barber'], ),
    sa.ForeignKeyConstraint(['id_user'], ['user.id_user'], ),
    sa.PrimaryKeyConstraint('id_appointment')
    )
    op.create_table('appointment_service',
    sa.Column('id_appointment_service', sa.Integer(), nullable=False),
    sa.Column('id_barbershop_service', sa.Integer(), nullable=False),
    sa.Column('id_appointment', sa.Integer(), nullable=False),
    sa.Column('appointment_detail', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['id_appointment'], ['appointment.id_appointment'], ),
    sa.ForeignKeyConstraint(['id_barbershop_service'], ['barbershop_service.id_barbershop_service'], ),
    sa.PrimaryKeyConstraint('id_appointment_service')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('appointment_service')
    op.drop_table('appointment')
    op.drop_table('barbershop_service')
    op.drop_table('barber')
    op.drop_table('user')
    op.drop_table('service')
    op.drop_table('barbershop')
    # ### end Alembic commands ###
