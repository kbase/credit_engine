import sys

print(sys.path)

import pytest
import credit_engine.util as util
from pathlib import Path

enc = "encoded"
f_name = "file_name"

KBASE_DOI_FILE = "sample_data/kbase/kbase-dois.txt"

doi_test_data = [
    pytest.param(
        {
            "doi": "10.1000/123%45.6#789",
            enc: "10.1000/123%2545.6%23789",
            f_name: "10.1000_123_45.6_789",
        },
        id="percent_hashtag",
    ),
    pytest.param(
        {
            "doi": '10.100/%"# ?.<>{}^[]`|\\+',
            enc: "10.100/%25%22%23%20%3F.%3C%3E%7B%7D%5E%5B%5D%60%7C%5C%2B",
            f_name: "10.100_._",
        },
        id="all_special_uri_chars",
    ),
]


@pytest.mark.parametrize("param", doi_test_data)
def test_encode_doi(param):
    assert util.encode_doi(param["doi"]) == param[enc]


@pytest.mark.parametrize("param", doi_test_data)
def test_doi_to_file_name(param):
    assert util.doi_to_file_name(param["doi"]) == param[f_name]


def test_full_path():
    full_path_to_file = util.full_path(KBASE_DOI_FILE)
    print(util.full_path("src/util.py"))
    assert Path.is_file(full_path_to_file)
    assert Path(full_path_to_file).is_absolute()

    from pathlib import PurePath

    alt_path_to_file = PurePath(KBASE_DOI_FILE)
    assert alt_path_to_file.is_absolute() is False
    aptf = Path(alt_path_to_file)
    full_alt_path = util.full_path(aptf)
    assert full_alt_path.is_absolute()
    assert full_alt_path.samefile(full_path_to_file)


def test_file_read_write_list(tmp_path):
    dest_path = tmp_path / "lines.txt"
    # round trip a simple list
    sample_list = ["hocus", "pocus", "diplo", "docus"]
    util.write_to_file(dest_path, sample_list)
    lines = util.read_text_file(dest_path)
    assert lines == sample_list

    # round trip an existing file
    doi_list_path = tmp_path / "doi_list.txt"
    doi_list = util.read_text_file(KBASE_DOI_FILE)
    assert len(doi_list) > 1
    util.write_to_file(doi_list_path, doi_list)
    assert doi_list == util.read_text_file(doi_list_path)


def test_file_read_write_json(tmp_path):
    dest_path = tmp_path / "dict.txt"
    # top level data structure is a list; ensure it is round-tripped correctly
    json_sample = util.read_json_file(
        "sample_data/osti/10.25982_26409.220_1820944.json"
    )
    util.write_to_file(dest_path, json_sample)
    assert json_sample == util.read_json_file(dest_path)


def test_file_read_write_text_lines(tmp_path):
    text_lines = """Write a list of lines of text to a file.

:param file_path: path relative to the credit_engine repo
:type file_path: string
:param lines: content to be written to the file
:type lines: list / dict / str
"""
    text_lines_file = tmp_path / "text.txt"
    util.write_to_file(text_lines_file, text_lines)
    # compare to existing file
    assert util.read_text_file(text_lines_file) == util.read_text_file(
        "tests/data/text.txt"
    )


def test_dir_scanner():
    # TODO: write tests!
    pass
