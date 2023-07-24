"""Tests for the ClientArgs classes."""
import re
from pathlib import Path
from typing import Any

import pytest
from pydantic import (
    Field,
)

import credit_engine.constants as CE  # noqa: N812
from credit_engine.clients import base
from credit_engine.clients.args import (
    AuthenticatedClientArgs,
    EmailClientArgs,
    GenericClientArgs,
)
from tests.conftest import (
    DOI_LIST_TEST_DATA,
    ERROR_AT_LEAST_THREE_CHARS,
    ERROR_FIELD_REQUIRED,
    ERROR_NONE_NOT_ALLOWED,
    FILE_CONTENTS_TEST_DATA,
    OUTPUT_FORMATS_TEST_DATA,
    SAVE_DIR_TEST_DATA,
    SAVE_FILES_TEST_DATA,
    SOURCE_TEST_DATA,
)

VALID_SOURCE = "datacite"
VALID_CLIENT = base
EMAIL_VALIDATION_ERROR = (
    "email_address\n  value is not a valid email address (type=value_error.email)"
)


@pytest.mark.parametrize("source", SOURCE_TEST_DATA)
def test_generic_client_args_invalid_source(source):
    """Test output source when creating a new set of client args and picking the client."""
    if "error" in source:
        with pytest.raises(ValueError, match=re.escape(source["error"])):
            base._validate_retrieve_dois(**source["args"])

    else:
        (params, _) = base._validate_retrieve_dois(**source["args"])
        assert params.output_formats == {CE.OutputFormat.JSON}
        assert params.source.value == source["output"]


def test_generic_client_args_dois_from_file() -> None:
    """Ensure there is no input to dois_from_file."""
    args = {
        "source": VALID_SOURCE,
        "client": VALID_CLIENT,
        "dois_from_file": "some value",
    }
    with pytest.raises(
        ValueError,
        match=re.escape(
            "This value is automatically generated; please do not assign to it."
        ),
    ):
        GenericClientArgs(**args)


@pytest.mark.parametrize("doi_file", FILE_CONTENTS_TEST_DATA)
def test_generic_client_args_doi_file(doi_file):
    """Test client args for doi_file.

    :param doi_file: _description_
    :type doi_file: _type_
    """
    args = {"source": VALID_SOURCE, "client": VALID_CLIENT, **doi_file["args"]}

    if "error" in doi_file:
        with pytest.raises(ValueError, match=re.escape("".join(doi_file["error"]))):
            GenericClientArgs(**args)
        return

    params = GenericClientArgs(**args)

    if "doi_file" in doi_file["args"]:
        assert params.doi_file is not None
        assert params.doi_file.samefile(Path(doi_file["args"]["doi_file"]))
    assert params.doi_list is None
    assert params.dois == doi_file["output"]


@pytest.mark.parametrize("doi_list", DOI_LIST_TEST_DATA)
def test_generic_client_args_doi_list(doi_list):
    """Test client args for doi_list.

    :param doi_list: _description_
    :type doi_list: _type_
    """
    args = {"source": VALID_SOURCE, "client": VALID_CLIENT, **doi_list["args"]}

    if "error" in doi_list:
        with pytest.raises(ValueError, match=re.escape("\n".join(doi_list["error"]))):
            GenericClientArgs(**args)
        return

    params = GenericClientArgs(**args)

    assert params.doi_list == doi_list["output"]
    assert params.output_formats == {CE.OutputFormat.JSON}
    assert params.dois == set() if doi_list["output"] is None else doi_list["output"]


@pytest.mark.parametrize("doi_file", FILE_CONTENTS_TEST_DATA)
@pytest.mark.parametrize("doi_list", DOI_LIST_TEST_DATA)
def test__validate_client_args_doi_input(doi_file, doi_list) -> None:
    """Test client args for different combinations of doi_file and doi_list.

    :param doi_file: _description_
    :type doi_file: _type_
    :param doi_list: _description_
    :type doi_list: _type_
    """
    args = {
        "source": VALID_SOURCE,
        "client": VALID_CLIENT,
        **doi_file["args"],
        **doi_list["args"],
    }

    errors = []
    if "error" in doi_file:
        errors = errors + doi_file["error"]
    if "error" in doi_list:
        errors = errors + doi_list["error"]

    if errors:
        with pytest.raises(ValueError, match=re.escape("\n".join(errors))):
            GenericClientArgs(**args)
        return

    output = set()
    if "output" in doi_file and doi_file["output"]:
        output = doi_file["output"]
    if "output" in doi_list and doi_list["output"]:
        output = output | doi_list["output"]

    params = GenericClientArgs(**args)
    assert params.dois == output


