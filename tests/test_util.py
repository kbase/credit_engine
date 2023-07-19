import json
import os.path
import re
from pathlib import Path, PurePath

import pytest
from pydantic import ValidationError

import credit_engine.constants as CE  # noqa: N812
from credit_engine import util
from tests.common import check_stdout_for_errs, run_file_contents_check

from .conftest import (
    FILE_LIST_TEST_DATA,
    FILE_NAME,
    OUTPUT_FORMAT_EXT_TEST_DATA,
    TRIM_DEDUPE_LIST_DATA,
    VALID_DOI_A,
)

KBASE_DOI_FILE = "sample_data/kbase/kbase-dois.txt"

DOI_TEST_DATA = [
    pytest.param(
        {
            "doi": doi,
            "file_name": FILE_NAME[doi],
        },
        id=doi,
    )
    for doi in FILE_NAME
]

FILE_READ_WRITE_JSON_TEST_DATA = [
    # top level data structure is a list
    pytest.param(
        "sample_data/osti/10.25982_26409.220_1820944.json", id="list_of_dicts"
    ),
    # top level data structure is a dict
    pytest.param("sample_data/crossref/10.46936_10.25585_60000513.json", id="dict"),
]

TEXT_LINES = """Write a list of lines of text to a file.

:param file_path: path relative to the credit_engine repo
:type file_path: string
:param lines: content to be written to the file
:type lines: list / dict / str
"""


@pytest.mark.parametrize("param", DOI_TEST_DATA)
def test_make_safe_file_name(param):
    assert util.make_safe_file_name(param["doi"]) == param["file_name"]


@pytest.mark.parametrize("param", TRIM_DEDUPE_LIST_DATA)
def test_trim_dedupe_list(param):
    if "output" in param:
        clean_dois = util.trim_dedupe_list(param["input"])
        assert clean_dois == param["output"]
    else:
        with pytest.raises(ValidationError, match=re.escape(param["error"])):
            util.trim_dedupe_list(param["input"])


def test_full_path():
    full_path_to_file = util.full_path(KBASE_DOI_FILE)
    assert Path.is_file(full_path_to_file)
    assert Path(full_path_to_file).is_absolute()

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


@pytest.mark.parametrize("param", FILE_READ_WRITE_JSON_TEST_DATA)
def test_file_read_write_json_list(param, tmp_path):
    dest_path = tmp_path / "json.txt"
    json_sample = util.read_json_file(param)
    util.write_to_file(dest_path, json_sample)
    assert json_sample == util.read_json_file(dest_path)


def test_file_read_write_text_lines(tmp_path):
    text_lines_file = tmp_path / "text.txt"
    util.write_to_file(text_lines_file, TEXT_LINES)
    # compare to existing file
    assert util.read_text_file(text_lines_file) == util.read_text_file(
        "tests/data/text.txt"
    )


def test_file_write_bytes(tmp_path):
    dest_path = tmp_path / "bytes.txt"
    byte_content = TEXT_LINES.encode()
    util.write_bytes_to_file(dest_path, byte_content)
    dest_path_contents = dest_path.read_bytes()
    assert dest_path_contents == byte_content


save_data_to_file_data = [
    {
        "doi": "10.25585/1487552",
        "suffix": "json",
        "data": json.loads(
            Path.read_text(util.full_path("sample_data/datacite/10.25585_1487552.json"))
        ),
    },
    {
        "doi": "10.25585/1487552",
        "suffix": "xml",
        "data": Path.read_bytes(
            util.full_path("sample_data/datacite/10.25585_1487552.xml")
        ),
    },
    {
        "doi": "10.46936/10.25585/60007526",
        "suffix": ".xml",
        "trimmed_suffix": "xml",
        "data": Path.read_bytes(
            util.full_path("sample_data/crossref/10.46936_10.25585_60007526.unixsd.xml")
        ),
    },
]


SAVE_DATA_TO_FILE_TEST_DATA = [
    pytest.param(
        param,
        id=f"save_{param['suffix']}",
    )
    for param in save_data_to_file_data
]


@pytest.mark.parametrize("param", SAVE_DATA_TO_FILE_TEST_DATA)
def test_save_data_to_file(param, tmp_path):
    doi_file = (
        tmp_path
        / f'{util.make_safe_file_name(param["doi"])}.{param["trimmed_suffix"]if "trimmed_suffix" in param else param["suffix"]}'
    )
    assert (
        util.save_data_to_file(param["doi"], tmp_path, param["suffix"], param["data"])
        == doi_file
    )
    run_file_contents_check(doi_file, param["data"])


