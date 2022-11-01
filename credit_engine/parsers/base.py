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


def die_with_errors(error_list: list[str]):
    """Die with the appropriate panache and list of errors.

    :param error_list: list of errors
    :type error_list: list[str]
    :raises ValueError: plus a generic line about trying again
    """
    if error_list:
        error_list.append("Please check the above errors and try again.")
        raise ValueError("\n".join(error_list))


def _validate_dois(
    doi_file: Optional[str],
    doi_list: Optional[list[str]],
    input_errors: list[str],
) -> list[str]:
    """Merge and validate the input DOIs.

    :param doi_file: file containing DOIs to be fetched
    :type doi_file: Optional[str]
    :param doi_list: list of DOIs to fetch
    :type doi_list: Optional[list[str]]
    :param input_errors: list of param validation errors
    :type input_errors: list[str]
    :return: unique DOIs to be fetched
    :rtype: list[str]
    """

    proto_doi_list: list[str] = []

    if doi_file:
        try:
            file_lines = util.read_unique_lines(doi_file)
            if file_lines:
                proto_doi_list = util.clean_doi_list(file_lines)
            print({"proto doi list from file": proto_doi_list})
        except OSError as e:
            input_errors.append(str(e))

    if doi_list:  # and isinstance(doi_list, list):
        try:
            cleaned_list = util.clean_doi_list(doi_list)
            proto_doi_list = proto_doi_list + cleaned_list
        except Exception as e:
            print(e)
            input_errors.append(str(e))

    return list(set(proto_doi_list))


def _validate_output_format_list(
    output_format_list: Optional[list[str]], source: str, input_errors: list[str]
) -> list[str]:
    """Validate the output formats requested

    :param output_format_list: list of output formats to fetch
    :type output_format_list: Optional[list[str]]
    :param source: data source
    :type source: str
    :param input_errors: list of param validation errors
    :type input_errors: list[str]
    :return: validated output format list
    :rtype: list[str]
    """
    parser = SOURCE_TO_PARSER[source]
    if output_format_list:
        output_format_list = list(set(output_format_list))
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
        output_format_list = [parser.DEFAULT_FORMAT]

    return output_format_list


def _validate_save_dir(
    save_dir: Optional[Union[Path, str]],
    parser: Optional[types.ModuleType],
    input_errors: list[str],
) -> Union[Path, None]:
    """Validate save-related parameters

    :param save_dir: directory in which to save files
    :type save_dir: Optional[Union[Path, str]]
    :param parser: parser object (if it exists)
    :type parser: Optional[types.ModuleType]
    :param input_errors: list of param validation errors
    :type input_errors: list[str]
    :return: validated path to the save dir or None
    :rtype: Union[Path, None]
    """
    if not save_dir:
        if not parser:
            input_errors.append("No save_dir specified")
            return None
        else:
            save_dir = parser.SAMPLE_DATA_DIR

    save_dir_path = util.full_path(save_dir)

    if not save_dir_path.exists() or not save_dir_path.is_dir():
        input_errors.append(
            make_error(
                "invalid_param",
                {
                    "param": "save_dir",
                    "save_dir": f"'{save_dir}' does not exist or is not a directory",
                },
            )
        )
        return None

    return save_dir_path


