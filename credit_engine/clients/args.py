"""Generic arguments for a client."""

from typing import Any

from pydantic import (
    BaseModel,
    DirectoryPath,
    EmailStr,
    Field,
    FilePath,
    conset,
    constr,
    validator,
)

import credit_engine.constants as CE  # noqa: N812
from credit_engine import util


class GenericClientArgs(BaseModel, extra="ignore", arbitrary_types_allowed=True):
    """Generic DOI client arguments.

    Input for the clients that fetch data from various sources.

    Extra fields are ignored.

    :param doi_file: valid path to a file containing IDs
    :type doi_file: Path, optional
    :param doi_list: set of IDs for the client to fetch
    :type doi_list: set[trimmed strings]
    :param save_files: whether or not to save the fetched data to a file
    :type save_files: boolean, defaults to False
    :param save_dir: directory to save files in; requires save_files=True
    :type save_dir: Path to a directory, optional
    :param source: name of the data source
    :type source: str
    :param client: module representing the client to be used to fetch data
    :type client: ModuleType
    :param output_formats: formats to retrieve data as
    :type output_formats: set[CE.OutputFormat]

    :return: object with all the relevant params data
    :rtype: GenericClientArgs
    """

    VALID_OUTPUT_FORMATS: set[CE.OutputFormat] = Field(
        {CE.OutputFormat.JSON, CE.OutputFormat.XML}, const=True
    )
    doi_file: FilePath | None = Field(None)
    dois_from_file: conset(
        constr(strip_whitespace=True, min_length=3), min_items=1
    ) | None = Field(None)
    doi_list: conset(
        constr(strip_whitespace=True, min_length=3), min_items=1
    ) | None = Field(None)
    save_files: bool = Field(default=False)
    # TODO @ialarmedalien: use client's SAMPLE_DATA_DIR as default
    # https://github.com/kbase/credit_engine/issues/158
    save_dir: DirectoryPath | None = Field(None)
    source: Any
    output_formats: conset(CE.OutputFormat, min_items=1) = Field(
        default={CE.OutputFormat.JSON}
    )

    @classmethod
    @property
    def default_output_format(cls) -> CE.OutputFormat:
        """The default output format, to be used if output_formats is empty.

        :return: default output forat
        :rtype: CE.OutputFormat
        """
        return CE.OutputFormat.JSON

    @property
    def dois(self) -> set[str]:
        """Get the set of unique dois from doi_list and doi_file.

        :return: set of DOIs
        :rtype: set[str]
        """
        all_dois: set[str] = set()
        if self.doi_list:
            all_dois = self.doi_list
        if self.dois_from_file:
            all_dois = all_dois | self.dois_from_file
        return all_dois

    @validator("doi_file", pre=True)
    def check_doi_file(cls, doi_file):
        return util.full_path(doi_file)

    @validator("dois_from_file", pre=True, always=True)
    def check_dois_from_file(cls, dois_from_file, values):
        if dois_from_file:
            raise ValueError(
                "This value is automatically generated; please do not assign to it."
            )
        if "doi_file" not in values or values["doi_file"] is None:
            return None
        return util.read_unique_lines(values["doi_file"])

    @validator("save_files", pre=True, always=True)
    def check_save_files(cls, save_files):
        if save_files is None:
            return False
        return save_files

    @validator("save_dir", pre=True, always=True)
    def check_save_dir(cls, save_dir, values):
        # this only matters if save_files is True
        if "save_files" in values and values["save_files"] is False:
            return None

        if save_dir is None:
            raise ValueError("save_dir must be defined if save_files is true")

        return util.full_path(save_dir)

    @validator("output_formats", pre=True)
    def check_output_formats(cls, output_formats, values):
        if output_formats is None:
            return None

        if not isinstance(output_formats, list | set):
            return output_formats

        formats_to_validate = set()
        for fmt in output_formats:
            if isinstance(fmt, str):
                try:
                    # check whether it's in the enum
                    formats_to_validate.add(CE.OutputFormat(fmt.strip().lower()))
                except Exception:
                    formats_to_validate.add(fmt)
                    continue
            else:
                formats_to_validate.add(fmt)

        invalid_formats = formats_to_validate - values["VALID_OUTPUT_FORMATS"]
        if invalid_formats:
            raise ValueError(
                "Invalid output format(s): "
                + ", ".join(
                    sorted(
                        f"{el!r}" if isinstance(el, str) else str(el)
                        for el in invalid_formats
                    )
                )
                + "\n"
                + "  Valid output formats: "
                + ", ".join(sorted(map(str, values["VALID_OUTPUT_FORMATS"])))
            )

        return formats_to_validate


class AuthenticatedClientArgs(GenericClientArgs):
    """Arguments for a client that requires login info.

    :return: object with validated client args
    :rtype: AuthenticatedClientArgs
    """

    username: constr(strip_whitespace=True, min_length=3)  # type: ignore
    password: constr(strip_whitespace=True, min_length=3)  # type: ignore


class EmailClientArgs(GenericClientArgs):
    """Arguments for a client that requires an email address.

    :return: object with validated client args
    :rtype: EmailClientArgs
    """

    email_address: EmailStr = Field(default=CE.DEFAULT_EMAIL)
