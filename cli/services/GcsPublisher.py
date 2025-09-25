"""Service for publishing files to Google Cloud Storage."""
import logging
import mimetypes
from pathlib import Path
from typing import Optional

from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError

logger = logging.getLogger(__name__)


class GcsPublisher:
    """Service for uploading files to Google Cloud Storage."""
    
    def __init__(self, default_bucket: str, gcp_project: str):
        """Initialize GCS publisher.
        
        Args:
            default_bucket: Default GCS bucket name
            gcp_project: GCP project ID
        """
        self.default_bucket = default_bucket
        self.gcp_project = gcp_project
        self._client = None
        self._credentials_available = None
        
    def _get_client(self) -> Optional[storage.Client]:
        """Get GCS client, handling credential errors gracefully."""
        if self._client is None and self._credentials_available is None:
            try:
                self._client = storage.Client(project=self.gcp_project)
                # Test credentials by attempting to list buckets
                list(self._client.list_buckets(max_results=1))
                self._credentials_available = True
                logger.info("GCS client initialized successfully")
            except DefaultCredentialsError:
                logger.warning("No GCS credentials available, will perform dry-run uploads")
                self._credentials_available = False
            except Exception as e:
                logger.warning(f"GCS client initialization failed: {e}, will perform dry-run uploads")
                self._credentials_available = False
                
        return self._client if self._credentials_available else None
    
    def upload(self, src_path: str, dst_blob: str, bucket_name: Optional[str] = None) -> str:
        """Upload a file to GCS.
        
        Args:
            src_path: Local file path to upload
            dst_blob: Destination blob name in GCS
            bucket_name: GCS bucket name (uses default if None)
            
        Returns:
            GCS URL (gs://bucket/blob)
        """
        bucket_name = bucket_name or self.default_bucket
        gs_url = f"gs://{bucket_name}/{dst_blob}"
        
        client = self._get_client()
        if not client:
            # Dry-run mode
            logger.info(f"DRY-RUN: Would upload {src_path} to {gs_url}")
            return gs_url
        
        try:
            src_file = Path(src_path)
            if not src_file.exists():
                raise FileNotFoundError(f"Source file not found: {src_path}")
            
            # Get bucket
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(dst_blob)
            
            # Determine content type
            content_type = self._get_content_type(src_file)
            
            # Upload file
            with open(src_file, 'rb') as f:
                blob.upload_from_file(f, content_type=content_type)
            
            logger.info(f"Uploaded {src_path} to {gs_url}")
            return gs_url
            
        except Exception as e:
            logger.error(f"Failed to upload {src_path} to GCS: {e}")
            raise
    
    def update_latest(self, src_blob: str, latest_path: str, bucket_name: Optional[str] = None) -> str:
        """Copy a blob to the fixed latest path.
        
        Args:
            src_blob: Source blob name to copy from
            latest_path: Fixed latest path destination
            bucket_name: GCS bucket name (uses default if None)
            
        Returns:
            GCS URL of the latest path
        """
        bucket_name = bucket_name or self.default_bucket
        latest_url = f"gs://{bucket_name}/{latest_path}"
        
        client = self._get_client()
        if not client:
            # Dry-run mode
            logger.info(f"DRY-RUN: Would copy {src_blob} to {latest_path}")
            return latest_url
        
        try:
            bucket = client.bucket(bucket_name)
            src_blob_obj = bucket.blob(src_blob)
            
            # Copy to latest path
            bucket.copy_blob(src_blob_obj, bucket, latest_path)
            
            logger.info(f"Updated latest path: {latest_url}")
            return latest_url
            
        except Exception as e:
            logger.error(f"Failed to update latest path: {e}")
            raise
    
    def upload_and_set_latest(self, src_path: str, dst_blob: str, latest_path: str, bucket_name: Optional[str] = None) -> tuple[str, str]:
        """Upload a file and also set it as the latest version.
        
        Args:
            src_path: Local file path to upload
            dst_blob: Destination blob name in GCS
            latest_path: Fixed latest path destination
            bucket_name: GCS bucket name (uses default if None)
            
        Returns:
            Tuple of (timestamped_url, latest_url)
        """
        # Upload to timestamped location
        timestamped_url = self.upload(src_path, dst_blob, bucket_name)
        
        # Update latest path
        latest_url = self.update_latest(dst_blob, latest_path, bucket_name)
        
        return timestamped_url, latest_url
    
    def _get_content_type(self, file_path: Path) -> str:
        """Determine content type based on file extension."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.html':
            return 'text/html'
        elif suffix == '.csv':
            return 'text/csv'
        else:
            # Use mimetypes for other files
            content_type, _ = mimetypes.guess_type(str(file_path))
            return content_type or 'application/octet-stream'