@pytest.mark.parametrize("output_formats", OUTPUT_FORMATS_TEST_DATA)
def test_generic_client_args_output_formats(output_formats):
    """Test client args for output_formats.

    :param output_formats: _description_
    :type output_formats: _type_
    """
    args = {"source": VALID_SOURCE, "client": VALID_CLIENT, **output_formats["args"]}

    if "error" in output_formats or "error_regex" in output_formats:
        if "error_regex" in output_formats:
            with pytest.raises(ValueError, match=output_formats["error_regex"]):
                GenericClientArgs(**args)
            return

        with pytest.raises(
            ValueError, match=re.escape("\n".join(output_formats["error"]))
        ):
            GenericClientArgs(**args)
        return

    params = GenericClientArgs(**args)

    assert params.output_formats == output_formats["output"]


def test_generic_client_args_default_output_formats():
    """Test client args for default output formats."""

    class TestClientOutputFormat(GenericClientArgs):
        output_formats: set[CE.OutputFormat] = Field(default={CE.OutputFormat.XML})

    args = {"source": VALID_SOURCE, "client": VALID_CLIENT}
    params = TestClientOutputFormat(**args)
    assert params.output_formats == {CE.OutputFormat.XML}


def test_generic_client_invalid_output_formats() -> None:
    """Test client args for custom valid output formats."""

    class TestClientOutputFormat(GenericClientArgs):
        VALID_OUTPUT_FORMATS: set[CE.OutputFormat] = Field(
            {CE.OutputFormat.XML}, const=True
        )
        output_formats: set[CE.OutputFormat] = Field(default={CE.OutputFormat.XML})

    args = {"source": VALID_SOURCE, "client": VALID_CLIENT}

    with pytest.raises(
        ValueError,
        match=re.escape(
            "output_formats\n  Invalid output format(s): 'text', OutputFormat.JSON\n"
            "  Valid output formats: OutputFormat.XML (type=value_error)"
        ),
    ):
        TestClientOutputFormat(**args, output_formats={"json", "text", "xml"})  # type: ignore


@pytest.mark.parametrize("save_dir", SAVE_DIR_TEST_DATA)
def test_generic_client_args_save_dir(save_dir) -> None:
    """Test client arguments for save_dir.

    :param save_dir: _description_
    :type save_dir: _type_
    """
    args = {"source": VALID_SOURCE, "client": VALID_CLIENT, **save_dir["args"]}
    if "error" in save_dir:
        with pytest.raises(ValueError, match=re.escape("".join(save_dir["error"]))):
            GenericClientArgs(
                **args,
                save_files=True,
            )

        # should be no issue if save_files is false
        params_save_false = GenericClientArgs(
            **args,
            save_files=False,
        )
        assert params_save_false.save_dir is None
        return

    params_save_true = GenericClientArgs(
        **args,
        save_files=True,
    )

    assert params_save_true.save_dir == save_dir["output"]

    params_save_false = GenericClientArgs(
        **args,
        save_files=False,
    )

    assert params_save_false.save_dir is None


@pytest.mark.parametrize("save_files", SAVE_FILES_TEST_DATA)
def test_generic_client_args_save_files(save_files):
    """Test client args for save_files.

    :param save_files: _description_
    :type save_files: _type_
    """
    args = {"source": VALID_SOURCE, "client": VALID_CLIENT, **save_files["args"]}
    if "error" in save_files:
        with pytest.raises(ValueError, match=re.escape("\n".join(save_files["error"]))):
            GenericClientArgs(**args)
        return

    params = GenericClientArgs(**args)
    assert params.save_files == save_files["output"]


VALID_EMAIL = "me@home.com"

EMAIL_TEST_DATA = [
    pytest.param(
        {
            "args": {},
            "output": CE.DEFAULT_EMAIL,
        },
        id="valid_email_missing_use_default",
    ),
    pytest.param(
        {
            "args": {
                "email_address": "something awful",
            },
            "error": [EMAIL_VALIDATION_ERROR],
        },
        id="invalid_email_string",
    ),
    pytest.param(
        {
            "args": {
                "email_address": "",
            },
            "error": [EMAIL_VALIDATION_ERROR],
        },
        id="invalid_email_len_0",
    ),
    pytest.param(
        {
            "args": {
                "email_address": "  \n\n  \r  \t \n",
            },
            "error": [EMAIL_VALIDATION_ERROR],
        },
        id="invalid_email_whitespace",
    ),
    pytest.param(
        {
            "args": {
                "email_address": None,
            },
            "error": [ERROR_NONE_NOT_ALLOWED],
        },
        id="invalid_email_None",
    ),
    pytest.param(
        {
            "args": {
                "email_address": VALID_EMAIL,
            },
            "output": VALID_EMAIL,
        },
        id="valid_email_crossref",
    ),
    pytest.param(
        {
            "args": {
                "email_address": "some invalid string",
            },
            "error": [EMAIL_VALIDATION_ERROR],
        },
        id="invalid_email_no_error",
    ),
]


