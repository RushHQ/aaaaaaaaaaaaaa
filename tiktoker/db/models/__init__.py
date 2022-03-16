"""database models"""

from .config import Config
from .usage_data import UsageData
from .shortener import Shortener
from .opted_out import OptedOut


__beanie_models__ = [Config, UsageData, Shortener, OptedOut]