@validate_arguments
def _validate_retrieve_doi_list_input(
    source: CE.TrimmedString,
    doi_file: Optional[str] = None,
    doi_list: Optional[list[str]] = None,
    output_format_list: Optional[list[str]] = None,
    save_files: bool = False,
    save_dir: Optional[Union[Path, str]] = None,
    input_errors: Optional[list[str]] = None,
) -> tuple[dict, types.ModuleType]:
    """Validate the input to retrieve_doi_list.

    :param doi_list: list of DOIs to retrieve
    :type doi_list: list[str], optional
    :param doi_file: (text) file containing a list of DOIs to retrieve
    :type doi_file: Path or string, optional
    :param source: DOI source (e.g. DataCite, CrossRef)
    :type source: str
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
    if not input_errors:
        input_errors = []

    params: dict[str, Any] = {
        "save_files": save_files,
    }
    parser: Optional[types.ModuleType] = None

    params["doi_list"] = _validate_dois(
        doi_file=doi_file, doi_list=doi_list, input_errors=input_errors
    )

    if source not in SOURCE_TO_PARSER:
        input_errors.append(
            make_error(
                "invalid_param", {"param": CE.DATA_SOURCE, CE.DATA_SOURCE: source}
            )
        )
    else:
        params["source"] = source
        parser = SOURCE_TO_PARSER[source]

        # only validate the output formats if there is a valid source
        params["output_format_list"] = _validate_output_format_list(
            output_format_list, source, input_errors
        )

    # set up the save_dir (if appropriate)
    if save_files:
        params["save_dir"] = _validate_save_dir(save_dir, parser, input_errors)

    if input_errors:
        die_with_errors(input_errors)

    # keep type checker happy
    if parser is not None:
        return (params, parser)


def retrieve_doi_list(**kwargs) -> dict:
    """Retrieve a list of DOIs.

    See _validate_retrieve_doi_list_input for specification of kwargs.

    :return: dictionary of results in the format:
        data: return data keyed by DOI and format
        files: path to the saved data files, keyed by DOI and format [Optional]
    :rtype: dict
    """

    (params, parser) = _validate_retrieve_doi_list_input(**kwargs)

    results = {
        CE.DATA: {},
    }

    if params["save_files"]:
        results[CE.FILES] = {}

    for doi in params["doi_list"]:
        results[CE.DATA][doi] = parser.retrieve_doi(
            doi, output_format_list=params["output_format_list"]
        )
        if not params["save_files"]:
            continue

        if doi not in results[CE.FILES]:
            results[CE.FILES][doi] = {}
        for fmt in params["output_format_list"]:
            if results[CE.DATA][doi][fmt] is None:
                results[CE.FILES][doi][fmt] = None
                continue
            # otherwise, save to file
            results_file = util.save_data_to_file(
                doi=doi,
                save_dir=params["save_dir"],
                suffix=get_extension(params["source"], fmt),
                data=results[CE.DATA][doi][fmt],
            )
            if results_file:
                results[CE.FILES][doi][fmt] = results_file

    return results


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


@validate_arguments
def retrieve_doi_list_from_unknown(
    doi_file: Optional[str] = None,
    doi_list: Optional[list[str]] = None,
    output_format_list: Optional[list[str]] = None,
    save_files: bool = False,
    save_dir: Optional[Union[Path, str]] = None,
) -> dict[str, Any]:
    """Retrieve a list of DOIs of unknown origin

    :param doi_file: file containing a list of DOIs to retrieve, defaults to None
    :type doi_file: Optional[str], optional
    :param doi_list: list of DOIs to retrieve, defaults to None
    :type doi_list: Optional[list[str]], optional
    :param output_format_list: list of formats to request data in, defaults to None
    :type output_format_list: Optional[list[str]], optional
    :param save_files: whether or not to save files, defaults to False
    :type save_files: bool, optional
    :param save_dir: directory location for saving files, defaults to None
    :type save_dir: Optional[Union[Path, str]], optional
    :return: data structure of fetched DOIs keyed by DOI and then format
    :rtype: dict[str, Any]
    """

    input_errors = []
    all_doi_list = _validate_dois(
        doi_file=doi_file, doi_list=doi_list, input_errors=input_errors
    )
    if input_errors:
        die_with_errors(input_errors)

    print("Searching Crossref...")

    if output_format_list:
        valid_crossref_formats = list(
            set(output_format_list).intersection(
                set(SOURCE_TO_PARSER[CE.CROSSREF].FILE_EXTENSIONS.keys())
            )
        )
    else:
        valid_crossref_formats = [SOURCE_TO_PARSER[CE.CROSSREF].DEFAULT_FORMAT]

    crossref_results = retrieve_doi_list(
        doi_list=all_doi_list,
        source=CE.CROSSREF,
        output_format_list=valid_crossref_formats,
        save_files=save_files,
        save_dir=save_dir,
    )

    not_found = _check_for_missing_dois(all_doi_list, crossref_results[CE.DATA])
    n_found = len(all_doi_list) - len(not_found)
    print(f"Found {n_found} DOI{'' if n_found == 1 else 's'} at Crossref")

    if not not_found:
        return crossref_results

    print(f"Searching Datacite...")
    # now retry these DOIs at datacite
    if output_format_list:
        valid_datacite_formats = list(
            set(output_format_list).intersection(
                set(SOURCE_TO_PARSER[CE.DATACITE].FILE_EXTENSIONS.keys())
            )
        )
    else:
        valid_datacite_formats = [SOURCE_TO_PARSER[CE.DATACITE].DEFAULT_FORMAT]
    datacite_results = retrieve_doi_list(
        doi_list=not_found,
        source=CE.DATACITE,
        output_format_list=valid_datacite_formats,
        save_files=save_files,
        save_dir=save_dir,
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