@pytest.mark.parametrize("email", EMAIL_TEST_DATA)
def test_generic_client_args_email(email):
    """Test client args with and without an email field.

    :param email: _description_
    :type email: _type_
    """
    args = {"source": VALID_SOURCE, "client": VALID_CLIENT, **email["args"]}

    no_email_params = GenericClientArgs(**args)
    with pytest.raises(
        AttributeError, match=re.escape("object has no attribute 'email_address'")
    ):
        assert no_email_params.email_address is None  # type: ignore

    if "error" in email:
        with pytest.raises(ValueError, match=re.escape("\n".join(email["error"]))):
            EmailClientArgs(**args)
        return

    params = EmailClientArgs(**args)
    assert params.email_address == email["output"]


USER = "my_cool_username"
PASS = "my_cool_password"  # noqa: S105
USER_LINE = "username\n"
PASS_LINE = "password\n"  # noqa: S105

AUTH_TEST_DATA = [
    pytest.param(
        {
            "args": {
                "username": USER,
                "password": PASS,
            },
            "output": {
                "username": USER,
                "password": PASS,
            },
        },
        id="valid_pw_name",
    ),
    pytest.param(
        {
            "args": {},
            "error": [
                USER_LINE
                + ERROR_FIELD_REQUIRED
                + "\n"
                + PASS_LINE
                + ERROR_FIELD_REQUIRED
            ],
        },
        id="invalid_missing_pw_name",
    ),
    pytest.param(
        {
            "args": {"password": PASS},
            "error": [USER_LINE + ERROR_FIELD_REQUIRED],
        },
        id="invalid_missing_name",
    ),
    pytest.param(
        {
            "args": {"name": "my cool username"},
            "error": [PASS_LINE + ERROR_FIELD_REQUIRED],
        },
        id="invalid_missing_pw",
    ),
]

possible_values = [
    (None, ERROR_NONE_NOT_ALLOWED, "none"),
    ("", ERROR_AT_LEAST_THREE_CHARS, "empty"),
    ("az", ERROR_AT_LEAST_THREE_CHARS, "az"),
    ("\r   \n \r \t\t", ERROR_AT_LEAST_THREE_CHARS, "whitespace"),
    ("\r\r   \t  az   \t\t\r", ERROR_AT_LEAST_THREE_CHARS, "too_short"),
    ("some valid text", None, "valid"),
    ("\n\n\n   some valid text \t\t   ", None, "trimmed"),
]

for username_value in possible_values:
    (u_val, u_err, u_name) = username_value
    for password_value in possible_values:
        (p_val, p_err, p_name) = password_value
        error = []
        if u_err:
            error.append(USER_LINE + u_err)
        if p_err:
            error.append(PASS_LINE + p_err)

        auth_params: dict[str, Any] = {
            "args": {
                "username": u_val,
                "password": p_val,
            }
        }

        if len(error):
            auth_params["error"] = error
        else:
            auth_params["output"] = {
                "username": "some valid text",
                "password": "some valid text",
            }

        AUTH_TEST_DATA.append(
            pytest.param(
                auth_params,
                id=f"invalid_user_{u_name}_pw_{p_name}",
            )
        )


@pytest.mark.parametrize("auth", AUTH_TEST_DATA)
def test_generic_client_args_username_password(auth):
    """Test the username and password for a client requiring auth.

    :param auth: dictionary of input, output, and errors
    :type email: dict[str, Any].
    """
    args = {"source": VALID_SOURCE, "client": VALID_CLIENT, **auth["args"]}

    no_auth_params = GenericClientArgs(**args)
    with pytest.raises(
        AttributeError, match=re.escape("object has no attribute 'username'")
    ):
        assert no_auth_params.username is None  # type: ignore
    with pytest.raises(
        AttributeError, match=re.escape("object has no attribute 'password'")
    ):
        assert no_auth_params.password is None  # type: ignore

    if "error" in auth:
        with pytest.raises(ValueError, match=re.escape("\n".join(auth["error"]))):
            AuthenticatedClientArgs(**args)
        return

    params = AuthenticatedClientArgs(**args)
    assert params.username == auth["output"]["username"]
    assert params.password == auth["output"]["password"]
