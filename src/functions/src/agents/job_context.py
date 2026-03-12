"""
JobContext and JobContextRegistry — in-memory bridge between the SK team
leader (which passes only job_id strings via function calling) and the
ExamOps pipeline (which exchanges live python-docx Document objects).

Usage::

    from src.agents.job_context import registry

    # Coordinator creates a context before invoking the team leader
    registry.create(job_id, file_url, user_id)

    # Plugins read/write to the context using only the job_id
    ctx = registry.get(job_id)
    ctx.original_doc = ...

    # Coordinator reads final state after team leader finishes
    ctx = registry.get(job_id)
    registry.remove(job_id)
"""

import threading
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JobContext:
    """
    Holds all live Python objects for one formatting job.

    Fields are populated progressively by the plugin methods as the
    SK team leader calls them in pipeline order.
    """

    job_id: str
    file_url: str
    user_id: str

    # Populated by FileHandlerPlugin.download_document
    original_doc: Optional[object] = field(default=None)

    # Populated by FileHandlerPlugin.get_template
    template_rules: Optional[dict] = field(default=None)

    # Populated by FormattingPlugin.format_and_validate
    formatted_doc: Optional[object] = field(default=None)
    validation_result: Optional[dict] = field(default=None)

    # Populated by DiffPlugin.generate_diff
    diff_result: Optional[dict] = field(default=None)

    # Populated by FileHandlerPlugin.save_outputs
    output_urls: Optional[dict] = field(default=None)

    # Populated by FileHandlerPlugin.create_sharing_link
    onedrive_link: Optional[str] = field(default=None)

    # Set by any plugin on unrecoverable error
    last_error: Optional[str] = field(default=None)


class JobContextRegistry:
    """Thread-safe in-memory store keyed by job_id."""

    def __init__(self) -> None:
        self._store: dict = {}
        self._lock = threading.Lock()

    def create(self, job_id: str, file_url: str, user_id: str) -> JobContext:
        """
        Create and register a new JobContext.

        Args:
            job_id:   Unique job identifier.
            file_url: Azure Blob SAS URL of the uploaded .docx.
            user_id:  Teams / AAD user ID.

        Returns:
            The newly created JobContext.
        """
        ctx = JobContext(job_id=job_id, file_url=file_url, user_id=user_id)
        with self._lock:
            self._store[job_id] = ctx
        return ctx

    def get(self, job_id: str) -> Optional[JobContext]:
        """Return the JobContext for job_id, or None if not found."""
        with self._lock:
            return self._store.get(job_id)

    def remove(self, job_id: str) -> None:
        """Remove the JobContext for job_id (no-op if not present)."""
        with self._lock:
            self._store.pop(job_id, None)


# Module-level singleton — import this in plugins and CoordinatorAgent
registry = JobContextRegistry()
