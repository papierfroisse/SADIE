"""Tests de performance du collecteur de trades."""

import asyncio
import pytest
from datetime import datetime, timedelta

from sadie.core.collectors.trade_collector import TradeCollector
from sadie.core.models.events import Exchange, Symbol, Timeframe 