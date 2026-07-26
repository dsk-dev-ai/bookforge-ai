from __future__ import annotations

from bookforge.config.enums import StorageBackend
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseSettings):
    """File and object storage configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKFORGE_STORAGE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    backend: StorageBackend = Field(default=StorageBackend.LOCAL, description="Storage backend type")
    local_path: str = Field(default="./data/storage", description="Local storage base path")
    s3_bucket: str | None = Field(default=None, description="S3 bucket name")
    s3_region: str | None = Field(default=None, description="S3 region")
    s3_access_key: str | None = Field(default=None, description="S3 access key ID")
    s3_secret_key: str | None = Field(default=None, description="S3 secret access key")
    s3_endpoint_url: str | None = Field(default=None, description="S3-compatible endpoint URL")
    gcs_bucket: str | None = Field(default=None, description="GCS bucket name")
    gcs_credentials_path: str | None = Field(default=None, description="GCS service account JSON path")
    azure_connection_string: str | None = Field(default=None, description="Azure Blob Storage connection string")
    azure_container: str | None = Field(default=None, description="Azure Blob Storage container name")
    max_file_size_mb: int = Field(default=500, ge=1, le=10000, description="Max upload file size in MB")
    temp_dir: str = Field(default="/tmp/bookforge", description="Temporary file directory")
