"""Constants used throughout the Credit Engine."""

from enum import Enum

from pydantic import EmailStr

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
