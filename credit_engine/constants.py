import pydantic as pydantic


class TrimmedString(pydantic.ConstrainedStr):
    strip_whitespace = True
    min_length = 1


class NonEmptyList(pydantic.ConstrainedList):
    min_items = 1


# data sources
CROSSREF = "crossref"
DATACITE = "datacite"
OSTI = "osti"
KBASE = "kbase"

# file formats and extensions
JSON = "json"
XML = "xml"
UNIXREF = "unixref"
UNIXSD = "unixsd"
EXT = {
    JSON: f".{JSON}",
    XML: f".{XML}",
    UNIXREF: f".{UNIXREF}.{XML}",
    UNIXSD: f".{UNIXSD}.{XML}",
}

# misc
DEFAULT_EMAIL = "credit_engine@kbase.us"

SAMPLE_DATA = "sample_data"
OUTPUT_FORMAT = "output format"
DATA_SOURCE = "data source"

DATA = "data"
FILES = "files"

KBASE_DOI = "10.1038/nbt.4163"
