from __future__ import annotations

import enum


class PlannerStatus(enum.StrEnum):
    PENDING = "pending"
    PLANNING = "planning"
    OPTIMIZING = "optimizing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


class PlanningStrategyType(enum.StrEnum):
    PROGRESSIVE_LEARNING = "progressive_learning"
    DEPENDENCY_ORDERED = "dependency_ordered"
    DIFFICULTY_PROGRESSION = "difficulty_progression"
    TOPIC_CLUSTERING = "topic_clustering"


class SectionType(enum.StrEnum):
    PREFACE = "preface"
    INTRODUCTION = "introduction"
    CHAPTER = "chapter"
    EXERCISE = "exercise"
    SUMMARY = "summary"
    GLOSSARY = "glossary"
    APPENDIX = "appendix"
    REFERENCES = "references"
    INDEX = "index"


class ValidationSeverity(enum.StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
