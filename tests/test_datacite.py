import pytest

import credit_engine.parsers.datacite as datacite
import credit_engine.parsers.doi as doi
from credit_engine.parsers.datacite import get_endpoint, retrieve_doi

from .common import run_retrieve_doi_list
from .conftest import (
    CLEAN_DOI_LIST_DATA,
    DOI_DATA,
    QUOTED_DOI,
    RETRIEVE_DOI_LIST_TEST_DATA,
    SAMPLE_DOI,
)


def test_get_endpoint_ok():
    expected = f"https://api.datacite.org/dois/{QUOTED_DOI}?affiliation=true"
    assert get_endpoint(SAMPLE_DOI) == expected


def test_get_endpoint_fail():
    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint()

    with pytest.raises(ValueError, match=r"Missing required argument: doi"):
        get_endpoint("")


def test_retrieve_doi_ok(_mock_response):
    assert retrieve_doi("VALID_DOI").json() == DOI_DATA["VALID_DOI"]


def test_retrieve_doi_fail(_mock_response):
    with pytest.raises(
        ValueError, match="Request for NOT_FOUND failed with status code 404"
    ):
        retrieve_doi("NOT_FOUND")


@pytest.mark.parametrize("param", RETRIEVE_DOI_LIST_TEST_DATA)
def test_retrieve_doi_list(param, _mock_response, tmp_path, capsys, monkeypatch):
    default_dir = tmp_path / "default_dir"
    monkeypatch.setattr(datacite, "SAMPLE_DATA_DIR", default_dir)

    run_retrieve_doi_list(
        capsys=capsys,
        default_dir=default_dir,
        param=param,
        source="datacite",
        tmp_path=tmp_path,
    )


@pytest.mark.parametrize("param", CLEAN_DOI_LIST_DATA)
def test_retrieve_doi_list_fail(param, _mock_response):
    # only run tests where we know the test fails
    if "output" not in param:
        with pytest.raises(ValueError, match=param["error"]):
            doi.retrieve_doi_list(param["input"], source="datacite")
