"""Migration initiale pour la configuration TimescaleDB."""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic
revision = '001_initial_timescale_setup'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Crée les tables et configure TimescaleDB."""
    # Activation de l'extension TimescaleDB
    op.execute('CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE')
    
    # Création de la table events
    op.create_table(
        'events',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('topic', sa.String(255), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data', sa.JSON, nullable=False),
        sa.Column('metadata', sa.JSON, nullable=True)
    )
    
    # Création de la table market_events
    op.create_table(
        'market_events',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('topic', sa.String(255), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data', sa.JSON, nullable=False),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('price', sa.Integer, nullable=False),
        sa.Column('volume', sa.Integer, nullable=False),
        sa.Column('side', sa.String(10), nullable=False),
        sa.Column('exchange', sa.String(50), nullable=False)
    )
    
    # Création de la table sentiment_events
    op.create_table(
        'sentiment_events',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('topic', sa.String(255), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data', sa.JSON, nullable=False),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('score', sa.Integer, nullable=False),
        sa.Column('entity', sa.String(100), nullable=False)
    )
    
    # Création des index
    op.create_index('ix_events_topic', 'events', ['topic'])
    op.create_index('ix_events_timestamp', 'events', ['timestamp'])
    
    op.create_index('ix_market_events_topic', 'market_events', ['topic'])
    op.create_index('ix_market_events_timestamp', 'market_events', ['timestamp'])
    op.create_index('ix_market_events_symbol', 'market_events', ['symbol'])
    op.create_index('ix_market_events_exchange', 'market_events', ['exchange'])
    
    op.create_index('ix_sentiment_events_topic', 'sentiment_events', ['topic'])
    op.create_index('ix_sentiment_events_timestamp', 'sentiment_events', ['timestamp'])
    op.create_index('ix_sentiment_events_source', 'sentiment_events', ['source'])
    op.create_index('ix_sentiment_events_entity', 'sentiment_events', ['entity'])
    
    # Configuration des hypertables TimescaleDB
    op.execute("""
        SELECT create_hypertable('events', 'timestamp',
            chunk_time_interval => INTERVAL '1 day');
    """)
    
    op.execute("""
        SELECT create_hypertable('market_events', 'timestamp',
            chunk_time_interval => INTERVAL '1 hour');
    """)
    
    op.execute("""
        SELECT create_hypertable('sentiment_events', 'timestamp',
            chunk_time_interval => INTERVAL '1 hour');
    """)
    
    # Configuration de la rétention des données (30 jours par défaut)
    op.execute("""
        SELECT add_retention_policy('events',
            INTERVAL '30 days');
    """)
    
    op.execute("""
        SELECT add_retention_policy('market_events',
            INTERVAL '30 days');
    """)
    
    op.execute("""
        SELECT add_retention_policy('sentiment_events',
            INTERVAL '30 days');
    """)
    
    # Configuration de la compression automatique
    op.execute("""
        ALTER TABLE events SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'topic'
        );
    """)
    
    op.execute("""
        ALTER TABLE market_events SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'symbol,exchange'
        );
    """)
    
    op.execute("""
        ALTER TABLE sentiment_events SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'source,entity'
        );
    """)
    
    # Ajout des politiques de compression (après 1 jour)
    op.execute("""
        SELECT add_compression_policy('events',
            INTERVAL '1 day');
    """)
    
    op.execute("""
        SELECT add_compression_policy('market_events',
            INTERVAL '1 day');
    """)
    
    op.execute("""
        SELECT add_compression_policy('sentiment_events',
            INTERVAL '1 day');
    """)

def downgrade() -> None:
    """Supprime les tables et la configuration TimescaleDB."""
    # Suppression des tables (les hypertables seront supprimées automatiquement)
    op.drop_table('sentiment_events')
    op.drop_table('market_events')
    op.drop_table('events')
    
    # Désactivation de l'extension TimescaleDB
    op.execute('DROP EXTENSION IF EXISTS timescaledb CASCADE') 