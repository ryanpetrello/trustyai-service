"""Tests for storage interface initialization with environment variables."""

import os
from unittest.mock import patch

import pytest

from src.service.data.storage import get_storage_interface
from src.service.data.storage.db.db_storage import DBStorage
from src.service.data.storage.pvc import PVCStorage


class TestStorageInterfaceEnvVars:
    """Test storage interface creation with different environment variable conventions."""

    def test_pvc_storage_creation(self) -> None:
        """Test PVC storage interface creation."""
        with patch.dict(
            os.environ,
            {
                "SERVICE_STORAGE_FORMAT": "PVC",
                "STORAGE_DATA_FOLDER": "/tmp/test",  # noqa: S108
                "STORAGE_DATA_FILENAME": "test.hdf5",
            },
            clear=False,
        ):
            storage = get_storage_interface()
            assert isinstance(storage, PVCStorage)
            assert storage.data_directory == "/tmp/test"  # noqa: S108
            assert storage.data_file == "test.hdf5"

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

    def test_unsupported_storage_format(self) -> None:
        """Test that unsupported storage format raises ValueError."""
        with (
            patch.dict(
                os.environ, {"SERVICE_STORAGE_FORMAT": "UNSUPPORTED"}, clear=False
            ),
            pytest.raises(ValueError, match="Unsupported storage format"),
        ):
            get_storage_interface()

    def test_db_missing_parameters_raises(self) -> None:
        """Missing required DB env vars raises ValueError."""
        with (
            patch.dict(
                os.environ,
                {"SERVICE_STORAGE_FORMAT": "MARIA"},
                clear=True,
            ),
            pytest.raises(ValueError, match="Database storage requires"),
        ):
            get_storage_interface()
