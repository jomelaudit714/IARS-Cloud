from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path
import mimetypes
import re
from typing import Any, Iterable

DEFAULT_BUCKET = "iars-document-library"
DEFAULT_TABLE = "document_library"
DEFAULT_FOLDERS_TABLE = "document_library_folders"
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}
COLLECTION_TEMPLATES = "Report Templates"
COLLECTION_POLICIES = "Policies & Memoranda"


class DocumentLibraryError(RuntimeError):
    """Base exception for document-library operations."""


class DocumentLibraryNotConfiguredError(DocumentLibraryError):
    """Raised when Supabase settings are missing."""


class DuplicateFolderError(DocumentLibraryError):
    """Raised when a company/group folder already exists."""

    def __init__(self, message: str, existing: dict[str, Any] | None = None):
        super().__init__(message)
        self.existing = existing or {}


class DuplicateDocumentError(DocumentLibraryError):
    """Raised when the same file is already stored in a collection."""

    def __init__(self, message: str, existing: dict[str, Any] | None = None):
        super().__init__(message)
        self.existing = existing or {}


@dataclass(frozen=True)
class DocumentLibraryConfig:
    url: str
    service_role_key: str
    bucket: str = DEFAULT_BUCKET
    table: str = DEFAULT_TABLE
    folders_table: str = DEFAULT_FOLDERS_TABLE


def _secret_value(container: Any, key: str, default: str = "") -> str:
    try:
        value = container.get(key, default)
    except Exception:
        try:
            value = container[key]
        except Exception:
            value = default
    return str(value or "").strip()


def read_document_library_config(secrets: Any) -> DocumentLibraryConfig:
    supabase_section = {}
    try:
        supabase_section = secrets.get("supabase", {})
    except Exception:
        pass

    return DocumentLibraryConfig(
        url=(
            _secret_value(supabase_section, "url")
            or _secret_value(secrets, "SUPABASE_URL")
        ),
        service_role_key=(
            _secret_value(supabase_section, "service_role_key")
            or _secret_value(secrets, "SUPABASE_SERVICE_ROLE_KEY")
        ),
        bucket=(
            _secret_value(supabase_section, "documents_bucket")
            or _secret_value(secrets, "SUPABASE_DOCUMENTS_BUCKET")
            or DEFAULT_BUCKET
        ),
        table=(
            _secret_value(supabase_section, "documents_table")
            or _secret_value(secrets, "SUPABASE_DOCUMENTS_TABLE")
            or DEFAULT_TABLE
        ),
        folders_table=(
            _secret_value(supabase_section, "documents_folders_table")
            or _secret_value(secrets, "SUPABASE_DOCUMENTS_FOLDERS_TABLE")
            or DEFAULT_FOLDERS_TABLE
        ),
    )


def document_library_is_configured(config: DocumentLibraryConfig) -> bool:
    return bool(config.url and config.service_role_key and config.bucket and config.table)


def create_document_library_client(config: DocumentLibraryConfig):
    if not document_library_is_configured(config):
        raise DocumentLibraryNotConfiguredError(
            "The document library is not configured. Add the Supabase URL and service-role key to Streamlit Secrets."
        )
    try:
        from supabase import create_client
    except Exception as exc:  # pragma: no cover
        raise DocumentLibraryNotConfiguredError(
            "The supabase Python package is not installed."
        ) from exc
    return create_client(config.url, config.service_role_key)


