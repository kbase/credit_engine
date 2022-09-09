import sys
print(sys.path)

import pytest
import src.util as util
from pathlib import Path

enc = "encoded"
f_name = "file_name"

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
    full_path_to_file = util.full_path("sample_data/kbase/kbase-dois.txt")
    print(util.full_path("src/util.py"))

    assert Path.is_file(full_path_to_file)
    assert Path(full_path_to_file).is_absolute()


def test_file_read_write_list():
    # round trip a simple list
    sample_list = ["hocus", "pocus", "diplo", "docus"]
    util.write_to_file("tests/temp/lines.txt", sample_list)
    lines = util.read_text_file("tests/temp/lines.txt")
    assert lines == sample_list

    # round trip an existing file
    doi_list = util.read_text_file("sample_data/kbase/kbase-dois.txt")
    assert len(doi_list) > 1
    util.write_to_file("tests/temp/doi_list.txt", doi_list)
    assert doi_list == util.read_text_file("tests/temp/doi_list.txt")


def test_file_read_write_json():
    # top level data structure is a list; ensure it is round-tripped correctly
    json_sample = util.read_json_file(
        "sample_data/osti/10.25982_26409.220_1820944.json"
    )
    util.write_to_file("tests/temp/dict.txt", json_sample)
    assert json_sample == util.read_json_file("tests/temp/dict.txt")


def test_file_read_write_text_lines():
    # TODO: add test
    util.write_to_file(
        "tests/temp/text.txt",
        """Write a list of lines of text to a file.

:param file_path: path relative to the credit_engine repo
:type file_path: string
:param lines: content to be written to the file
:type lines: list / dict / str
""",
    )


def test_dir_scanner():
    # TODO: write tests!
    pass
