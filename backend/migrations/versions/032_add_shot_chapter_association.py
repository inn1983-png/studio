"""add shot chapter association

Revision ID: 032
Revises: 031
Create Date: 2026-05-23 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '032'
down_revision = '031'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('movie_shots', sa.Column('chapter_id', UUID(as_uuid=True), nullable=True, comment='章节外键'))
    op.create_foreign_key('fk_movie_shots_chapter_id', 'movie_shots', 'chapters', ['chapter_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_movie_shots_chapter_id', 'movie_shots', ['chapter_id'])


def downgrade():
    op.drop_index('ix_movie_shots_chapter_id', table_name='movie_shots')
    op.drop_constraint('fk_movie_shots_chapter_id', 'movie_shots', type_='foreignkey')
    op.drop_column('movie_shots', 'chapter_id')
