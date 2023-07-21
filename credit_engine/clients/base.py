"""Base functionality for any client retrieving data from a data source."""
import types
from enum import Enum
from typing import Any

from pydantic import validate_arguments

from credit_engine import constants as CE  # noqa: N812
from credit_engine import util
from credit_engine.clients import crossref, datacite, osti, osti_elink
from credit_engine.clients.args import GenericClientArgs

SOURCE_TO_CLIENT = {CE.CROSSREF: crossref, CE.DATACITE: datacite, CE.OSTI: osti}


class SourceToClient(Enum):
    """Class representing the various data sources."""

    CROSSREF = crossref
    DATACITE = datacite
    OSTI = osti
    OSTI_ELINK = osti_elink


def die_with_errors(error_list: list[str]):
    """Die with the appropriate panache and list of errors.

    :param error_list: list of errors
    :type error_list: list[str]
    :raises ValueError: plus a generic line about trying again
    """
    if error_list:
        error_list.append("Please check the above errors and try again.")
        raise ValueError("\n".join(error_list))


def _validate_retrieve_dois(
    **kwargs,
) -> tuple[GenericClientArgs, types.ModuleType]:
    """Validate the input to retrieve_dois.

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
    if "source" not in kwargs:
        raise ValueError("Missing required parameter: source")

    source = kwargs["source"]
    del kwargs["source"]
    src = None
    if not isinstance(source, SourceToClient):
        try:
            src = SourceToClient[source.strip().upper()]
        except (AttributeError, KeyError) as e:
            raise ValueError(f"Invalid data source: {source!r}") from e
    else:
        src = source

    client: types.ModuleType = src.value

    params: GenericClientArgs = client.ClientArgs(
        source=src,
        **kwargs,
    )
    return (params, client)


def retrieve_dois(**kwargs) -> dict:
    """Retrieve a list of DOIs.

    See _validate_retrieve_dois for specification of kwargs.

    :return: dictionary of results in the format:
        data: return data keyed by DOI and format
        files: path to the saved data files, keyed by DOI and format [Optional]
    :rtype: dict
    """
    if "params" not in kwargs and "client" not in kwargs:
        (params, client) = _validate_retrieve_dois(**kwargs)
    else:
        params = kwargs["params"]
        client = kwargs["client"]

    results = {
        CE.DATA: {},
    }
    file_ext_mapping = {}
    if params.save_files:
        results[CE.FILES] = {}
        # make a local mapping of file extensions
        for output_format in params.output_formats:
            file_ext_mapping[output_format.value] = util.get_extension(output_format)

    for doi in params.dois:
        results[CE.DATA][doi] = client.retrieve_doi(params, doi=doi)
        if not params.save_files:
            continue

        if doi not in results[CE.FILES]:
            results[CE.FILES][doi] = {}
        for output_format in params.output_formats:
            fmt = output_format.value
            if results[CE.DATA][doi][fmt] is None:
                results[CE.FILES][doi][fmt] = None
                continue
            # otherwise, save to file
            results_file = util.save_data_to_file(
                file_name=doi,
                save_dir=params.save_dir,
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
def retrieve_dois_from_unknown(
    **kwargs,
) -> dict[str, Any]:
    """Retrieve a list of DOIs of unknown origin.

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
    (params, client) = _validate_retrieve_dois(**kwargs, source=CE.CROSSREF)
    all_dois = params.dois
    for doi_src in ["doi_file", "doi_list"]:
        if doi_src in kwargs:
            del kwargs[doi_src]

    print("Searching Crossref...")

    crossref_results = retrieve_dois(params=params, client=client)

    not_found: set[str] = _check_for_missing_dois(all_dois, crossref_results[CE.DATA])
    n_found = len(all_dois) - len(not_found)
    print(f"Found {n_found} DOI{'' if n_found == 1 else 's'} at Crossref")

    if not not_found:
        return crossref_results

    print("Searching DataCite...")
    datacite_results = retrieve_dois(
        **kwargs,
        doi_list=not_found,
        source=CE.DATACITE,
    )

    still_not_found: set[str] = _check_for_missing_dois(
        not_found, datacite_results[CE.DATA]
    )
    n_now_found = len(not_found) - len(still_not_found)
    print(f"Found {n_now_found} DOI{'' if n_now_found == 1 else 's'} at DataCite")

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
