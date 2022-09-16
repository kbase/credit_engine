import os.path
from pathlib import Path, PurePath

import pytest

import credit_engine.util as util

from .conftest import CLEAN_DOI_LIST_DATA, MockResponse

KBASE_DOI_FILE = "sample_data/kbase/kbase-dois.txt"

DOI_TEST_DATA = [
    pytest.param(
        {
            "doi": "10.1000/123%45.6#789",
            "file_name": "10.1000_123_45.6_789",
        },
        id="percent_hashtag",
    ),
    pytest.param(
        {
            "doi": '10.100/%"# ?.<>{}^[]`|\\+',
            "file_name": "10.100_._",
        },
        id="all_special_uri_chars",
    ),
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
def test_doi_to_file_name(param):
    assert util.doi_to_file_name(param["doi"]) == param["file_name"]


@pytest.mark.parametrize("param", CLEAN_DOI_LIST_DATA)
def test_clean_doi_list(param):
    if "output" in param:
        clean_dois = util.clean_doi_list(param["input"])
        assert set(clean_dois) == set(param["output"])
    else:
        with pytest.raises(ValueError, match=param["error"]):
            util.clean_doi_list(param["input"])


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


SAVE_DATA_TO_FILE_TEST_DATA = [
    pytest.param(
        {
            "doi": "VALID_DOI",
            "suffix": "json",
            "resp": MockResponse({"json": {"this": "that"}}),
            "doi_file": "VALID_DOI.json",
        },
        id="",
    )
]


@pytest.mark.parametrize("param", SAVE_DATA_TO_FILE_TEST_DATA)
def test_save_data_to_file(param, tmp_path):
    doi_file = tmp_path / param["doi_file"]
    assert (
        util.save_data_to_file(param["doi"], tmp_path, param["suffix"], param["resp"])
        == doi_file
    )
    assert Path.exists(doi_file) and Path.is_file(doi_file)
    # read the file contents and ensure they are correct


SAVE_DATA_TO_FILE_FAIL_TEST_DATA = [
    # dir does not exist
    pytest.param(
        {
            "doi": "VALID_DOI",
            "save_dir": "no/dir/found",
            "suffix": "json",
            "resp": MockResponse({"json": {"this": "that"}}),
            "error": f"No such file or directory: '{util.full_path('no/dir/found')}/VALID_DOI.json'",
        },
        id="relative_dir_not_found",
    ),
    pytest.param(
        {
            "doi": "VALID_DOI",
            "save_dir": "/no/dir/found",
            "suffix": "json",
            "resp": MockResponse({"json": {"this": "that"}}),
            "error": "No such file or directory: '/no/dir/found/VALID_DOI.json'",
        },
        id="absolute_dir_not_found",
    ),
]


@pytest.mark.parametrize("param", SAVE_DATA_TO_FILE_FAIL_TEST_DATA)
def test_save_data_to_file_fail(param, capsys):
    assert (
        util.save_data_to_file(
            param["doi"], param["save_dir"], param["suffix"], param["resp"]
        )
        is None
    )
    readouterr = capsys.readouterr()
    sys_out = readouterr.out.split("\n")
    match_found = False
    for line in sys_out:
        if line.find(param["error"]) != -1:
            match_found = True
            break
    assert match_found is True


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
    assert set(got) == set([os.path.join(test_dir, f) for f in param["expected"]])


def test_dir_scanner_with_relative_file_input():
    got = util.dir_scanner(KBASE_DOI_FILE, [lambda x: x.find("kbase-dois") != -1])
    assert len(got) == 1
    assert got[0].endswith(KBASE_DOI_FILE)
