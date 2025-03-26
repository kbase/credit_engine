"""NMDC - biosample retrieval by lat/long."""

from collections.abc import Generator
from typing import Any

from jsonpath_ng import jsonpath
import jsonpath_ng
from jsonpointer import JsonPointer, JsonPointerException, resolve_pointer, set_pointer

import dlt
from dlt.common.typing import TDataItem
from dlt.destinations import filesystem as fs_out
from dlt.extract.resource import DltResource
from dlt.extract.source import DltSource
from dlt.sources.helpers import requests
from dlt.sources.helpers.rest_client.client import RESTClient
from dlt.sources.helpers.rest_client.paginators import (
    JSONResponseCursorPaginator,
)
from dlt.sources.rest_api import rest_api_source
from dlt.sources.rest_api.typing import EndpointResource

# "mongo_filter_dict": {
#   "lat_lon.latitude": {
#     "$gt": 0
#   },
#   "lat_lon.longitude": {
#     "$gt": 0
#   }

NMDC_API_URL = "https://api.microbiomedata.org/"

ID_FIELDS = [
    "alternative_identifiers",
    "emsl_biosample_identifiers",
    "gold_biosample_identifiers",
    "igsn_biosample_identifiers",
    "img_identifiers",
    "insdc_biosample_identifiers",
    "neon_biosample_identifiers",
]

ENV_FIELDS = [
    "env_broad_scale",
    "env_local_scale",
    "env_medium",
    "env_package",
]

COORD_FIELDS = [
    "alt",  # altitude
    "depth",
    "elev",  # elevation
    "geo_loc_name",
    "lat_lon",
]

DATE_FIELDS = ["add_date", "collection_date", "mod_date"]

CORE_FIELDS = [
    "associated_studies",
    "description",
    "id",
    "name",
    "project_id",
    "samp_name",
    "type",
]

NMDC_FIELDS = ID_FIELDS + ENV_FIELDS + COORD_FIELDS + DATE_FIELDS + CORE_FIELDS

# endpoint configs
VALID_ENDPOINTS = ["biosamples", "studies"]
PER_PAGE = 500


