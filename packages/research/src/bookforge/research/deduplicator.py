from __future__ import annotations

from collections.abc import Sequence
from hashlib import sha256

from bookforge.research.models import ResearchDocument, ResearchSource


class ResearchDeduplicator:
    """Detects and removes duplicate sources and documents.

    Uses content fingerprinting via SHA-256 hashes. Two items with
    the same content hash are considered duplicates.
    """

    def deduplicate_sources(self, sources: Sequence[ResearchSource]) -> list[ResearchSource]:
        seen: set[str] = set()
        result: list[ResearchSource] = []
        for s in sources:
            fingerprint = self._fingerprint_source(s)
            if fingerprint not in seen:
                seen.add(fingerprint)
                result.append(s)
        return result

    def deduplicate_documents(self, documents: Sequence[ResearchDocument]) -> list[ResearchDocument]:
        seen: set[str] = set()
        result: list[ResearchDocument] = []
        for d in documents:
            fingerprint = self._fingerprint_document(d)
            if fingerprint not in seen:
                seen.add(fingerprint)
                result.append(d)
        return result

    def find_duplicates(
        self,
        sources: Sequence[ResearchSource],
    ) -> list[tuple[ResearchSource, ResearchSource]]:
        groups: dict[str, list[ResearchSource]] = {}
        for s in sources:
            fp = self._fingerprint_source(s)
            groups.setdefault(fp, []).append(s)

        duplicates: list[tuple[ResearchSource, ResearchSource]] = []
        for group in groups.values():
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    duplicates.append((group[i], group[j]))
        return duplicates

    def _fingerprint_source(self, source: ResearchSource) -> str:
        raw = f"{source.title.lower().strip()}:{source.content[:500].lower().strip()}"
        return sha256(raw.encode()).hexdigest()

    def _fingerprint_document(self, doc: ResearchDocument) -> str:
        raw = f"{doc.title.lower().strip()}:{doc.content[:500].lower().strip()}"
        return sha256(raw.encode()).hexdigest()
