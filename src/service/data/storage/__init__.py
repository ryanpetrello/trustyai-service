"""Storage backend implementations."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.service.data.storage.storage_interface import StorageInterface

from src.service.data.storage.db.db_storage import DBStorage
from src.service.data.storage.pvc import PVCStorage


class GlobalStorageInterface:
    """Singleton holder for global storage interface."""

    _instance: StorageInterface | None = None

    @classmethod
    def get(cls, *, force_reload: bool = False) -> StorageInterface:
        """Get or create the global storage interface singleton."""
        if cls._instance is None or force_reload:
            cls._instance = get_storage_interface()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (useful for testing)."""
        cls._instance = None


def get_global_storage_interface(*, force_reload: bool = False) -> StorageInterface:
    """Get or create the global storage interface singleton."""
    return GlobalStorageInterface.get(force_reload=force_reload)


def get_storage_interface() -> StorageInterface:
    """Create a new storage interface based on environment configuration.

    Supported formats:
    - PVC: HDF5-based file storage (default)
    - MARIA / DATABASE: MariaDB via SQLAlchemy async (asyncmy)
    - POSTGRES / POSTGRESQL: PostgreSQL via SQLAlchemy async (asyncpg)
    """
    storage_format = os.environ.get("SERVICE_STORAGE_FORMAT", "PVC")

    if storage_format == "PVC":
        return PVCStorage(
            data_directory=os.environ.get("STORAGE_DATA_FOLDER", "/tmp"),  # noqa: S108
            data_file=os.environ.get("STORAGE_DATA_FILENAME", "trustyai.hdf5"),
        )

    if storage_format in ("MARIA", "DATABASE", "POSTGRES", "POSTGRESQL"):
        from src.service.data.storage.db.engine import (  # noqa: PLC0415
            create_db_engine,
        )

        engine = create_db_engine(storage_format)
        return DBStorage(engine)

    msg = f"Unsupported storage format: {storage_format}"
    raise ValueError(msg)