def batch_endpoint_cfg(
    endpoint_name: str = "",
    filters: dict[str, Any] | None = None,
    fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate the config for a batch endpoint.

    :param endpoint_name: path to the endpoint, minus trailing slash
    :type endpoint_name: str
    :param filters: filter query param
    :type: dict[str, str]
    :param fields: fields query param
    :type: dict[str, str]
    :return: endpoint config
    :rtype: dict[str, Any]
    """
    if not endpoint_name or endpoint_name not in VALID_ENDPOINTS:
        err_msg = f"Invalid endpoint name: {endpoint_name}"
        raise ValueError(err_msg)

    params = {
        "per_page": PER_PAGE,
        "cursor": "*",
    }

    for f in [filters, fields]:
        if f:
            if not isinstance(f, dict):
                err_msg = f"invalid format for {f}"
                raise TypeError(err_msg)
            params.update(f)

    return {
        "name": endpoint_name,
        "endpoint": {
            "path": f"{endpoint_name}/",
            "data_selector": "results",
            "params": params,
            "paginator": JSONResponseCursorPaginator(
                cursor_param="cursor", cursor_path="meta.next_cursor"
            ),
        },
    }


def fields_param(field_list: list[str]) -> dict[str, str]:
    """Generate query parameters to specify the fields to be included in the response.

    :param field_list: list of fields to include
    :type field_list: list[str]
    :return: field query param
    :rtype: str
    """
    return {"fields": ",".join(field_list)}


def filter_param(filter_list: list[tuple[str, str | None, Any]]) -> dict[str, str]:
    """Generate query parameters to filter the results returned.

    e.g. [
        ("lat_lon.latitude", ">", 35.0),         # latitude > 35.0
        ("ecosystem_category", None, "Plants"),  # ecosystem_category is 'Plants'
        ("funding_sources.search", None, "NSF")  # funding_sources contains "NSF"
    ]

    Valid comparators (per `nmdc-runtime.api.endpoints.util.py`): "<", ">", ">=", "<="
    Omit the comparator (i.e. use None) for an exact match

    To search a field, `.search` should be appended to the field name, e.g. samp_name.search

    :param filters: tuple of field name, comparator or None, and value
    :type filters: list[tuple[str, str, str]]
    :return: filter query param
    :rtype: dict[str, str]
    """
    return {"filter": ",".join(f"{fltr[0]}:{fltr[1] or ''}{fltr[2]}" for fltr in filter_list)}


def nmdc_endpoint_src(config: dict[str, Any]) -> DltSource:
    """NMDC openapi endpoints.

    :return: DltSource for the endpoint
    :rtype: DltSource
    """
    return rest_api_source(
        {
            "client": {
                "base_url": NMDC_API_URL,
            },
            "resource_defaults": {"primary_key": "id"},
            "resources": [EndpointResource(**config)],
        }
    )


def nmdc_endpoint(config: dict[str, Any]) -> Generator[TDataItem, Any, None]:
    """NMDC openapi endpoints.

    :yield: REST API generator
    :rtype: Generator[TDataItem, Any, None]
    """
    yield from nmdc_endpoint_src(config)


def coord_query(lat: float, lon: float) -> list[tuple[str, str, float]]:
    return [
        ("lat_lon.latitude", ">=", lat - 0.1),
        ("lat_lon.latitude", "<=", lat + 0.1),
        ("lat_lon.longitude", ">=", lon - 0.1),
        ("lat_lon.longitude", "<=", lon + 0.1),
    ]


@dlt.transformer()
def nmdc_biosample(item: TDataItem, study_set: set[str]) -> TDataItem:
    """Transform sample data to fit the BER Common Data Model.

    :param item: biosample data structure
    :type item: TDataItem
    :param study_set: accumulator for study IDs
    :type study_set: set[str]
    :yield: transformed biosample data structure
    :rtype: Iterator[TDataItem]
    """
    pruned = {key: item[key] for key in item if key in CORE_FIELDS + DATE_FIELDS}

    # add in the lists
    for list_name in ["alt_ids", "alt_names"]:
        pruned[list_name] = []
    # and dictionaries
    for dict_name in ["env", "dates"]:
        pruned[dict_name] = {}

    remap = [
        ("/lat_lon", "/coordinates"),
        ("/alt", "/coordinates/altitude"),
        ("/elev", "/coordinates/elevation"),
        ("/depth", "/coordinates/depth"),
        ("/geo_loc_name", "/coordinates/geo_loc_name"),
        # env fields
        *[(f"/{field}/", f"/env/{field}") for field in ENV_FIELDS],
        *[(f"/{field}/", f"/dates/{field}") for field in DATE_FIELDS],
        ("/samp_name", "/alt_names/-"),
        *[
            (
                f"/{id_type}",
                "/alt_ids/-",
                lambda value, ptr: {
                    "id": value,
                    "description": f"{ptr.get_parts()[-1].replace('_', ' ').replace('identifiers', 'identifier')}",
                },
            )
            for id_type in item
            if id_type.endswith("_identifiers")
        ],
    ]

    for study in item.get("associated_studies", []):
        study_set.update(item.get("associated_studies", []))
        # save the sample to study mapping in a separate table
        yield dlt.mark.with_table_name(
            {"biosample_id": pruned["id"], "study_id": study}, "sample_to_study"
        )

    # copy over the fields to be remapped (if they exist)
    for remapping in remap:
        transform_item(item, pruned, remapping)

    yield pruned


def transform_item(source, destination, transform):
    jp = JsonPointer(transform[0])
    try:
        contents = jp.get(source)
    except (JsonPointerException, KeyError):
        return

    if not contents:
        return

    if len(transform) == 2:
        (_, mapped) = transform
        set_pointer(destination, mapped, contents)
        return

    if len(transform) == 3:
        (_, mapped, fn) = transform
        if isinstance(contents, list):
            for c in contents:
                set_pointer(destination, mapped, fn(c, jp))
        else:
            set_pointer(destination, mapped, fn(contents, jp))


@dlt.resource
def study_retriever(study_set: set[str]) -> Generator[TDataItem, Any, None]:
    """Fetch study data from the NMDC API.

    :param studies: set of study IDs to fetch
    :type studies: set[str]
    :yield: study data
    :rtype: Generator[TDataItem, Any, None]
    """
    for item in study_set:
        response = requests.get(f"{NMDC_API_URL}studies/{item}")
        yield response.json()


@dlt.transformer
def study_wrangler(study: TDataItem) -> TDataItem:
    base_obj = {
        "comment": None,
        "content_url": None,
        "contributors": [],
        "dates": [],
        "descriptions": [],
        "funding": [],
        "identifier": None,
        "license": None,
        "meta": {},
        "publisher": None,
        "related_identifiers": [],
        "resource_type": "dataset",
        "titles": [],
        "url": None,
        "version": None,
    }

    rel_map = {
        "award_doi": "is_financed_by",
        "dataset_doi": "is_published_in",
        "publication_doi": "is_referenced_by",
        "data_management_plan_doi": "is_related_material",
    }

    def resolve(curie: str) -> str:
        return f"https://something/{curie}"

    # value refers to the result returned by following the JSONpointer in the first tuple element
    # ptr is the jsonpointer object itself
    remap = [
        ("/id", "/identifier"),
        (
            "/description",
            "/descriptions/-",
            lambda value, ptr: {"description_text": value, "description_type": "description"},
        ),
        (
            "/alternative_descriptions",
            "/descriptions/-",
            lambda value, ptr: {"description_text": value, "description_type": "description"},
        ),
        ("/title", "/titles/-", lambda value, ptr: {"title": value}),
        # dedupe name, alternative_names and alternative_titles
        (
            "/name",
            "/titles/-",
            lambda value, ptr: {"title": value, "title_type": "alternative_title"},
        ),
        (
            "/alternative_names",
            "/titles/-",
            lambda value, ptr: {"title": value, "title_type": "alternative_title"},
        ),
        (
            "/alternative_titles",
            "/titles/-",
            lambda value, ptr: {"title": value, "title_type": "alternative_title"},
        ),
        # ask about principal investigator -- is info already in `has_credit_associations`?
        # (
        #     "/principal_investigator",
        #     "/contributors/-",
        #     lambda value, ptr: {
        #         "name": value["name"],
        #         "contributor_id": value["orcid"],
        #         "contributor_roles": ["principal investigator"],
        #         "contributor_type": "Person",
        #     },
        # ),
        (
            "/has_credit_associations",
            "/contributors/-",
            lambda value, ptr: {
                "name": resolve_pointer(value, "/applies_to_person/name"),
                "contributor_type": "Person",
                "contributor_roles": resolve_pointer(value, "/applied_roles"),
                # a bit dodgy!
                "contributor_id": resolve_pointer(value, "/applies_to_person/orcid", None),
            },
        ),
        # related IDs
        (
            "/part_of",
            "/related_identifiers/-",
            lambda value, ptr: {"id": value, "relationship_type": "is_part_of"},
        ),
        (
            "/associated_dois",
            "/related_identifiers/-",
            lambda value, ptr: {
                "id": resolve_pointer(value, "/doi_value"),
                "description": f"NMDC {str(resolve_pointer(value, '/doi_category')).replace('_', ' ')}",
                "relationship_type": rel_map[str(resolve_pointer(value, "/doi_category"))],
            },
        ),
        # alternative_identifiers:
        # emsl_project_identifiers:
        # gnps_task_identifiers:
        # gold_study_identifiers:
        # insdc_bioproject_identifiers:
        # jgi_portal_study_identifiers:
        # mgnify_project_identifiers:
        # neon_study_identifiers:
        # related_identifiers:
        # identifiers: copy field name to description
        # relationship type??
        *[
            (
                f"/{id_type}",
                "/related_identifiers/-",
                lambda value, ptr: {
                    "id": value,
                    "description": f"{ptr.get_parts()[-1].replace('_', ' ').replace('identifiers', 'identifier')}",
                },
            )
            for id_type in study
            if id_type.endswith("_identifiers")
        ],
        # relationship type?
        ("/id", "/url", lambda value, ptr: f"{resolve(value)}"),
    ]

    # info still required: license, date/version
    # funding_sources: - we need funder org/org id; grant id; grant title; grant URL
    # protocol_link: {url: ..., type: ..., name: ...}

    # copy over the fields to be remapped (if they exist)
    for remapping in remap:
        transform_item(study, base_obj, remapping)

    yield dlt.mark.with_table_name(base_obj, "converted")

    yield base_obj


def retrieve_studies(study_set: set[str]) -> None:
    study_pipeline = dlt.pipeline(
        pipeline_name="nmdc_studies",
        destination=fs_out(bucket_url="output/nmdc/no_tables"),
        dataset_name="study",
    )

    study_retriever.max_table_nesting = 0
    study_wrangler.max_table_nesting = 0

    load_info = study_pipeline.run(
        study_retriever(study_set) | study_wrangler,
        table_name="downloaded_studies",
        # table_format="delta",
    )

    print(load_info)


def retrieve_samples():
    # collect biosamples, reformatting the data as we go.
    pipeline = dlt.pipeline(
        pipeline_name="pipe_samples",
        destination=fs_out(bucket_url="output/nmdc/no_tables"),
        dataset_name="samples_data",
    )
    filters = filter_param([("lat_lon.latitude", ">", 60.0)])
    samples_cfg = batch_endpoint_cfg("biosamples", filters=filters)
    samples_gen = nmdc_endpoint(samples_cfg)

    nmdc_biosample.max_table_nesting = 0

    # collect the sample IDs mentioned in a set
    study_set = set()
    load_info = pipeline.run(
        samples_gen | nmdc_biosample(study_set).with_name("cdm_samples"),
        # table_format="delta",
    )
    print(study_set)

    retrieve_studies(study_set)


if __name__ == "__main__":
    study_set = {
        "nmdc:sty-11-hht5sb92",
        "nmdc:sty-11-34xj1150",
        "nmdc:sty-11-8xdqsn54",
        "nmdc:sty-11-5tgfr349",
        "nmdc:sty-11-547rwq94",
        "nmdc:sty-11-db67n062",
        "nmdc:sty-11-pzmd0x14",
    }
    # retrieve_samples()
    retrieve_studies(study_set)
