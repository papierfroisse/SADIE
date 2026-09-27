"""Tests d'intégration du collecteur de sentiment."""

import pytest
from datetime import datetime, timedelta

from sadie.data.sentiment import SentimentCollector, SentimentSource, SentimentAnalyzer, SentimentScore 