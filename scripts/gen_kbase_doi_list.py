"""DataCite client.

access to the DataCite DOI endpoint does not require authentication

API documentation: https://support.datacite.org/docs/api
"""

import datetime as dt
from collections.abc import Generator
from io import StringIO, TextIOWrapper
from pathlib import Path
from typing import Any, TextIO

import dlt
from dlt.common.typing import TDataItem
from dlt.destinations import filesystem as fs_out
from dlt.sources.rest_api import rest_api_source


def has_required_keys(item: dict, required_keys: list) -> bool:
    """Ensure that a dictionary has all required keys populated.

    :param item: dictionary to check
    :type item: dict
    :param required_keys: list of keys to check
    :type required_keys: list
    :return: True or False
    :rtype: bool
    """
    return all(item.get(key) for key in required_keys)


def datacite_prefix_endpoint(prefix: str) -> Generator[TDataItem, Any]:
    """DataCite DOI endpoint for fetching DOIs by prefix.

    :param doi: prefix to retrieve
    :type doi: str
    :yield: REST API generator
    :rtype: Generator[TDataItem, Any, None]
    """
    yield from rest_api_source(
        {
            "client": {"base_url": "https://api.datacite.org/"},
            "resource_defaults": {"primary_key": "doi"},
            "resources": [
                {
                    "name": "doi_prefix_match",
                    "endpoint": {
                        "path": "dois",
                        "data_selector": "data[*].attributes",
                        "params": {"prefix": prefix, "sort": "-created", "affiliation": "true", "publisher": "true"},
                    },
                },
            ],
        }
    )


@dlt.transformer()
def extract_citation_data(item: dict[str, Any], fh: TextIO | TextIOWrapper) -> dict[str, Any]:
    """Extract useful citation data from the item.

    :param item: citation data object from the datacite API.
    :type item: dict[str, Any]
    :return: cut-down citation data
    :rtype: dict[str, Any]
    """
    item["contributors"] = item["creators"] + item["contributors"]
    for con in item["contributors"]:
        if has_required_keys(con, ["familyName", "givenName"]):
            con["citable"] = con.get("familyName") + " " + con.get("givenName")[:1]
        else:
            con["citable"] = con.get("name")

        if con.get("nameIdentifiers"):
            for name_id in con.get("nameIdentifiers"):
                if name_id.get("nameIdentifierScheme") == "ORCID":
                    # remove the full URL, replace with 'ORCID:'
                    con["orcid"] = name_id.get("nameIdentifier").replace("https://orcid.org/", "ORCID:")
                    break

    if fh and has_required_keys(item, ["doi", "titles", "contributors", "publicationYear", "updated"]):
        print_row(fh, item)
    else:
        print(f"ERROR: doi:{item.get('doi', 'UNKNOWN')} is missing required fields")

    return item


def print_row(fh: TextIO | TextIOWrapper, item: dict[str, Any]) -> None:
    """Print out DOI info to a file.

    :param fh: file handle to print to
    :type fh: TextIO | TextIOWrapper
    :param item: doi information in dictionary form
    :type item: dict[str, Any]
    """
    author_string = ", ".join(con.get("citable") for con in item.get("contributors", []))

    fh.write(
        f"| {item.get('doi')} | [{item.get('titles', {})[0]['title']}](https://dx.doi.org/{item.get('doi')})<br>{author_string} | {item.get('publicationYear')} | {item.get('updated')} |\n",
    )


def has_doi_changes(existing_content: str, new_content: str) -> bool:
    """Compare existing and new markdown content, ignoring the 'Generated on' line.

    :param existing_content: current file content
    :type existing_content: str
    :param new_content: newly generated content
    :type new_content: str
    :return: True if content differs outside the 'Generated on' line
    :rtype: bool
    """
    existing_lines = [line for line in existing_content.splitlines() if not line.startswith("Generated on ")]
    new_lines = [line for line in new_content.splitlines() if not line.startswith("Generated on ")]
    return existing_lines != new_lines


def run_doi_update_pipeline(output_file: str) -> None:
    """Run the pipeline to update the KBase DOI list.

    :param output_file: file to save the DOI info to.
    :type  output_file: str
    """
    current_date = dt.datetime.now(tz=dt.UTC).date().isoformat()
    buf = StringIO()
    buf.write("# KBase FAIR Narratives\n")
    buf.write(f"Generated on {current_date}\n\n")
    buf.write("| DOI | Title, Authors | Published | Updated |\n|-----|----------------|-----------|---------|\n")

    # Create the pipeline
    pipeline = dlt.pipeline(
        pipeline_name="datacite_search_pipeline",
        destination=fs_out(bucket_url="./out"),
        dataset_name="datacite",
    )
    extract_citation_data.bind(fh=buf)
    # Run the pipeline
    load_info = pipeline.run(
        datacite_prefix_endpoint("10.25982") | extract_citation_data,
    )
    print(load_info)

    new_content = buf.getvalue()
    output_path = Path(output_file)
    if output_path.exists() and not has_doi_changes(output_path.read_text(encoding="utf-8"), new_content):
        print(f"No DOI changes detected in {output_file}; skipping file update.")
        return

    output_path.write_text(new_content, encoding="utf-8")
    print(f"Updated {output_file}.")


if __name__ == "__main__":
    run_doi_update_pipeline("src/docs/pages/kbase_dois.md")
