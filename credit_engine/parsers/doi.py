import types
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import quote

import requests
from pydantic import validate_arguments

import credit_engine.constants as CE
import credit_engine.parsers.crossref as crossref
import credit_engine.parsers.datacite as datacite
import credit_engine.util as util
from credit_engine.errors import make_error

SOURCE_TO_PARSER = {
    CE.CROSSREF: crossref,
    CE.DATACITE: datacite,
}


@validate_arguments
def check_doi_source(doi: CE.TrimmedString) -> Optional[str]:
    """Check whether a DOI is accessible via CrossRef

    :param doi: digital object identifier
    :type doi: str
    :return: ID of the agency from which the data can be retrieved
    :rtype: str | None
    """
    resp = requests.get(f"https://api.crossref.org/works/{quote(doi)}/agency")
    if resp.status_code == 200:
        payload = resp.json()
        agency = payload.get("message", {}).get("agency", {}).get("id", "unknown")
        print(f"doi {doi} at {agency}")
        return agency

    return None


@validate_arguments
def get_extension(source: str, output_format: str = CE.JSON) -> str:
    """Get the appropriate file extension for saving data.

    :param source: the data source
    :type source: str
    :param output_format: format of data to be saved, defaults to 'json'
    :type output_format: str, optional
    :raises ValueError: if the output format is not valid for that parser
    :return: file extension
    :rtype: str
    """
    lc_output_format = output_format.lower()
    if source not in SOURCE_TO_PARSER:
        raise ValueError(f"No parser for source {source}")
    parser = SOURCE_TO_PARSER[source]
    if lc_output_format not in parser.FILE_EXTENSIONS:
        raise ValueError(
            make_error(
                "invalid_param",
                {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: output_format},
            )
        )
    return parser.FILE_EXTENSIONS[lc_output_format]


@validate_arguments
def _validate_retrieve_doi_list_input(
    doi_list: CE.NonEmptyList[CE.TrimmedString],
    source: CE.TrimmedString,
    output_format_list: Optional[list[CE.TrimmedString]] = None,
    save_files: bool = False,
    save_dir: Optional[Union[Path, str]] = None,
) -> tuple[dict, types.ModuleType]:
    """Validate the input to retrieve_doi_list.

    :param doi_list: list of DOIs to retrieve
    :type doi_list: list[str], optional
    :param source: DOI source (e.g. DataCite, CrossRef), defaults to ''
    :type source: str, optional
    :param output_format_list: formats to retrieve the DOIs in, defaults to None
    :type output_format_list: Optional[list[str]], optional
    :param save_files: whether or not to save the files, defaults to False
    :type save_files: bool, optional
    :param save_dir: path to the save directory, defaults to None
    :type save_dir: Optional[Union[Path, str]], optional
    :raises ValueError: if there are any input parameter errors
    :return: tuple containing a dict of validated params and the parser module
    :rtype: tuple
    """
    input_errors = []
    params: dict[str, Any] = {
        "save_files": save_files,
    }
    parser: Optional[types.ModuleType] = None

    params["doi_list"] = util.clean_doi_list(doi_list)

    if source not in SOURCE_TO_PARSER:
        input_errors.append(
            make_error(
                "invalid_param", {"param": CE.DATA_SOURCE, CE.DATA_SOURCE: source}
            )
        )
    else:
        params["source"] = source
        parser = SOURCE_TO_PARSER[source]

    if output_format_list:
        if parser:
            # ensure the validity of the file format(s)
            invalid_formats = [
                fmt for fmt in output_format_list if fmt not in parser.FILE_EXTENSIONS
            ]
            if invalid_formats:
                for fmt in invalid_formats:
                    input_errors.append(
                        make_error(
                            "invalid_param",
                            {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: fmt},
                        )
                    )
            else:
                params["output_format_list"] = list(set(output_format_list))
    else:
        params["output_format_list"] = [parser.DEFAULT_FORMAT if parser else None]

    # use the sample dir if save_dir is not set
    if not save_dir and parser:
        save_dir = parser.SAMPLE_DATA_DIR

    if save_dir:
        save_dir_path = util.full_path(save_dir)

        if save_files and not (save_dir_path.exists() and save_dir_path.is_dir()):
            input_errors.append(
                make_error(
                    "invalid_param",
                    {
                        "param": "save_dir",
                        "save_dir": f"'{save_dir}' does not exist or is not a directory",
                    },
                )
            )
        else:
            params["save_dir"] = save_dir_path

    if input_errors:
        input_errors.append("Please check the above errors and try again.")
        raise ValueError("\n".join(input_errors))

    return (params, parser)


@validate_arguments
def retrieve_doi_list(
    doi_list: CE.NonEmptyList[CE.TrimmedString],
    source: CE.TrimmedString,
    output_format_list: Optional[list[CE.TrimmedString]] = None,
    save_files: bool = False,
    save_dir: Optional[Union[Path, str]] = None,
) -> dict:
    """Retrieve a list of DOIs

    :param doi_list: list of DOIs to retrieve
    :type doi_list: list[str], optional
    :param source: DOI source (e.g. DataCite, CrossRef), defaults to ''
    :type source: str, optional
    :param output_format_list: formats to retrieve the DOIs in, defaults to None
    :type output_format_list: Optional[list[str]], optional
    :param save_files: whether or not to save the files, defaults to False
    :type save_files: bool, optional
    :param save_dir: path to the save directory, defaults to None
    :type save_dir: Optional[Union[Path, str]], optional

    :return: dictionary of results in the format:
        data: return data keyed by DOI and format
        files: path to the saved data files, keyed by DOI and format [Optional]
    :rtype: dict
    """

    (params, parser) = _validate_retrieve_doi_list_input(
        doi_list=doi_list,
        source=source,
        output_format_list=output_format_list,
        save_files=save_files,
        save_dir=save_dir,
    )

    results = {
        CE.DATA: {},
    }

    if params["save_files"]:
        results[CE.FILES] = {}

    for doi in params["doi_list"]:
        results[CE.DATA][doi] = parser.retrieve_doi(
            doi, output_format_list=params["output_format_list"]
        )
        if not save_files:
            continue

        if doi not in results[CE.FILES]:
            results[CE.FILES][doi] = {}
        for fmt in params["output_format_list"]:
            if results[CE.DATA][doi][fmt] is None:
                results[CE.FILES][doi][fmt] = None
                continue
            # otherwise, save to file
            doi_file = util.save_data_to_file(
                doi=doi,
                save_dir=params["save_dir"],
                suffix=get_extension(params["source"], fmt),
                data=results[CE.DATA][doi][fmt],
            )
            if doi_file:
                results[CE.FILES][doi][fmt] = doi_file

    return results
