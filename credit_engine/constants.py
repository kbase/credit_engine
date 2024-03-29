"""Constants used throughout the Credit Engine."""

from enum import Enum

import pydantic
from pydantic import EmailStr


class TrimmedString(pydantic.ConstrainedStr):
    """Non-zero length trimmed string."""

    strip_whitespace = True
    min_length = 1


class NonEmptyList(pydantic.ConstrainedList):
    """Non-zero length list."""

    min_items = 1


# file formats and extensions
JSON = "json"
XML = "xml"


class OutputFormat(Enum):
    """Valid output format strings."""

    JSON = "json"
    XML = "xml"


# file formats and extensions
EXT = {
    JSON: ".json",
    XML: ".xml",
}


# data sources
CROSSREF = "crossref"
DATACITE = "datacite"
OSTI = "osti"
OSTI_ELINK = "osti_elink"
KBASE = "kbase"
UNKNOWN = "unknown"

# misc
DEFAULT_EMAIL: EmailStr = "credit_engine@kbase.us"

SAMPLE_DATA = "sample_data"
OUTPUT_FORMAT = "output format"
DATA_SOURCE = "data source"

DATA = "data"
FILES = "files"

KBASE_DOI = "10.1038/nbt.4163"
