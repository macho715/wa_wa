"""
MACHO-GPT v3.4-mini Async WhatsApp Multi-Group Scraper
Samsung C&T Logistics · HVDC Project

멀티 그룹 병렬 스크래핑 모듈
"""

from .group_config import GroupConfig, ScraperSettings, AIIntegrationSettings
from .async_scraper import AsyncGroupScraper
from .multi_group_manager import MultiGroupManager

__all__ = [
    'GroupConfig',
    'ScraperSettings',
    'AIIntegrationSettings',
    'AsyncGroupScraper',
    'MultiGroupManager',
]

__version__ = '1.0.0'

