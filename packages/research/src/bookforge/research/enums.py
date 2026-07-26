from __future__ import annotations

import enum


class SourceType(enum.StrEnum):
    DOCUMENTATION = "documentation"
    GITHUB = "github"
    RFC = "rfc"
    PAPER = "paper"
    BLOG = "blog"
    BOOK = "book"
    SPECIFICATION = "specification"
    API = "api"


class ResearchStatus(enum.StrEnum):
    PENDING = "pending"
    PLANNING = "planning"
    COLLECTING = "collecting"
    NORMALIZING = "normalizing"
    DEDUPLICATING = "deduplicating"
    RANKING = "ranking"
    VALIDATING = "validating"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


class RankCriterion(enum.StrEnum):
    AUTHORITY = "authority"
    FRESHNESS = "freshness"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"


class SupportedInput(enum.StrEnum):
    TECHNICAL_TOPIC = "technical_topic"
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    TECHNOLOGY = "technology"
    SOFTWARE_LIBRARY = "software_library"
    API = "api"
    RFC = "rfc"
    ARCHITECTURE = "architecture"
