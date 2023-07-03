import types
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import quote

import requests
from pydantic import validate_arguments

from credit_engine import constants as CE
from credit_engine import util
from credit_engine.clients import crossref, datacite, osti
from credit_engine.errors import make_error

SOURCE_TO_CLIENT = {CE.CROSSREF: crossref, CE.DATACITE: datacite, CE.OSTI: osti}


@validate_arguments
def check_doi_source(doi: CE.TrimmedString) -> Optional[str]:
    """
    Check whether a DOI is accessible via CrossRef.

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
    doi_file: Optional[Path | str],
    doi_list: Optional[list[str]],  # set[str]],
    input_errors: list[str],
) -> set[str]:
    """
    Merge and validate the input DOIs.

    :param doi_file: file containing DOIs to be fetched
    :type doi_file: Optional[str]
    :param doi_list: list of DOIs to fetch
    :type doi_list: Optional[list[str]]
    :param input_errors: list of param validation errors
    :type input_errors: list[str]
    :return: unique DOIs to be fetched
    :rtype: set[str]
    """

    proto_doi_list: set[str] = set()

    if doi_file:
        try:
            file_lines = util.read_unique_lines(doi_file)
            if file_lines:
                proto_doi_list = file_lines
        except OSError as e:
            input_errors.append(str(e))

    if doi_list is not None:
        try:
            cleaned_list = util.trim_dedupe_list(doi_list)
            proto_doi_list = proto_doi_list | cleaned_list
        except Exception as e:
            input_errors.append(str(e))

    return proto_doi_list


@validate_arguments(config={"arbitrary_types_allowed": True})
def _validate_output_formats(
    client: types.ModuleType,
    output_formats: Optional[set[str]],
    input_errors: list[str],
) -> tuple[set[CE.OutputFormat], list[str]]:
    """Validate the output formats requested

    :param client: client object
    :type client: object
    :param output_formats: output formats to fetch
    :type output_formats: Optional[set[str]]
    :param input_errors: list of param validation errors
    :type input_errors: list[str]
    :return: validated output format list
    :rtype: tuple[set[CE.OutputFormat], list[str]]
    """
    valid_output_formats = set()
    invalid_formats = set()
    if output_formats:
        for fmt in output_formats:
            output_format = None

            if not isinstance(fmt, CE.OutputFormat):
                try:
                    # check whether it's in the enum
                    output_format = CE.OutputFormat[fmt.upper()]
                except KeyError:
                    invalid_formats.add(fmt)
                    continue
            else:
                output_format = fmt

            if output_format in client.VALID_OUTPUT_FORMATS:
                valid_output_formats.add(output_format)
            else:
                invalid_formats.add(fmt)

        if invalid_formats:
            for fmt in invalid_formats:
                input_errors.append(
                    make_error(
                        "invalid_param",
                        {"param": CE.OUTPUT_FORMAT, CE.OUTPUT_FORMAT: fmt},
                    )
                )
    else:
        valid_output_formats.add(client.DEFAULT_FORMAT)

    return (valid_output_formats, input_errors)


def _validate_save_dir(
    save_dir: Optional[Union[Path, str]],
    client: Optional[types.ModuleType],
    input_errors: list[str],
) -> Optional[Path]:
    """
    Validate save-related parameters.

    :param save_dir: directory in which to save files
    :type save_dir: Optional[Union[Path, str]]
    :param client: client object (if it exists)
    :type client: Optional[types.ModuleType]
    :param input_errors: list of param validation errors
    :type input_errors: list[str]
    :return: validated path to the save dir or None
    :rtype: Optional[Path]
    """
    if client and not save_dir:
        save_dir = client.SAMPLE_DATA_DIR

    if save_dir is None:
        input_errors.append("No save_dir specified")
        return None

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
    doi_file: Optional[Path | str] = None,
    doi_list: Optional[list[str]] = None,
    output_formats: Optional[set[str]] = None,
    save_files: bool = False,
    save_dir: Optional[Path | str] = None,
    input_errors: Optional[list[str]] = None,
    **kwargs,
) -> tuple[dict, types.ModuleType]:
    """
    Validate the input to retrieve_doi_list.

    :param doi_list: list of DOIs to retrieve
    :type doi_list: list[str], optional
    :param doi_file: (text) file containing a list of DOIs to retrieve
    :type doi_file: Path or string, optional
    :param source: DOI source (e.g. DataCite, CrossRef)
    :type source: str
    :param output_formats: formats to retrieve the DOIs in, defaults to None
    :type output_formats: Optional[set[str]], optional
    :param save_files: whether or not to save the files, defaults to False
    :type save_files: bool, optional
    :param save_dir: path to the save directory, defaults to None
    :type save_dir: Optional[Path | str], optional
    :raises ValueError: if there are any input parameter errors
    :return: tuple containing a dict of validated params and the client module
    :rtype: tuple
    """
    if not input_errors:
        input_errors = []

    params: dict[str, Any] = {
        "save_files": save_files,
    }
    client: Optional[types.ModuleType] = None

    params["doi_list"] = _validate_dois(
        doi_file=doi_file, doi_list=doi_list, input_errors=input_errors
    )

    if source not in SOURCE_TO_CLIENT:
        input_errors.append(
            make_error(
                "invalid_param", {"param": CE.DATA_SOURCE, CE.DATA_SOURCE: source}
            )
        )
    else:
        params["source"] = source
        client = SOURCE_TO_CLIENT[source]

        # only validate the output formats if there is a valid client
        (params["output_formats"], input_errors) = _validate_output_formats(
            client, output_formats, input_errors
        )

    # set up the save_dir (if appropriate)
    if save_files:
        params["save_dir"] = _validate_save_dir(save_dir, client, input_errors)

    if input_errors:
        die_with_errors(input_errors)

    # keep type checker happy
    if client is not None:
        return (params, client)


def retrieve_doi_list(**kwargs) -> dict:
    """
    Retrieve a list of DOIs.

    See _validate_retrieve_doi_list_input for specification of kwargs.

    :return: dictionary of results in the format:
        data: return data keyed by DOI and format
        files: path to the saved data files, keyed by DOI and format [Optional]
    :rtype: dict
    """

    (params, client) = _validate_retrieve_doi_list_input(**kwargs)

    results = {
        CE.DATA: {},
    }
    file_ext_mapping = {}
    if params["save_files"]:
        results[CE.FILES] = {}
        # make a local mapping of file extensions
        for fmt in params["output_formats"]:
            file_ext_mapping[fmt] = util.get_extension(fmt)

    for doi in params["doi_list"]:
        results[CE.DATA][doi] = client.retrieve_doi(
            doi, output_formats=params["output_formats"]
        )
        if not params["save_files"]:
            continue

        if doi not in results[CE.FILES]:
            results[CE.FILES][doi] = {}
        for fmt in params["output_formats"]:
            if results[CE.DATA][doi][fmt] is None:
                results[CE.FILES][doi][fmt] = None
                continue
            # otherwise, save to file
            results_file = util.save_data_to_file(
                file_name=doi,
                save_dir=params["save_dir"],
                suffix=file_ext_mapping[fmt],
                data=results[CE.DATA][doi][fmt],
            )
            if results_file:
                results[CE.FILES][doi][fmt] = results_file

    return results


def _check_for_missing_dois(
    dois: set[str],
    results_dict: dict,
) -> set[str]:
    """Check for DOIs that do not have data associated with them.

    :param dois: DOIs to check
    :type dois: set[str]
    :param results_dict: DOI data, indexed by DOI and then format
    :type results_dict: dict
    :return: DOIs without any associated data
    :rtype: set[str]
    """
    not_found = set()
    for doi in dois:
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

    return not_found


@validate_arguments
def retrieve_doi_list_from_unknown(
    doi_file: Optional[str] = None,
    doi_list: Optional[list[str]] = None,
    output_formats: Optional[set[str]] = None,
    save_files: bool = False,
    save_dir: Optional[Path | str] = None,
    **kwargs,
) -> dict[str, Any]:
    """
    Retrieve a list of DOIs of unknown origin.

    :param doi_file: file containing a list of DOIs to retrieve, defaults to None
    :type doi_file: Optional[str], optional
    :param doi_list: list of DOIs to retrieve, defaults to None
    :type doi_list: Optional[list[str]], optional
    :param output_formats: formats to request data in, defaults to None
    :type output_formats: Optional[set[str]], optional
    :param save_files: whether or not to save files, defaults to False
    :type save_files: bool, optional
    :param save_dir: directory location for saving files, defaults to None
    :type save_dir: Optional[Path | str], optional
    :return: data structure of fetched DOIs keyed by DOI and then format
    :rtype: dict[str, Any]
    """

    input_errors = []
    all_dois: set[str] = _validate_dois(
        doi_file=doi_file, doi_list=doi_list, input_errors=input_errors
    )
    if input_errors:
        die_with_errors(input_errors)

    print("Searching Crossref...")

    # FIXME: output formats need to be converted into CE.OutputFormat.* first
    if output_formats:
        valid_crossref_formats = output_formats.intersection(
            SOURCE_TO_CLIENT[CE.CROSSREF].VALID_OUTPUT_FORMATS
        )
    else:
        valid_crossref_formats = {SOURCE_TO_CLIENT[CE.CROSSREF].DEFAULT_FORMAT}

    crossref_results = retrieve_doi_list(
        doi_list=list(all_dois),
        source=CE.CROSSREF,
        output_formats=valid_crossref_formats,
        save_files=save_files,
        save_dir=save_dir,
    )

    not_found: set[str] = _check_for_missing_dois(all_dois, crossref_results[CE.DATA])
    n_found = len(all_dois) - len(not_found)
    print(f"Found {n_found} DOI{'' if n_found == 1 else 's'} at Crossref")

    if not not_found:
        return crossref_results

    print("Searching Datacite...")
    # now retry these DOIs at datacite
    if output_formats:
        valid_datacite_formats = output_formats.intersection(
            SOURCE_TO_CLIENT[CE.DATACITE].VALID_OUTPUT_FORMATS
        )
    else:
        valid_datacite_formats = {SOURCE_TO_CLIENT[CE.DATACITE].DEFAULT_FORMAT}
    datacite_results = retrieve_doi_list(
        doi_list=list(not_found),
        source=CE.DATACITE,
        output_formats=valid_datacite_formats,
        save_files=save_files,
        save_dir=save_dir,
    )

    still_not_found: set[str] = _check_for_missing_dois(
        not_found, datacite_results[CE.DATA]
    )
    n_now_found = len(not_found) - len(still_not_found)
    print(f"Found {n_now_found} DOI{'' if n_now_found == 1 else 's'} at Datacite")

    # print out a warning about the dois that could not be located
    if still_not_found:
        sorted_still_not_found = list(still_not_found)
        sorted_still_not_found.sort()
        print(
            "The following DOIs could not be found:\n"
            + "\n".join(sorted_still_not_found)
        )

    for key in crossref_results:
        crossref_results[key].update(datacite_results[key])
    return crossref_results
