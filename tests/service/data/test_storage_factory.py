"""Tests for storage backend factory."""

import os
from unittest.mock import patch

import pytest

from src.service.data.storage import get_storage_interface
from src.service.data.storage.db.db_storage import DBStorage
from src.service.data.storage.pvc import PVCStorage


class TestGetStorageInterface:
    """Tests for get_storage_interface factory function."""

    def test_pvc_is_default(self) -> None:
        """PVC storage is returned when no format is specified."""
        env = os.environ.copy()
        env.pop("SERVICE_STORAGE_FORMAT", None)
        with patch.dict(os.environ, env, clear=True):
            storage = get_storage_interface()
            assert isinstance(storage, PVCStorage)

    def test_unsupported_format_raises(self) -> None:
        """Unsupported format raises ValueError."""
        with (
            patch.dict(os.environ, {"SERVICE_STORAGE_FORMAT": "REDIS"}, clear=False),
            pytest.raises(ValueError, match="Unsupported storage format"),
        ):
            get_storage_interface()

    @patch("src.service.data.storage.db.engine.create_db_engine")
    def test_maria_format_creates_dbstorage(self, _mock_engine: object) -> None:
        """MARIA format returns DBStorage."""
        env = {
            "SERVICE_STORAGE_FORMAT": "MARIA",
            "DATABASE_USERNAME": "user",
            "DATABASE_PASSWORD": "pass",  # pragma: allowlist secret
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "3306",
            "DATABASE_DATABASE": "testdb",
        }
        with patch.dict(os.environ, env, clear=False):
            storage = get_storage_interface()
            assert isinstance(storage, DBStorage)

    @patch("src.service.data.storage.db.engine.create_db_engine")
    def test_database_format_creates_dbstorage(self, _mock_engine: object) -> None:
        """DATABASE format is accepted as alias for MARIA."""
        env = {
            "SERVICE_STORAGE_FORMAT": "DATABASE",
            "DATABASE_USERNAME": "user",
            "DATABASE_PASSWORD": "pass",  # pragma: allowlist secret
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "3306",
            "DATABASE_DATABASE": "testdb",
        }
        with patch.dict(os.environ, env, clear=False):
            storage = get_storage_interface()
            assert isinstance(storage, DBStorage)

    @patch("src.service.data.storage.db.engine.create_db_engine")
    def test_postgres_format_creates_dbstorage(self, _mock_engine: object) -> None:
        """POSTGRES format returns DBStorage."""
        env = {
            "SERVICE_STORAGE_FORMAT": "POSTGRES",
            "DATABASE_USERNAME": "user",
            "DATABASE_PASSWORD": "pass",  # pragma: allowlist secret
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_DATABASE": "testdb",
        }
        with patch.dict(os.environ, env, clear=False):
            storage = get_storage_interface()
            assert isinstance(storage, DBStorage)
