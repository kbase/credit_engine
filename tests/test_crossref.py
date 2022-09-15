from urllib.parse import quote

import pytest

from credit_engine.parsers.crossref import DEFAULT_EMAIL, get_endpoint

SAMPLE_DOI = "10.46936/jejc.proj%2013?48+08-6/60005298"
QUOTED_DOI = quote(SAMPLE_DOI)
SAMPLE_EMAIL = "me@home.com"
QUOTED_EMAIL = quote(SAMPLE_EMAIL)

GET_ENDPOINT_DATA = [
    pytest.param(
        [], f"https://api.crossref.org/works/{QUOTED_DOI}", id="default_format"
    ),
    pytest.param(["JSON"], f"https://api.crossref.org/works/{QUOTED_DOI}", id="json"),
    pytest.param(
        ["JSON", SAMPLE_EMAIL],
        f"https://api.crossref.org/works/{QUOTED_DOI}",
        id="json_with_email",
    ),
    pytest.param(
        ["UnixSd"],
        f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixsd&id={QUOTED_DOI}",
        id="unixsd",
    ),
    pytest.param(
        ["UNIXSD", ""],
        f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixsd&id={QUOTED_DOI}",
        id="unixsd_with_empty_email",
    ),
    pytest.param(
        ["UNIXSD", SAMPLE_EMAIL],
        f"https://doi.crossref.org/servlet/query?pid={SAMPLE_EMAIL}&format=unixsd&id={QUOTED_DOI}",
        id="unixsd_with_email",
    ),
    pytest.param(
        ["unixref"],
        f"https://doi.crossref.org/servlet/query?pid={DEFAULT_EMAIL}&format=unixref&id={QUOTED_DOI}",
        id="unixref",
    ),
    pytest.param(
        ["UNIXref", SAMPLE_EMAIL],
        f"https://doi.crossref.org/servlet/query?pid={SAMPLE_EMAIL}&format=unixref&id={QUOTED_DOI}",
        id="unixref_with_email",
    ),
]


@pytest.mark.parametrize("test_input,expected", GET_ENDPOINT_DATA)
def test_get_endpoint_ok(test_input, expected):
    assert get_endpoint(SAMPLE_DOI, *test_input) == expected


def test_get_endpoint_fail():

    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint()

    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint("")

    with pytest.raises(ValueError, match=r"Invalid output format: XML"):
        get_endpoint("some_doi_here", "XML")
