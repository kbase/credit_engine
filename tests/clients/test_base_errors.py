"""Input error tests for retrieve_dois and retrieve_dois_from_unknown."""
import re

import pytest

import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients import base
from tests.conftest import (
    DOI_LIST_TEST_DATA,
    FILE_CONTENTS_TEST_DATA,
    SAVE_DIR_X_SAVE_FILES_TEST_DATA,
    SOURCE_TEST_DATA,
    SOURCE_X_FORMAT_TEST_DATA,
)


@pytest.mark.parametrize("source", SOURCE_TEST_DATA)
def test__validate_retrieve_dois_invalid_source(source):
    """Ensure invalid sources are rejected."""
    if "error" in source:
        with pytest.raises(ValueError, match=re.escape(source["error"])):
            base.retrieve_dois(**source["args"])
        return

    (params, _) = base._validate_retrieve_dois(
        **source["args"], doi_list=["one", "two", "three"]
    )
    assert params.source.value == source["output"]
    assert params.dois == {"one", "two", "three"}
    assert params.output_formats == {CE.OutputFormat.JSON}


@pytest.mark.parametrize("save_files_dir", SAVE_DIR_X_SAVE_FILES_TEST_DATA)
@pytest.mark.parametrize("source_format", SOURCE_X_FORMAT_TEST_DATA)
@pytest.mark.parametrize("doi_list", DOI_LIST_TEST_DATA)
@pytest.mark.parametrize("doi_file", FILE_CONTENTS_TEST_DATA)
def test_retrieve_dois_errors(
    doi_file,
    doi_list,
    source_format,
    save_files_dir,  # save_dir
):
    """Test various combinations of inputs that will trigger errors.

    :param doi_file: _description_
    :type doi_file: _type_
    :param doi_list: _description_
    :type doi_list: _type_
    :param source_format: _description_
    :type source_format: _type_
    :param save_files_dir: _description_
    :type save_files_dir: _type_
    """
    error_list = []
    for parameter in [
        doi_file,
        doi_list,
        source_format,
        save_files_dir,
    ]:  # save_dir]:
        if "error" in parameter:
            error_list = error_list + parameter["error"]

    if not error_list:
        return

    args = {
        **save_files_dir["args"],
        **source_format["args"],
        **doi_file["args"],
        **doi_list["args"],
    }

    with pytest.raises(ValueError) as exc_info:
        base.retrieve_dois(**args)

    for err in error_list:
        assert re.search(re.escape(err), exc_info.exconly()) is not None


# TODO @ialarmedalien: add error tests for retrieve_dois_from_unknown
# requires a new source_format variable without the OSTI source stuff
# https://github.com/kbase/credit_engine/issues/159
# @pytest.mark.parametrize("save_files_dir", SAVE_DIR_X_SAVE_FILES_TEST_DATA)
# @pytest.mark.parametrize("source_format", SOURCE_X_FORMAT_TEST_DATA)
# @pytest.mark.parametrize("doi_list", DOI_LIST_TEST_DATA)
# @pytest.mark.parametrize("doi_file", FILE_CONTENTS_TEST_DATA)
# def test_retrieve_dois_from_unknown_errors(
#     doi_file,
#     doi_list,
#     source_format,
#     save_files_dir,  # save_dir
# ):
#     """Test various combinations of inputs that will trigger errors."""
#     error_list = []
#     for parameter in [
#         doi_file,
#         doi_list,
#         source_format,
#         save_files_dir,
#     ]:  # save_dir]:
#         if "error" in parameter:
#             error_list = error_list + parameter["error"]

#     if not error_list:
#         return

#     args = {
#         **save_files_dir["args"],
#         **source_format["args"],
#         **doi_file["args"],
#         **doi_list["args"],
#     }

#     with pytest.raises(ValueError) as exc_info:
#         base.retrieve_dois_from_unknown(**args)

#     for err in error_list:
#         assert re.search(re.escape(err), exc_info.exconly()) is not None
