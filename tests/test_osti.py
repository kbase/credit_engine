import pytest

from credit_engine.parsers.osti import get_endpoint

from tests.conftest import QUOTED_DOI, SAMPLE_DOI


def test_get_endpoint_ok():
    expected = f"https://www.osti.gov/api/v1/records/{QUOTED_DOI}"
    assert get_endpoint(SAMPLE_DOI) == expected


def test_get_endpoint_fail():
    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint()

    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint("")