def _response_data(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    if data is None and isinstance(response, dict):
        data = response.get("data")
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _clean_text(value: Any, limit: int = 250) -> str:
    return " ".join(str(value or "").split()).strip()[:limit]


def sanitize_segment(value: str, fallback: str = "document") -> str:
    value = _clean_text(value, 180)
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("._-")
    return value[:140] or fallback


def normalize_collection(value: str) -> str:
    text = _clean_text(value)
    if text.casefold() == COLLECTION_POLICIES.casefold():
        return COLLECTION_POLICIES
    return COLLECTION_TEMPLATES


def normalize_folder_name(value: str) -> str:
    """Return a clean display name for a company/group folder."""
    return _clean_text(value, 120)


def list_document_folders(
    client: Any,
    config: DocumentLibraryConfig,
    *,
    collection: str = COLLECTION_POLICIES,
    active_only: bool = True,
    limit: int = 500,
) -> list[dict[str, Any]]:
    """List company/group folders used by a document collection."""
    query = (
        client.table(config.folders_table)
        .select("*")
        .eq("collection", normalize_collection(collection))
        .order("folder_name")
        .limit(limit)
    )
    if active_only:
        query = query.eq("status", "Active")
    return _response_data(query.execute())


def find_folder_by_name(
    client: Any,
    config: DocumentLibraryConfig,
    *,
    collection: str,
    folder_name: str,
) -> dict[str, Any] | None:
    """Find an existing folder using a case-insensitive exact name."""
    clean_name = normalize_folder_name(folder_name)
    if not clean_name:
        return None
    response = (
        client.table(config.folders_table)
        .select("*")
        .eq("collection", normalize_collection(collection))
        .ilike("folder_name", clean_name)
        .limit(1)
        .execute()
    )
    rows = _response_data(response)
    return rows[0] if rows else None


def create_document_folder(
    client: Any,
    config: DocumentLibraryConfig,
    *,
    folder_name: str,
    description: str = "",
    created_by: str = "",
    collection: str = COLLECTION_POLICIES,
) -> dict[str, Any]:
    """Create a company/group folder for policies and memoranda."""
    clean_name = normalize_folder_name(folder_name)
    if not clean_name:
        raise DocumentLibraryError("Folder name is required.")

    existing = find_folder_by_name(
        client,
        config,
        collection=collection,
        folder_name=clean_name,
    )
    if existing:
        raise DuplicateFolderError(
            f'A folder named "{existing.get("folder_name", clean_name)}" already exists.',
            existing,
        )

    metadata = {
        "collection": normalize_collection(collection),
        "folder_name": clean_name,
        "description": _clean_text(description, 1000),
        "created_by": _clean_text(created_by, 150),
        "status": "Active",
    }
    try:
        response = client.table(config.folders_table).insert(metadata).execute()
        rows = _response_data(response)
        return rows[0] if rows else metadata
    except Exception as exc:
        message = str(exc)
        if "duplicate" in message.casefold() or "unique" in message.casefold():
            raise DuplicateFolderError(
                f'A folder named "{clean_name}" already exists.'
            ) from exc
        raise DocumentLibraryError(f"Unable to create the company folder: {exc}") from exc


def validate_filename(filename: str) -> tuple[str, str, str]:
    safe_name = Path(str(filename or "")).name
    extension = Path(safe_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise DocumentLibraryError(f"Unsupported file type. Allowed extensions: {allowed}")
    mime_type = mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
    return safe_name, extension, mime_type


def make_storage_path(
    collection: str,
    category: str,
    original_filename: str,
    now: datetime | None = None,
    folder_name: str = "",
) -> str:
    now = now or datetime.now(timezone.utc)
    collection_slug = "report-templates" if normalize_collection(collection) == COLLECTION_TEMPLATES else "policies-memoranda"
    category_slug = sanitize_segment(category, "general")
    filename = sanitize_segment(Path(original_filename).name, "document")
    timestamp = now.strftime("%Y%m%dT%H%M%S%fZ")
    if normalize_collection(collection) == COLLECTION_POLICIES:
        folder_slug = sanitize_segment(folder_name, "unfiled")
        return f"{collection_slug}/{folder_slug}/{now.year}/{category_slug}/{timestamp}_{filename}"
    return f"{collection_slug}/{now.year}/{category_slug}/{timestamp}_{filename}"


def document_hash(file_bytes: bytes) -> str:
    return sha256(file_bytes).hexdigest()


def find_duplicate(
    client: Any,
    config: DocumentLibraryConfig,
    *,
    collection: str,
    digest: str,
) -> dict[str, Any] | None:
    response = (
        client.table(config.table)
        .select("*")
        .eq("collection", normalize_collection(collection))
        .eq("sha256", digest)
        .limit(1)
        .execute()
    )
    rows = _response_data(response)
    return rows[0] if rows else None


def upload_document(
    client: Any,
    config: DocumentLibraryConfig,
    *,
    collection: str,
    file_bytes: bytes,
    original_filename: str,
    title: str,
    category: str,
    description: str,
    version_label: str,
    effective_date: date | None,
    uploaded_by: str,
    subject_category: str = "",
    folder_id: str = "",
    folder_name: str = "",
    prevent_duplicate: bool = True,
) -> dict[str, Any]:
    if not file_bytes:
        raise DocumentLibraryError("The selected file is empty.")

    safe_name, extension, mime_type = validate_filename(original_filename)
    digest = document_hash(file_bytes)
    collection_value = normalize_collection(collection)

    if prevent_duplicate:
        existing = find_duplicate(
            client,
            config,
            collection=collection_value,
            digest=digest,
        )
        if existing:
            raise DuplicateDocumentError(
                f"This exact file is already stored as {existing.get('original_filename', 'an existing document')}.",
                existing,
            )

    title_value = _clean_text(title, 220) or Path(safe_name).stem
    category_value = _clean_text(category, 100) or "General"
    subject_category_value = _clean_text(subject_category, 120)
    if collection_value == COLLECTION_POLICIES and not subject_category_value:
        subject_category_value = "Other"
    folder_id_value = _clean_text(folder_id, 80)
    folder_name_value = normalize_folder_name(folder_name)
    if collection_value == COLLECTION_POLICIES and not folder_id_value:
        raise DocumentLibraryError(
            "Select a company/group folder before uploading a policy or memorandum."
        )

    storage_path = make_storage_path(
        collection=collection_value,
        category=category_value,
        original_filename=safe_name,
        folder_name=folder_name_value,
    )

    bucket = client.storage.from_(config.bucket)
    try:
        bucket.upload(
            path=storage_path,
            file=file_bytes,
            file_options={
                "content-type": mime_type,
                "cache-control": "3600",
                "upsert": "false",
            },
        )
    except Exception as exc:
        raise DocumentLibraryError(f"Unable to upload the document to Supabase Storage: {exc}") from exc

    metadata = {
        "collection": collection_value,
        "title": title_value,
        "category": category_value,
        "subject_category": subject_category_value or None,
        "description": _clean_text(description, 2000),
        "version_label": _clean_text(version_label, 60),
        "effective_date": effective_date.isoformat() if isinstance(effective_date, date) else None,
        "original_filename": safe_name,
        "storage_bucket": config.bucket,
        "storage_path": storage_path,
        "mime_type": mime_type,
        "file_extension": extension.lstrip("."),
        "uploaded_by": _clean_text(uploaded_by, 150),
        "file_size": len(file_bytes),
        "sha256": digest,
        "status": "Active",
    }
    if collection_value == COLLECTION_POLICIES:
        metadata["folder_id"] = folder_id_value

    try:
        response = client.table(config.table).insert(metadata).execute()
        rows = _response_data(response)
        return rows[0] if rows else metadata
    except Exception as exc:
        try:
            bucket.remove([storage_path])
        except Exception:
            pass
        raise DocumentLibraryError(f"The file uploaded, but its library record could not be saved: {exc}") from exc


def list_documents(
    client: Any,
    config: DocumentLibraryConfig,
    *,
    collection: str | None = None,
    limit: int = 2000,
) -> list[dict[str, Any]]:
    query = (
        client.table(config.table)
        .select("*")
        .order("uploaded_at", desc=True)
        .limit(limit)
    )
    if collection:
        query = query.eq("collection", normalize_collection(collection))
    return _response_data(query.execute())


def filter_documents(
    records: Iterable[dict[str, Any]],
    *,
    search: str = "",
    category: str = "All",
    extension: str = "All",
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict[str, Any]]:
    search_value = _clean_text(search, 300).casefold()
    category_value = _clean_text(category).casefold()
    extension_value = _clean_text(extension).lstrip(".").casefold()
    filtered: list[dict[str, Any]] = []

    for record in records:
        haystack = " ".join(
            str(record.get(key, "") or "")
            for key in (
                "title",
                "folder_name",
                "category",
                "subject_category",
                "description",
                "version_label",
                "original_filename",
                "uploaded_by",
            )
        ).casefold()
        if search_value and search_value not in haystack:
            continue

        record_category = _clean_text(record.get("category", "")).casefold()
        if category_value not in {"", "all"} and record_category != category_value:
            continue

        record_extension = _clean_text(record.get("file_extension", "")).casefold()
        if extension_value not in {"", "all"} and record_extension != extension_value:
            continue

        uploaded_text = str(record.get("uploaded_at", "") or "")
        uploaded_date = None
        if uploaded_text:
            try:
                uploaded_date = datetime.fromisoformat(uploaded_text.replace("Z", "+00:00")).date()
            except ValueError:
                pass
        if start_date and uploaded_date and uploaded_date < start_date:
            continue
        if end_date and uploaded_date and uploaded_date > end_date:
            continue
        filtered.append(record)

    return filtered


def download_document(
    client: Any,
    config: DocumentLibraryConfig,
    storage_path: str,
) -> bytes:
    try:
        data = client.storage.from_(config.bucket).download(storage_path)
    except Exception as exc:
        raise DocumentLibraryError(f"Unable to download the stored document: {exc}") from exc
    if isinstance(data, bytes):
        return data
    if hasattr(data, "read"):
        return data.read()
    try:
        return bytes(data)
    except Exception as exc:
        raise DocumentLibraryError("Supabase returned an unsupported download response.") from exc


def delete_document(
    client: Any,
    config: DocumentLibraryConfig,
    record: dict[str, Any],
) -> None:
    record_id = record.get("id")
    storage_path = _clean_text(record.get("storage_path", ""), 500)
    if not record_id or not storage_path:
        raise DocumentLibraryError("The selected document record is incomplete.")

    try:
        client.storage.from_(config.bucket).remove([storage_path])
    except Exception as exc:
        raise DocumentLibraryError(f"Unable to remove the document from Storage: {exc}") from exc

    try:
        client.table(config.table).delete().eq("id", record_id).execute()
    except Exception as exc:
        raise DocumentLibraryError(
            "The file was removed from Storage, but its metadata row could not be deleted. "
            f"Remove record {record_id} manually. Details: {exc}"
        ) from exc


def human_file_size(size_bytes: Any) -> str:
    try:
        size = float(size_bytes)
    except (TypeError, ValueError):
        return ""
    units = ["B", "KB", "MB", "GB"]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return ""