SAVE_DATA_TO_FILE_FAIL_TEST_DATA = [
    # dir does not exist
    pytest.param(
        {
            "doi": VALID_DOI_A,
            "save_dir": "no/dir/found",
            "suffix": "json",
            "data": {"this": "that"},
            "error": f"[Errno 2] No such file or directory: '{util.full_path('no/dir/found')}/{FILE_NAME[VALID_DOI_A]}.json'",
        },
        id="relative_dir_not_found",
    ),
    pytest.param(
        {
            "doi": VALID_DOI_A,
            "save_dir": "/no/dir/found",
            "suffix": "json",
            "data": {"this": "that"},
            "error": f"[Errno 2] No such file or directory: '/no/dir/found/{FILE_NAME[VALID_DOI_A]}.json'",
        },
        id="absolute_dir_not_found",
    ),
    pytest.param(
        {
            "doi": VALID_DOI_A,
            "suffix": "json",
            "data": {"this": {"that", "the", "other"}},
            "error": "Object of type set is not JSON serializable",
        },
        id="json_encode_error",
    ),
]


@pytest.mark.parametrize("param", SAVE_DATA_TO_FILE_FAIL_TEST_DATA)
def test_save_data_to_file_fail(param, capsys, tmp_path):
    if "save_dir" not in param:
        param["save_dir"] = tmp_path

    assert (
        util.save_data_to_file(
            param["doi"], param["save_dir"], param["suffix"], param["data"]
        )
        is None
    )

    check_stdout_for_errs(capsys, [param["error"]])


FILES = {
    "dot_json": [
        "file_a.json",
        "file_b.json",
    ],
    "numbered": ["file_1.txt", "file_2.txt", "file_1.xml", "file_2.xml"],
    "only_one": ["file_1.txt"],
    "twos": ["file_2.txt", "file_2.xml"],
    "none": [],
}
FILES["all"] = FILES["numbered"] + FILES["dot_json"]

ALL_FILES = [".DS_Store"] + FILES["all"]
DIRECTORIES = [f"directory_{character}" for character in ["1", "2", "a", "b"]]

DIR_SCANNER_TEST_INPUTS = {
    "all": {
        "conditions": [],
    },
    "dot_json": {
        "conditions": [lambda x: x.endswith(".json")],
    },
    "numbered": {
        "conditions": [
            lambda x: x.find("1") != -1 or x.find("2") != -1,
        ],
    },
    "only_one": {
        "conditions": [
            lambda x: x.find("1") != -1,
            lambda x: x.endswith("txt"),
        ],
    },
    "twos": {
        "conditions": [
            lambda x: x.find("2") != -1,
        ],
    },
    "none": {
        "conditions": [
            lambda x: x.find("hippopotamus") != -1,
        ]
    },
}


DIR_SCANNER_TEST_DATA = []
for k, v in DIR_SCANNER_TEST_INPUTS.items():
    v["expected"] = FILES[k]
    DIR_SCANNER_TEST_DATA.append(pytest.param(v, id=k))


def set_up_test_dir(tmp_path):
    # set up the dir_scanner test
    dir_path = tmp_path / "dir_scanner_test"
    dir_path.mkdir(exist_ok=True)
    for file_name in ALL_FILES:
        file_path = dir_path / file_name
        file_path.touch(exist_ok=True)
    # add in directories
    for dir_name in DIRECTORIES:
        new_dir = dir_path / dir_name
        new_dir.mkdir(exist_ok=True)
    return dir_path


@pytest.mark.parametrize("param", DIR_SCANNER_TEST_DATA)
def test_dir_scanner(param, tmp_path):
    test_dir = set_up_test_dir(tmp_path)

    dir_contents = []
    for child in test_dir.iterdir():
        dir_contents.append(child.name)
    # ensure that the dir has been set up properly
    assert set(ALL_FILES + DIRECTORIES) == set(dir_contents)

    got = util.dir_scanner(test_dir, param["conditions"])
    assert set(got) == {os.path.join(test_dir, f) for f in param["expected"]}


def test_dir_scanner_with_relative_file_input():
    got = util.dir_scanner(KBASE_DOI_FILE, [lambda x: x.find("kbase-dois") != -1])
    assert len(got) == 1
    assert got[0].endswith(KBASE_DOI_FILE)


@pytest.mark.parametrize("param", FILE_LIST_TEST_DATA)
def test_read_unique_lines(param):
    if "output" in param:
        returned_input = util.read_unique_lines(param["input"])
        assert returned_input == param["output"]

    else:
        with pytest.raises(param["error_type"], match=re.escape(param["error"])):
            util.read_unique_lines(param["input"])


@pytest.mark.parametrize("param", OUTPUT_FORMAT_EXT_TEST_DATA)
def test_get_extension_string(param):
    output_format = param["input"]
    expected = None
    if "expected" in param:
        expected = param["expected"]

        assert util.get_extension(output_format) == expected
        if not isinstance(output_format, CE.OutputFormat):
            assert util.get_extension(output_format.upper()) == expected
            assert util.get_extension(output_format.title()) == expected
            assert util.get_extension(output_format.title().swapcase()) == expected
    else:
        with pytest.raises(param["error"], match=param["error_msg"]):
            util.get_extension(param["input"])
