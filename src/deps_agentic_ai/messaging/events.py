from dataclasses import dataclass

__all__ = ["DocumentDeleted", "DocumentTypeDeleted"]


@dataclass
class DocumentDeleted:
    document_id: str


@dataclass
class DocumentTypeDeleted:
    document_type: str
    tenant: str
