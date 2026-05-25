"""create movie_props table

Revision ID: 030
Revises: 029
Create Date: 2026-05-23 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '030'
down_revision = '029'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('movie_props',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='主键ID'),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False, comment='项目外键'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='道具名称'),
        sa.Column('category', sa.String(length=50), nullable=True, comment='道具分类'),
        sa.Column('description', sa.Text(), nullable=True, comment='道具描述'),
        sa.Column('visual_traits', sa.Text(), nullable=True, comment='视觉特征描述'),
        sa.Column('era_background', sa.String(length=200), nullable=True, comment='时代背景'),
        sa.Column('key_visual_traits', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='核心视觉特征列表'),
        sa.Column('generated_prompt', sa.Text(), nullable=True, comment='生成的道具图提示词'),
        sa.Column('image_url', sa.String(length=500), nullable=True, comment='道具图片URL'),
        sa.Column('reference_images', postgresql.JSON(astext_type=sa.Text()), nullable=True, comment='参考图URL列表'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.Index('idx_movie_prop_project', 'project_id'),
        comment='电影道具表'
    )

    op.execute("""
        CREATE TRIGGER update_movie_props_updated_at
            BEFORE UPDATE ON movie_props
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS update_movie_props_updated_at ON movie_props")
    op.drop_table('movie_props')
