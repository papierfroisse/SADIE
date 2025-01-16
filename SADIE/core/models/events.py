"""Modèles de base de données pour les événements."""

from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Event(Base):
    """Modèle de base pour tous les événements."""
    
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    topic = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    data = Column(JSON, nullable=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "event",
        "polymorphic_on": topic
    }

class MarketEvent(Event):
    """Modèle pour les événements de marché."""
    
    __tablename__ = "market_events"
    
    id = Column(Integer, ForeignKey('events.id'), primary_key=True)
    symbol = Column(String, nullable=False, index=True)
    price = Column(BigInteger, nullable=False)  # Prix en centimes
    volume = Column(BigInteger, nullable=False)  # Volume en centimes
    side = Column(String, nullable=False)
    exchange = Column(String, nullable=False, index=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "market"
    } 