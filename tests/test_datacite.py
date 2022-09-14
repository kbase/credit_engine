from urllib.parse import quote

import pytest

from credit_engine.parsers.datacite import get_endpoint

SAMPLE_DOI = "10.46936/jejc.proj%2013?48+08-6/60005298"
QUOTED_DOI = quote(SAMPLE_DOI)


def test_get_endpoint_ok():
    expected = f"https://api.datacite.org/dois/{QUOTED_DOI}?affiliation=true"
    assert get_endpoint(SAMPLE_DOI) == expected


def test_get_endpoint_fail():

    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint()

    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint("")
