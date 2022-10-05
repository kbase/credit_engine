import types
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import quote

import requests
from pydantic import validate_arguments

import credit_engine.constants as CE
import credit_engine.parsers.crossref as crossref
import credit_engine.parsers.datacite as datacite
import credit_engine.parsers.osti as osti
import credit_engine.util as util
from credit_engine.errors import make_error

SOURCE_TO_PARSER = {CE.CROSSREF: crossref, CE.DATACITE: datacite, CE.OSTI: osti}


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
    doi_list: list[str],
    source: str,
    output_format_list: Optional[list[str]] = None,
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


# TODO: move to util file AND/OR convert to decorator
@validate_arguments
def import_dois_from_file(
    file: Union[Path, str],
) -> list[str]:
    return util.read_unique_lines(file)


def _check_for_missing_dois(
    doi_list: list[str],
    results_dict: dict,
) -> list[str]:
    """Check for DOIs that do not have data associated with them.

    :param doi_list: list of DOIs
    :type doi_list: list[str]
    :param results_dict: DOI data, indexed by DOI and then format
    :type results_dict: dict
    :return: list of DOIs without any associated data
    :rtype: list[str]
    """
    not_found = set()
    for doi in doi_list:
        if doi not in results_dict:
            # this should never happen!
            not_found.add(doi)
            print(f"{doi} is not in the results!")
            continue

        data_found = False
        for val in results_dict[doi].values():
            if val is not None:
                data_found = True
                break

        if not data_found:
            not_found.add(doi)

    return list(not_found)


def retrieve_doi_list_from_unknown(
    doi_list: list[str],
    output_format_list: Optional[list[str]] = None,
    save_files: bool = False,
    save_dir: Optional[Union[Path, str]] = None,
):

    print("Searching Crossref...")
    crossref_results = retrieve_doi_list(
        doi_list, CE.CROSSREF, output_format_list, save_files, save_dir
    )

    not_found = _check_for_missing_dois(doi_list, crossref_results[CE.DATA])
    n_found = len(doi_list) - len(not_found)
    print(f"Found {n_found} DOI{'' if n_found == 1 else 's'} at Crossref")

    if not not_found:
        return crossref_results

    print(f"Searching Datacite...")
    # now retry these DOIs at datacite
    datacite_results = retrieve_doi_list(
        not_found, CE.DATACITE, output_format_list, save_files, save_dir
    )

    still_not_found = _check_for_missing_dois(not_found, datacite_results[CE.DATA])
    n_now_found = len(not_found) - len(still_not_found)
    print(f"Found {n_now_found} DOI{'' if n_now_found == 1 else 's'} at Datacite")

    still_not_found.sort()

    # print out a warning about the dois that could not be located
    if still_not_found:
        print("The following DOIs could not be found:\n" + "\n".join(still_not_found))

    for key in crossref_results:
        crossref_results[key].update(datacite_results[key])
    return crossref_results
