from enum import Enum


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Audience(str, Enum):
    DEVELOPERS = "developers"
    DATA_SCIENTISTS = "data_scientists"
    DEVOPS = "devops"
    ARCHITECTS = "architects"
    STUDENTS = "students"
    HOBBYISTS = "hobbyists"
    PROFESSIONALS = "professionals"
    MANAGERS = "managers"


class Language(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    ARABIC = "ar"
    HINDI = "hi"
    ITALIAN = "it"
    DUTCH = "nl"
    POLISH = "pl"
    TURKISH = "tr"
    VIETNAMESE = "vi"
    THAI = "th"
    SWEDISH = "sv"
    GREEK = "el"
    HEBREW = "he"


class BookStatus(str, Enum):
    DRAFT = "draft"
    PLANNING = "planning"
    RESEARCHING = "researching"
    WRITING = "writing"
    REVIEWING = "reviewing"
    EDITING = "editing"
    FORMATTING = "formatting"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class GenerationStage(str, Enum):
    CREATED = "created"
    OUTLINING = "outlining"
    OUTLINED = "outlined"
    RESEARCHING = "researching"
    RESEARCHED = "researched"
    WRITING = "writing"
    WRITTEN = "written"
    REVIEWING = "reviewing"
    REVIEWED = "reviewed"
    FORMATTING = "formatting"
    FORMATTED = "formatted"
    EXPORTING = "exporting"
    EXPORTED = "exported"
    FAILED = "failed"


class ExportFormat(str, Enum):
    PDF = "pdf"
    EPUB = "epub"
    MOBI = "mobi"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "markdown"
    LATEX = "latex"
    ASCIIDOC = "asciidoc"
    PLAIN_TEXT = "plain_text"


class DiagramType(str, Enum):
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    CLASS = "class_diagram"
    ERD = "erd"
    ARCHITECTURE = "architecture"
    COMPONENT = "component"
    DEPLOYMENT = "deployment"
    STATE = "state"
    TIMING = "timing"
    GANTT = "gantt"
    MINDMAP = "mindmap"
    CUSTOM = "custom"


class ReferenceType(str, Enum):
    BOOK = "book"
    ARTICLE = "article"
    CONFERENCE = "conference"
    THESIS = "thesis"
    TECHNICAL_REPORT = "technical_report"
    WEBSITE = "website"
    DOCUMENTATION = "documentation"
    STANDARD = "standard"
    PATENT = "patent"
    SOFTWARE = "software"
    VIDEO = "video"
    PODCAST = "podcast"
    BLOG = "blog"
    OTHER = "other"


class AssetType(str, Enum):
    IMAGE = "image"
    DIAGRAM = "diagram"
    CODE_SNIPPET = "code_snippet"
    TABLE = "table"
    CHART = "chart"
    SCREENSHOT = "screenshot"
    LOGO = "logo"
    ICON = "icon"
    ATTACHMENT = "attachment"
    OTHER = "other"


class CodeLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    GO = "go"
    JAVA = "java"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    CPP = "cpp"
    C = "c"
    CSHARP = "csharp"
    RUBY = "ruby"
    PHP = "php"
    SHELL = "shell"
    SQL = "sql"
    YAML = "yaml"
    JSON = "json"
    XML = "xml"
    HTML = "html"
    CSS = "css"
    SCALA = "scala"
    ELIXIR = "elixir"
    HASKELL = "haskell"
    LUA = "lua"
    R = "r"
    MATLAB = "matlab"
    BASH = "bash"
    POWERSHELL = "powershell"
    DOCKERFILE = "dockerfile"
    DIFF = "diff"
    TEXT = "text"
    OTHER = "other"


class BloomLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"
