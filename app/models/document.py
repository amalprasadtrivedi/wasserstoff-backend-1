import os
import uuid
from typing import List, Optional
from datetime import datetime


class Document:
    def __init__(self, name: str, path: str, content: str, doc_id: Optional[str] = None):
        self.id = doc_id or str(uuid.uuid4())
        self.name = name
        self.path = path
        self.content = content
        self.upload_time = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "content": self.content,
            "upload_time": self.upload_time
        }

    @staticmethod
    def from_dict(data: dict):
        return Document(
            doc_id=data.get("id"),
            name=data.get("name"),
            path=data.get("path"),
            content=data.get("content")
        )


class DocumentStore:
    def __init__(self):
        self.documents: List[Document] = []

    def add_document(self, doc: Document):
        self.documents.append(doc)

    def get_all(self) -> List[Document]:
        return self.documents

    def get_by_id(self, doc_id: str) -> Optional[Document]:
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        return None

    def to_dict_list(self):
        return [doc.to_dict() for doc in self.documents]

    def load_from_dict_list(self, data: List[dict]):
        self.documents = [Document.from_dict(d) for d in data]

    def delete_by_id(self, doc_id: str) -> bool:
        doc = self.get_by_id(doc_id)
        if doc:
            try:
                os.remove(doc.path)
            except FileNotFoundError:
                pass  # File already gone
            self.documents.remove(doc)
            return True
        return False
