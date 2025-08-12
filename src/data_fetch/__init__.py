"""
SSB Data Fetch Package

A modular package for fetching and processing emissions data from Statistics Norway (SSB).
"""

from .ssb_api import SSBApiClient
from .data_processors import SSBDataProcessor
from .file_manager import DataFileManager

__all__ = ["SSBApiClient", "SSBDataProcessor", "DataFileManager"]
