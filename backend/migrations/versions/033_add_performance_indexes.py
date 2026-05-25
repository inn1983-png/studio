"""add performance indexes

Revision ID: 033
Revises: 032
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '033'
down_revision = '032'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index('idx_character_project_name', 'movie_characters', ['project_id', 'name'])
    op.create_index('idx_prop_project_name', 'movie_props', ['project_id', 'name'])
    op.create_index('idx_shot_scene_order', 'movie_shots', ['scene_id', 'order_index'])
    op.create_index('idx_transition_script_status', 'movie_shot_transitions', ['script_id', 'status'])
    op.create_index('idx_canvas_item_doc_type', 'canvas_items', ['document_id', 'item_type'])
    op.create_index('idx_apikey_user_provider_status', 'api_keys', ['user_id', 'provider', 'status'])


def downgrade() -> None:
    op.drop_index('idx_apikey_user_provider_status', table_name='api_keys')
    op.drop_index('idx_canvas_item_doc_type', table_name='canvas_items')
    op.drop_index('idx_transition_script_status', table_name='movie_shot_transitions')
    op.drop_index('idx_shot_scene_order', table_name='movie_shots')
    op.drop_index('idx_prop_project_name', table_name='movie_props')
    op.drop_index('idx_character_project_name', table_name='movie_characters')
