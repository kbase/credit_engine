from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

metamodel_version = "None"
version = "0.0.6"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    pass


class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key: str):
        return getattr(self.root, key)

    def __getitem__(self, key: str):
        return self.root[key]

    def __setitem__(self, key: str, value):
        self.root[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta(
    {
        "default_curi_maps": ["semweb_context"],
        "default_prefix": "dcm",
        "default_range": "string",
        "description": "Schema for dataset credit metadata.",
        "id": "https://github.com/kbase/credit_engine/schema/dcm/linkml/credit_metadata",
        "imports": ["components", "linkml:types"],
        "name": "credit_metadata",
        "prefixes": {
            "Crossref": {"prefix_prefix": "Crossref", "prefix_reference": "https://crossref.org/"},
            "DOI": {"prefix_prefix": "DOI", "prefix_reference": "http://identifiers.org/doi/"},
            "DataCite": {
                "prefix_prefix": "DataCite",
                "prefix_reference": "https://purl.org/datacite/v4.4/",
            },
            "JGI": {"prefix_prefix": "JGI", "prefix_reference": "https://data.jgi.doe.gov/search/"},
            "ORCID": {
                "prefix_prefix": "ORCID",
                "prefix_reference": "http://identifiers.org/orcid/",
            },
            "OSTI.ARTICLE": {
                "prefix_prefix": "OSTI.ARTICLE",
                "prefix_reference": "https://www.osti.gov/biblio/",
            },
            "biolink": {
                "prefix_prefix": "biolink",
                "prefix_reference": "https://w3id.org/biolink/vocab/",
            },
            "dcm": {
                "prefix_prefix": "dcm",
                "prefix_reference": "https://kbase.github.io/credit_engine/",
            },
            "linkml": {"prefix_prefix": "linkml", "prefix_reference": "https://w3id.org/linkml/"},
            "nmdc": {"prefix_prefix": "nmdc", "prefix_reference": "https://w3id.org/nmdc/"},
            "schema": {"prefix_prefix": "schema", "prefix_reference": "http://schema.org/"},
        },
        "source_file": "schema/dcm/linkml/credit_metadata.yaml",
    }
)


class ContributorRole(str, Enum):
    """
    The type of contribution made by a contributor.
    """

    """Person with knowledge of how to access, troubleshoot, or otherwise field issues related to the resource. May also be "Point of Contact" in organisation that controls access to the resource, if that organisation is different from Publisher, Distributor, Data Manager."""
    contact_person = "contact_person"
    """Person/institution responsible for finding, gathering/collecting data under the guidelines of the author(s) or Principal Investigator (PI). May also use when crediting survey conductors, interviewers, event or condition observers, person responsible for monitoring key instrument data."""
    data_collector = "data_collector"
    """Person tasked with reviewing, enhancing, cleaning, or standardizing metadata and the associated data submitted for storage, use, and maintenance within a data centre or repository. While the "DataManager" is concerned with digital maintenance, the DataCurator's role encompasses quality assurance focused on content and metadata. This includes checking whether the submitted dataset is complete, with all files and components as described by submitter, whether the metadata is standardized to appropriate systems and schema, whether specialized metadata is needed to add value and ensure access across disciplines, and determining how the metadata might map to search engines, database products, and automated feeds."""
    data_curator = "data_curator"
    """Person (or organisation with a staff of data managers, such as a data centre) responsible for maintaining the finished resource. The work done by this person or organisation ensures that the resource is periodically "refreshed" in terms of software/hardware support, is kept available or is protected from unauthorized access, is stored in accordance with industry standards, and is handled in accordance with the records management requirements applicable to it."""
    data_manager = "data_manager"
    """Institution tasked with responsibility to generate/disseminate copies of the resource in either electronic or print form. Works stored in more than one archive/repository may credit each as a distributor."""
    distributor = "distributor"
    """A person who oversees the details related to the publication format of the resource. N.b. if the Editor is to be credited in place of multiple creators, the Editor's name may be supplied as Creator, with "(Ed.)" appended to the name."""
    editor = "editor"
    """Typically, the organisation allowing the resource to be available on the internet through the provision of its hardware/software/operating support. May also be used for an organisation that stores the data offline. Often a data centre (if that data centre is not the "publisher" of the resource)."""
    hosting_institution = "hosting_institution"
    """Typically a person or organisation responsible for the artistry and form of a media product. In the data industry, this may be a company "producing" DVDs that package data for future dissemination by a distributor."""
    producer = "producer"
    """Person officially designated as head of project team or sub- project team instrumental in the work necessary to development of the resource. The Project Leader is not "removed" from the work that resulted in the resource; he or she remains intimately involved throughout the life of the particular project team."""
    project_leader = "project_leader"
    """Person officially designated as manager of a project. Project may consist of one or many project teams and sub-teams. The manager of a project normally has more administrative responsibility than actual work involvement."""
    project_manager = "project_manager"
    """Person on the membership list of a designated project/project team. This vocabulary may or may not indicate the quality, quantity, or substance of the person's involvement."""
    project_member = "project_member"
    """Institution/organisation officially appointed by a Registration Authority to handle specific tasks within a defined area of responsibility. DataCite is a Registration Agency for the International DOI Foundation (IDF). One of DataCite's tasks is to assign DOI prefixes to the allocating agents who then assign the full, specific character string to data clients, provide metadata back to the DataCite registry, etc."""
    registration_agency = "registration_agency"
    """A standards-setting body from which Registration Agencies obtain official recognition and guidance. The IDF serves as the Registration Authority for the International Standards Organisation (ISO) in the area/domain of Digital Object Identifiers."""
    registration_authority = "registration_authority"
    """A person without a specifically defined role in the development of the resource, but who is someone the author wishes to recognize. This person could be an author's intellectual mentor, a person providing intellectual leadership in the discipline or subject domain, etc."""
    related_person = "related_person"
    """A person involved in analyzing data or the results of an experiment or formal study. May indicate an intern or assistant to one of the authors who helped with research but who was not so "key" as to be listed as an author. Should be a person, not an institution. Note that a person involved in the gathering of data would fall under the contributorType "data_collector." The researcher may find additional data online and correlate it to the data collected for the experiment or study, for example."""
    researcher = "researcher"
    """Typically refers to a group of individuals with a lab, department, or division; the group has a particular, defined focus of activity. May operate at a narrower level of scope; may or may not hold less administrative responsibility than a project team."""
    research_group = "research_group"
    """Person or institution owning or managing property rights, including intellectual property rights over the resource."""
    rights_holder = "rights_holder"
    """Person or organisation that issued a contract or under the auspices of which a work has been written, printed, published, developed, etc. Includes organisations that provide in-kind support, through donation, provision of people or a facility or instrumentation necessary for the development of the resource, etc."""
    sponsor = "sponsor"
    """Designated administrator over one or more groups/teams working to produce a resource or over one or more steps of a development process."""
    supervisor = "supervisor"
    """A Work Package is a recognized data product, not all of which is included in publication. The package, instead, may include notes, discarded documents, etc. The Work Package Leader is responsible for ensuring the comprehensive contents, versioning, and availability of the Work Package during the development of the resource."""
    work_package_leader = "work_package_leader"
    """Any person or institution making a significant contribution to the development and/or maintenance of the resource, but whose contribution does not "fit" other controlled vocabulary for contributorType. Could be a photographer, artist, or writer whose contribution helped to publicize the resource (as opposed to creating it), a reviewer of the resource, someone providing administrative services to the author (such as depositing updates into an online repository, analysing usage, etc.), or one of many other roles."""
    other = "other"
    """Ideas; formulation or evolution of overarching research goals and aims."""
    conceptualization = "conceptualization"
    """Management activities to annotate (produce metadata), scrub data and maintain research data (including software code, where it is necessary for interpreting the data itself) for initial use and later re-use."""
    data_curation = "data_curation"
    """Application of statistical, mathematical, computational, or other formal techniques to analyze or synthesize study data."""
    formal_analysis = "formal_analysis"
    """Acquisition of the financial support for the project leading to this publication."""
    funding_acquisition = "funding_acquisition"
    """Conducting a research and investigation process, specifically performing the experiments, or data/evidence collection."""
    investigation = "investigation"
    """Development or design of methodology; creation of models."""
    methodology = "methodology"
    """Management and coordination responsibility for the research activity planning and execution."""
    project_administration = "project_administration"
    """Provision of study materials, reagents, materials, patients, laboratory samples, animals, instrumentation, computing resources, or other analysis tools."""
    resources = "resources"
    """Programming, software development; designing computer programs; implementation of the computer code and supporting algorithms; testing of existing code components."""
    software = "software"
    """Oversight and leadership responsibility for the research activity planning and execution, including mentorship external to the core team."""
    supervision = "supervision"
    """Verification, whether as a part of the activity or separate, of the overall replication/reproducibility of results/experiments and other research outputs."""
    validation = "validation"
    """Preparation, creation and/or presentation of the published work, specifically visualization/data presentation."""
    visualization = "visualization"
    """Preparation, creation and/or presentation of the published work, specifically writing the initial draft (including substantive translation)."""
    writing_original_draft = "writing_original_draft"
    """Preparation, creation and/or presentation of the published work by those from the original research group, specifically critical review, commentary or revision -- including pre- or post-publication stages."""
    writing_review_andSOLIDUSor_editing = "writing_review_editing"


class ContributorType(str, Enum):
    """
    The type of contributor being represented.
    """

    """A person."""
    Person = "Person"
    """An organization."""
    Organization = "Organization"


class DescriptionType(str, Enum):
    """
    The type of text being represented.
    """

    """A brief description of the resource and the context in which the resource was created."""
    abstract = "abstract"
    description = "description"
    summary = "summary"


class EventType(str, Enum):
    """
    The type of date being represented.
    """

    """The date that the publisher accepted the resource into their system. To indicate the start of an embargo period, use Submitted or Accepted, as appropriate.
"""
    accepted = "accepted"
    """The date the resource is made publicly available. To indicate the end of an embargo period, use Available.
"""
    available = "available"
    """The specific, documented date at which the resource receives a copyrighted status, if applicable.
"""
    copyrighted = "copyrighted"
    """The date or date range in which the resource content was collected. To indicate precise or particular timeframes in which research was conducted.
"""
    collected = "collected"
    """The date the resource itself was put together; this could refer to a timeframe in ancient history, be a date range or a single date for a final component, e.g., the finalized file with all of the data.
"""
    created = "created"
    """The date that the resource is published or distributed e.g. to a data centre
"""
    issued = "issued"
    """The date the creator submits the resource to the publisher. This could be different from Accepted if the publisher then applies a selection process. To indicate the start of an embargo period, use Submitted or Accepted, as appropriate.
"""
    submitted = "submitted"
    """The date of the last update to the resource, when the resource is being added to.
"""
    updated = "updated"
    """The date (or date range) during which the dataset or resource is accurate.
"""
    valid = "valid"
    """The date the resource is removed.
"""
    withdrawn = "withdrawn"
    other = "other"


class RelationshipType(str, Enum):
    """
    The relationship between two entities. For example, when a PermanentID class is used to represent objects in the CreditMetadata field 'related_identifiers', the 'relationship_type' field captures the relationship between the resource being registered (A) and this ID (B).
    """

    based_on_data = "based_on_data"
    """Indicates that A includes B in a citation."""
    cites = "cites"
    """Indicates B is the result of a compile or creation event using A. May be used for software and text, as a compiler can be a computer program or a person."""
    compiles = "compiles"
    """Indicates A is a continuation of the work B."""
    continues = "continues"
    """Indicates A describes B."""
    describes = "describes"
    """Indicates A is documentation about B; e.g. points to software documentation."""
    documents = "documents"
    finances = "finances"
    has_comment = "has_comment"
    has_derivation = "has_derivation"
    has_expression = "has_expression"
    has_format = "has_format"
    has_manifestation = "has_manifestation"
    has_manuscript = "has_manuscript"
    """Indicates resource A has additional metadata B."""
    has_metadata = "has_metadata"
    """Indicates A includes the part B. Primarily this relation is applied to container-contained type relationships. May be used for individual software modules; note that code repository-to-version relationships should be modeled using IsVersionOf and HasVersion."""
    has_part = "has_part"
    has_preprint = "has_preprint"
    has_related_material = "has_related_material"
    has_reply = "has_reply"
    has_review = "has_review"
    has_translation = "has_translation"
    """Indicates A has a version (B). The registered resource such as a software package or code repository has a versioned instance (indicates A has the instance B) e.g. it may be used to relate an un-versioned code repository to one of its specific software versions."""
    has_version = "has_version"
    is_based_on = "is_based_on"
    is_basis_for = "is_basis_for"
    """Indicates that B includes A in a citation."""
    is_cited_by = "is_cited_by"
    is_comment_on = "is_comment_on"
    """Indicates B is used to compile or create A. May be used for software and text, as a compiler can be a computer program or a person."""
    is_compiled_by = "is_compiled_by"
    """Indicates A is continued by the work B."""
    is_continued_by = "is_continued_by"
    is_data_basis_for = "is_data_basis_for"
    """Indicates B is a source upon which A is based. IsDerivedFrom should be used for a resource that is a derivative of an original resource. For example, 'A isDerivedFrom B' could describe a dataset (A) derived from a larger dataset (B) where data values have been manipulated from their original state."""
    is_derived_from = "is_derived_from"
    """Indicates A is described by B."""
    is_described_by = "is_described_by"
    """Indicates B is documentation about/explaining A; e.g. points to software documentation."""
    is_documented_by = "is_documented_by"
    is_expression_of = "is_expression_of"
    is_financed_by = "is_financed_by"
    is_format_of = "is_format_of"
    """Indicates that A is identical to B, for use when there is a need to register two separate instances of the same resource. Should be used for a resource that is the same as the registered resource but is saved in another location, e.g. another institution."""
    is_identical_to = "is_identical_to"
    is_manifestation_of = "is_manifestation_of"
    is_manuscript_of = "is_manuscript_of"
    """Indicates additional metadata A for a resource B."""
    is_metadata_for = "is_metadata_for"
    """Indicates A is a new edition of B, where the new edition has been modified or updated."""
    is_new_version_of = "is_new_version_of"
    """Indicates A is replaced by B."""
    is_obsoleted_by = "is_obsoleted_by"
    """Indicates A is the original form of B. May be used for different software operating systems or compiler formats, for example."""
    is_original_form_of = "is_original_form_of"
    """Indicates A is a portion of B; may be used for elements of a series. Primarily this relation is applied to container-contained type relationships. May be used for individual software modules; note that code repository-to-version relationships should be modeled using IsVersionOf and HasVersion."""
    is_part_of = "is_part_of"
    is_preprint_of = "is_preprint_of"
    """Indicates A is a previous edition of B."""
    is_previous_version_of = "is_previous_version_of"
    """Indicates A is published inside B, but is independent of other things published inside of B."""
    is_published_in = "is_published_in"
    """Indicates A is used as a source of information by B."""
    is_referenced_by = "is_referenced_by"
    is_related_material = "is_related_material"
    is_replaced_by = "is_replaced_by"
    is_reply_to = "is_reply_to"
    """Indicates A is required by B. May be used to indicate software dependencies."""
    is_required_by = "is_required_by"
    is_review_of = "is_review_of"
    """Indicates that A is reviewed by B."""
    is_reviewed_by = "is_reviewed_by"
    is_same_as = "is_same_as"
    """Indicates A is a source upon which B is based. IsSourceOf is the original resource from which a derivative resource was created. For example, 'A isSourceOf B' could describe a dataset (A) which acts as the source of a derived dataset (B) where the values have been manipulated."""
    is_source_of = "is_source_of"
    """Indicates that A is a supplement to B."""
    is_supplement_to = "is_supplement_to"
    """Indicates that B is a supplement to A."""
    is_supplemented_by = "is_supplemented_by"
    is_translation_of = "is_translation_of"
    """Indicates A is a variant or different form of B. Use for a different form of one thing. May be used for different software operating systems or compiler formats, for example."""
    is_variant_form_of = "is_variant_form_of"
    """Indicates A is a version of B. The registered resource is an instance of a target resource (indicates that A is an instance of B) e.g. it may be used to relate a specific version of a software package to its software code repository."""
    is_version_of = "is_version_of"
    """Indicates A replaces B."""
    obsoletes = "obsoletes"
    """Indicates B is used as a source of information for A."""
    references = "references"
    replaces = "replaces"
    """Indicates A requires B. May be used to indicate software dependencies."""
    requires = "requires"
    """Indicates that A is a review of B."""
    reviews = "reviews"
    """The relationship between subject and object is unknown."""
    unknown = "unknown"


class ResourceType(str, Enum):
    """
    The type of resource being represented.
    """

    """A dataset."""
    dataset = "dataset"


class TitleType(str, Enum):
    """
    The type of title being represented.
    """

    """Any subtitle for the resource."""
    subtitle = "subtitle"
    """Other title(s) or names for the resource."""
    alternative_title = "alternative_title"
    """Translation of the title into another language."""
    translated_title = "translated_title"
    """Anything that doesn't fit into the above categories."""
    other = "other"


class Contributor(ConfiguredBaseModel):
    """
    Represents a contributor to the resource.

    Contributors must have a 'contributor_type', either 'Person' or 'Organization', and
    one of the 'name' fields: either 'given_name' and 'family_name' (for a person), or 'name' (for an organization or a person).

    The 'contributor_role' field takes values from the DataCite and CRediT contributor
    roles vocabularies. For more information on these resources and choosing
    appropriate roles, please see the following links:

    DataCite contributor roles: https://support.datacite.org/docs/datacite-metadata-schema-v44-recommended-and-optional-properties#7a-contributortype

    CRediT contributor role taxonomy: https://credit.niso.org.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "any_of": [
                {
                    "slot_conditions": {
                        "family_name": {"name": "family_name", "required": True},
                        "given_name": {"name": "given_name", "required": True},
                    }
                },
                {"slot_conditions": {"name": {"name": "name", "required": True}}},
            ],
            "from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/components",
        }
    )

    contributor_type: Optional[ContributorType] = Field(
        default=None,
        description="""Must be either 'Person' or 'Organization'.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "contributor_type",
                "domain_of": ["Contributor"],
                "examples": [{"value": "Person"}, {"value": "Organization"}],
                "slot_uri": "schema:@type",
            }
        },
    )
    contributor_id: Optional[str] = Field(
        default=None,
        description="""Persistent unique identifier for the contributor; this might be an ORCID for an individual, or a ROR ID for an organization.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "contributor_id",
                "domain_of": ["Contributor"],
                "examples": [{"value": "ORCID:0000-0001-9557-7715"}, {"value": "ROR:01znn6x10"}],
                "slot_uri": "schema:identifier",
            }
        },
    )
    name: Optional[str] = Field(
        default=None,
        description="""Contributor name. For organizations, this should be the full (unabbreviated) name; can also be used for a person if the given name/family name format is not applicable.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": ["Contributor"],
                "examples": [
                    {"value": "National Institute of Mental Health"},
                    {"value": "Madonna"},
                    {"value": "Ransome the Clown"},
                ],
                "slot_uri": "schema:name",
            }
        },
    )
    given_name: Optional[str] = Field(
        default=None,
        description="""The given name(s) of the contributor.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "given_name",
                "domain_of": ["Contributor"],
                "examples": [
                    {"value": "Marionetta Cecille de la"},
                    {"value": "Helena"},
                    {"value": "Hubert George"},
                ],
            }
        },
    )
    family_name: Optional[str] = Field(
        default=None,
        description="""The family name(s) of the contributor.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "family_name",
                "domain_of": ["Contributor"],
                "examples": [
                    {"value": "Carte-Postale"},
                    {"value": "Bonham Carter"},
                    {"value": "Wells"},
                ],
            }
        },
    )
    affiliations: Optional[List[Organization]] = Field(
        default=None,
        description="""List of organizations with which the contributor is affiliated. For contributors that represent an organization, this may be a parent organization (e.g. KBase, US DOE; Arkin lab, LBNL).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "affiliations",
                "domain_of": ["Contributor"],
                "slot_uri": "schema:affiliation",
            }
        },
    )
    contributor_roles: Optional[List[ContributorRole]] = Field(
        default=None,
        description="""List of roles played by the contributor when working on the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "contributor_roles",
                "domain_of": ["Contributor"],
                "slot_uri": "schema:Role",
            }
        },
    )

    @field_validator("contributor_id")
    def pattern_contributor_id(cls, v):
        pattern = re.compile(r"^[a-zA-Z0-9.-_]+:\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(v, str) and not pattern.match(element):
                    raise ValueError(f"Invalid contributor_id format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid contributor_id format: {v}")
        return v


class DataSource(ConfiguredBaseModel):
    """
    Source of any kind of data.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "any_of": [
                {"slot_conditions": {"source_name": {"name": "source_name", "required": True}}},
                {"slot_conditions": {"source_url": {"name": "source_url", "required": True}}},
            ],
            "from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/components",
        }
    )

    access_timestamp: int = Field(
        default=...,
        description="""Unix timestamp for when the data was retrieved from that source.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "access_timestamp",
                "comments": ["This could be added programmatically when updates occur."],
                "domain_of": ["DataSource"],
            }
        },
    )
    source_data_updated: Optional[datetime] = Field(
        default=None,
        description="""The date when the data source was last updated, if available.""",
        json_schema_extra={
            "linkml_meta": {"alias": "source_data_updated", "domain_of": ["DataSource"]}
        },
    )
    source_name: Optional[str] = Field(
        default=None,
        description="""Where the data was retrieved from.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_name",
                "domain_of": ["DataSource"],
                "examples": [{"value": "DataCite"}, {"value": "Crossref"}, {"value": "IMG"}],
            }
        },
    )
    source_url: Optional[str] = Field(
        default=None,
        description="""URL from whence data was retrieved.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "source_url",
                "domain_of": ["DataSource"],
                "examples": [
                    {
                        "value": "https://figshare.com/articles/dataset/Blue_Hole_Metagenome-assembled_Genomes/12644081"
                    },
                    {"value": "https://api.microbiomedata.org/studies/sty-123abc-999"},
                ],
            }
        },
    )


class Description(ConfiguredBaseModel):
    """
    Textual information about the resource being represented.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/components"}
    )

    description_text: str = Field(
        default=...,
        description="""The text content of the informational element.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description_text",
                "domain_of": ["Description"],
                "examples": [{"value": "This is the most interesting dataset ever to earn a DOI."}],
            }
        },
    )
    description_type: Optional[DescriptionType] = Field(
        default=None,
        description="""The type of text being represented.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description_type",
                "domain_of": ["Description"],
                "examples": [{"value": "abstract"}, {"value": "description"}, {"value": "summary"}],
            }
        },
    )
    language: Optional[str] = Field(
        default=None,
        description="""The language in which the description is written, using the appropriate IETF BCP-47 notation.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "language",
                "domain_of": ["Description", "Title"],
                "examples": [{"value": "ru-Cyrl"}, {"value": "fr"}],
            }
        },
    )


class EventDate(ConfiguredBaseModel):
    """
    Represents an event in the lifecycle of a resource and the date it occurred on.

    See https://support.datacite.org/docs/datacite-metadata-schema-v44-recommended-and-optional-properties#8-date for more information on the events.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/components"}
    )

    date: str = Field(
        default=...,
        description="""The date associated with the event. The date may be in the format YYYY, YYYY-MM, or YYYY-MM-DD.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "date",
                "domain_of": ["EventDate"],
                "examples": [{"value": "2001"}, {"value": "2021-05"}, {"value": "1998-02-15"}],
            }
        },
    )
    event: EventType = Field(
        default=...,
        description="""The nature of the resource-related event that occurred on that date.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "event",
                "domain_of": ["EventDate"],
                "examples": [{"value": "available"}, {"value": "updated"}],
            }
        },
    )

    @field_validator("date")
    def pattern_date(cls, v):
        pattern = re.compile(r"\d{4}(-\d{2}){0,2}")
        if isinstance(v, list):
            for element in v:
                if isinstance(v, str) and not pattern.match(element):
                    raise ValueError(f"Invalid date format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid date format: {v}")
        return v


class FundingReference(ConfiguredBaseModel):
    """
    Represents a funding source for a resource, including the funding body and the grant awarded.

    One (or more) of the fields 'grant_id', 'grant_url', or 'funder.organization_name' is required; others are optional.

    Recommended resources for organization identifiers include:
      - Research Organization Registry, http://ror.org
      - International Standard Name Identifier, https://isni.org
      - Crossref Funder Registry, https://www.crossref.org/services/funder-registry/ (to be subsumed into ROR)

    Some organizations may have a digital object identifier (DOI).

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "any_of": [
                {"slot_conditions": {"grant_id": {"name": "grant_id", "required": True}}},
                {"slot_conditions": {"grant_url": {"name": "grant_url", "required": True}}},
                {"slot_conditions": {"funder": {"name": "funder", "required": True}}},
            ],
            "class_uri": "schema:MonetaryGrant",
            "from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/components",
        }
    )

    funder: Optional[Organization] = Field(
        default=None,
        description="""The funder for the grant or award.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "funder",
                "domain_of": ["FundingReference"],
                "slot_uri": "schema:funder",
            }
        },
    )
    grant_id: Optional[str] = Field(
        default=None,
        description="""Code for the grant, assigned by the funder.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "grant_id",
                "domain_of": ["FundingReference"],
                "examples": [
                    {"value": "1296"},
                    {"value": "CBET-0756451"},
                    {"value": "DOI:10.46936/10.25585/60000745"},
                ],
                "slot_uri": "schema:identifier",
            }
        },
    )
    grant_title: Optional[str] = Field(
        default=None,
        description="""Title for the grant.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "grant_title",
                "domain_of": ["FundingReference"],
                "examples": [
                    {
                        "value": "Metagenomic analysis of the rhizosphere of three "
                        "biofuel crops at the KBS intensive site"
                    }
                ],
                "slot_uri": "schema:name",
            }
        },
    )
    grant_url: Optional[str] = Field(
        default=None,
        description="""URL for the grant.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "grant_url",
                "domain_of": ["FundingReference"],
                "examples": [
                    {
                        "value": "https://genome.jgi.doe.gov/portal/Metanaintenssite/Metanaintenssite.info.html"
                    }
                ],
                "slot_uri": "schema:url",
            }
        },
    )

    @field_validator("grant_url")
    def pattern_grant_url(cls, v):
        pattern = re.compile(r"^[a-zA-Z0-9.-_]+:\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(v, str) and not pattern.match(element):
                    raise ValueError(f"Invalid grant_url format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid grant_url format: {v}")
        return v


class License(ConfiguredBaseModel):
    """
    License information for the resource.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "any_of": [
                {"slot_conditions": {"id": {"name": "id", "required": True}}},
                {"slot_conditions": {"url": {"name": "url", "required": True}}},
            ],
            "from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/components",
        }
    )

    id: Optional[str] = Field(
        default=None,
        description="""String representing the license, from the SPDX license identifiers at https://spdx.org/licenses/.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": ["License", "PermanentID"],
                "examples": [{"value": "CC-BY-NC-ND-4.0"}, {"value": "Apache-2.0"}],
            }
        },
    )
    url: Optional[str] = Field(
        default=None,
        description="""URL for the license.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "url",
                "domain_of": ["License", "CreditMetadata"],
                "examples": [{"value": "https://jgi.doe.gov/user-programs/pmo-overview/policies/"}],
            }
        },
    )


class Metadata(ConfiguredBaseModel):
    """
    Metadata for the credit metadata, including the schema version used, who submitted it, and the date of submission. When the credit metadata for a resource is added or updated, this additional metadata must be provided along with the credit information.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/components"}
    )

    credit_metadata_schema_version: str = Field(
        default=...,
        description="""The version of the credit metadata schema used.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "credit_metadata_schema_version",
                "domain_of": ["Metadata"],
                "examples": [{"value": "1.1.0"}],
                "slot_uri": "schema:schemaVersion",
            }
        },
    )
    credit_metadata_source: Optional[List[DataSource]] = Field(
        default=None,
        description="""Information about where the credit metadata was sourced from.""",
        json_schema_extra={
            "linkml_meta": {"alias": "credit_metadata_source", "domain_of": ["Metadata"]}
        },
    )
    saved_by: str = Field(
        default=...,
        description="""PID for the user who added this entry.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "saved_by",
                "domain_of": ["Metadata"],
                "slot_uri": "schema:sdPublisher",
            }
        },
    )
    timestamp: int = Field(
        default=...,
        description="""Unix timestamp for the addition of this set of credit metadata.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "timestamp",
                "comments": ["This could be added programmatically when updates occur."],
                "domain_of": ["Metadata"],
                "slot_uri": "schema:sdDatePublished",
            }
        },
    )


class Organization(ConfiguredBaseModel):
    """
    Represents an organization.

    Recommended resources for organization identifiers and canonical organization names include:
      - Research Organization Registry, http://ror.org
      - International Standard Name Identifier, https://isni.org
      - Crossref Funder Registry, https://www.crossref.org/services/funder-registry/

    For example, the US DOE would be entered as:
      organization_name: United States Department of Energy
      organization_id:   ROR:01bj3aw27

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "class_uri": "schema:Organization",
            "from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/components",
        }
    )

    organization_id: Optional[str] = Field(
        default=None,
        description="""Persistent unique identifier for the organization in the format <database name>:<identifier within database>.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "organization_id",
                "domain_of": ["Organization"],
                "examples": [
                    {"value": "ROR:01bj3aw27"},
                    {"value": "ISNI:0000000123423717"},
                    {"value": "CrossrefFunder:100000015"},
                ],
                "slot_uri": "schema:identifier",
            }
        },
    )
    organization_name: str = Field(
        default=...,
        description="""Common name of the organization; use the name recommended by ROR if possible.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "organization_name",
                "domain_of": ["Organization"],
                "examples": [
                    {"value": "KBase"},
                    {"value": "Lawrence Berkeley National Laboratory"},
                    {"value": "The Ohio State University"},
                ],
                "slot_uri": "schema:name",
            }
        },
    )

    @field_validator("organization_id")
    def pattern_organization_id(cls, v):
        pattern = re.compile(r"^[a-zA-Z0-9.-_]+:\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(v, str) and not pattern.match(element):
                    raise ValueError(f"Invalid organization_id format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid organization_id format: {v}")
        return v


class PermanentID(ConfiguredBaseModel):
    """
    Represents a persistent unique identifier for an entity and its relationship to some other entity.

    The 'id' field and 'relationship_type' fields are required.

    The values in the 'relationship_type' field come from controlled vocabularies maintained by DataCite and Crossref. See the documentation links below for more details.

    DataCite relation types: https://support.datacite.org/docs/datacite-metadata-schema-v44-recommended-and-optional-properties#12b-relationtype

    Crossref relation types: https://www.crossref.org/documentation/schema-library/markup-guide-metadata-segments/relationships/

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/components"}
    )

    id: str = Field(
        default=...,
        description="""Persistent unique ID for an entity. Should be in the format <database name>:<identifier within database>.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": ["License", "PermanentID"],
                "examples": [
                    {"value": "DOI:10.46936/10.25585/60000745"},
                    {"value": "GO:0005456"},
                    {"value": "HGNC:7470"},
                ],
                "slot_uri": "schema:identifier",
            }
        },
    )
    description: Optional[str] = Field(
        default=None,
        description="""Description of that entity.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description",
                "domain_of": ["PermanentID"],
                "examples": [
                    {"value": "Amaranthus hypochondriacus genome"},
                    {
                        "value": "This data analysis workflow demonstrates how to "
                        "process a metagenome to identify viruses using "
                        "VirSorter. Then, provides taxonomic classification "
                        "using vConTACT2."
                    },
                ],
                "slot_uri": "schema:description",
            }
        },
    )
    relationship_type: Optional[RelationshipType] = Field(
        default=None,
        description="""The relationship between the ID and some other entity. For example, when a PermanentID class is used to represent objects in the CreditMetadata field 'related_identifiers', the 'relationship_type' field captures the relationship between the resource being registered and this ID.""",
        json_schema_extra={
            "linkml_meta": {"alias": "relationship_type", "domain_of": ["PermanentID"]}
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"^[a-zA-Z0-9.-_]+:\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(v, str) and not pattern.match(element):
                    raise ValueError(f"Invalid id format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid id format: {v}")
        return v


class Title(ConfiguredBaseModel):
    """
    Represents the title or name of a resource, the type of that title, and the language used (if appropriate).

    The 'title' field is required; 'title_type' is only necessary if the text is not the primary title.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/components"}
    )

    language: Optional[str] = Field(
        default=None,
        description="""The language in which the title is written, using the appropriate IETF BCP-47 notation.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "language",
                "domain_of": ["Description", "Title"],
                "examples": [{"value": "ru-Cyrl"}, {"value": "fr"}],
            }
        },
    )
    title: str = Field(
        default=...,
        description="""A string used as a title for a resource.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "title",
                "domain_of": ["Title"],
                "examples": [
                    {"value": "Amaranthus hypochondriacus genome"},
                    {"value": "Геном амаранта ипохондрического"},
                ],
                "slot_uri": "schema:name",
            }
        },
    )
    title_type: Optional[TitleType] = Field(
        default=None,
        description="""A descriptor for the title for cases where the contents of the 'title' field is not the primary name or title.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "title_type",
                "domain_of": ["Title"],
                "examples": [
                    {"value": "subtitle"},
                    {"value": "alternative_title"},
                    {"value": "translated_title"},
                    {"value": "other"},
                ],
            }
        },
    )


class CreditMetadata(ConfiguredBaseModel):
    """
    Represents the credit metadata associated with an object.

    In the following documentation, 'resource' is used to refer to the object
    that the CM pertains to, for example, a KBase Workspace object; a
    sample from NMDC or ESS-DIVE; sequence data from IMG.

    The 'resource_type' field should be filled using values from the DataCite
    resourceTypeGeneral field:

    https://support.datacite.org/docs/datacite-metadata-schema-v44-mandatory-properties#10a-resourcetypegeneral

    Currently this schema only supports credit metadata for objects of type
    'dataset'; anything else will return an error.

    The license may be supplied either as an URL pointing to licensing information for
    the resource, or using an SPDX license identifier from the list maintained at https://spdx.org/licenses/.

    Required fields are:
    - identifier
    - resource_type
    - versioning information: if the resource does not have an explicit version number,
    one or more dates should be supplied: ideally the date of resource publication and
    the last update (if applicable).
    - contributors (one or more required)
    - titles (one or more required)
    - meta

    The resource_type field is required, but as there is currently only a single valid
    value, 'dataset', it is automatically populated if no value is supplied.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "any_of": [
                {"slot_conditions": {"dates": {"name": "dates", "required": True}}},
                {"slot_conditions": {"version": {"name": "version", "required": True}}},
            ],
            "from_schema": "https://github.com/kbase/credit_engine/schema/dcm/linkml/credit_metadata",
            "tree_root": True,
        }
    )

    comment: Optional[List[str]] = Field(
        default=None,
        description="""List of strings of freeform text providing extra information about this credit metadata.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "comment",
                "domain_of": ["CreditMetadata"],
                "examples": [{"value": "This comment adds a lot of extra value!"}],
                "slot_uri": "schema:comment",
            }
        },
    )
    content_url: Optional[List[str]] = Field(
        default=None,
        description="""The URL of the content of the resource.""",
        json_schema_extra={
            "linkml_meta": {"alias": "content_url", "domain_of": ["CreditMetadata"]}
        },
    )
    contributors: List[Contributor] = Field(
        default=...,
        description="""A list of people and/or organizations who contributed to the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "contributors",
                "domain_of": ["CreditMetadata"],
                "slot_uri": "schema:creator",
            }
        },
    )
    dates: Optional[List[EventDate]] = Field(
        default=None,
        description="""A list of relevant lifecycle events for the resource. Note that these dates apply only to the resource itself, and not to the creation or update of the credit metadata record for the resource.""",
        json_schema_extra={"linkml_meta": {"alias": "dates", "domain_of": ["CreditMetadata"]}},
    )
    descriptions: Optional[List[Description]] = Field(
        default=None,
        description="""A brief description or abstract for the resource being represented.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "descriptions",
                "domain_of": ["CreditMetadata"],
                "slot_uri": "schema:description",
            }
        },
    )
    funding: Optional[List[FundingReference]] = Field(
        default=None,
        description="""Funding sources for the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "funding",
                "domain_of": ["CreditMetadata"],
                "slot_uri": "schema:funding",
                "todos": ["Should funding info be duplicated in the related_identifiers field?"],
            }
        },
    )
    identifier: str = Field(
        default=...,
        description="""Resolvable persistent unique identifier for the resource. Should be in the format <database name>:<identifier within database>.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "identifier",
                "comments": ["can generate schema:url from the identifier"],
                "domain_of": ["CreditMetadata"],
                "examples": [
                    {"value": "RefSeq:GCF_004214875.1"},
                    {"value": "GenBank:CP035949.1"},
                    {"value": "img.taxon:648028003"},
                ],
                "slot_uri": "schema:identifier",
            }
        },
    )
    license: Optional[License] = Field(
        default=None,
        description="""Usage license for the resource. Use one of the SPDX license identifiers or provide a link to the license text if no SPDX ID is available.
""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "license",
                "domain_of": ["CreditMetadata"],
                "exact_mappings": ["biolink:license"],
                "slot_uri": "schema:license",
            }
        },
    )
    meta: Metadata = Field(
        default=...,
        description="""Metadata for this credit information, including submitter, schema version, and timestamp.""",
        json_schema_extra={"linkml_meta": {"alias": "meta", "domain_of": ["CreditMetadata"]}},
    )
    publisher: Optional[Organization] = Field(
        default=None,
        description="""The publisher of the resource. For a dataset, this is the repository where it is stored.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "publisher",
                "domain_of": ["CreditMetadata"],
                "slot_uri": "schema:provider",
            }
        },
    )
    related_identifiers: Optional[List[PermanentID]] = Field(
        default=None,
        description="""Other resolvable persistent unique IDs related to the resource.""",
        json_schema_extra={
            "linkml_meta": {"alias": "related_identifiers", "domain_of": ["CreditMetadata"]}
        },
    )
    resource_type: ResourceType = Field(
        default=...,
        description="""The broad type of the source data for this object. 'dataset' is currently the only valid value supported by this schema.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "resource_type",
                "domain_of": ["CreditMetadata"],
                "examples": [{"value": "dataset"}],
                "slot_uri": "schema:@type",
            }
        },
    )
    titles: List[Title] = Field(
        default=...,
        description="""One or more titles for the resource.""",
        json_schema_extra={"linkml_meta": {"alias": "titles", "domain_of": ["CreditMetadata"]}},
    )
    url: Optional[str] = Field(
        default=None,
        description="""The URL of the resource.""",
        json_schema_extra={
            "linkml_meta": {"alias": "url", "domain_of": ["License", "CreditMetadata"]}
        },
    )
    version: Optional[str] = Field(
        default=None,
        description="""The version of the resource. This must be an absolute version, not a relative version like 'latest'.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "version",
                "domain_of": ["CreditMetadata"],
                "exact_mappings": ["DataCite:attributes.version"],
                "examples": [{"value": "5"}, {"value": "1.2.1"}, {"value": "20220405"}],
                "slot_uri": "schema:version",
            }
        },
    )

    @field_validator("identifier")
    def pattern_identifier(cls, v):
        pattern = re.compile(r"^[a-zA-Z0-9.-_]+:\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(v, str) and not pattern.match(element):
                    raise ValueError(f"Invalid identifier format: {element}")
        elif isinstance(v, str):
            if not pattern.match(v):
                raise ValueError(f"Invalid identifier format: {v}")
        return v


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Contributor.model_rebuild()
DataSource.model_rebuild()
Description.model_rebuild()
EventDate.model_rebuild()
FundingReference.model_rebuild()
License.model_rebuild()
Metadata.model_rebuild()
Organization.model_rebuild()
PermanentID.model_rebuild()
Title.model_rebuild()
CreditMetadata.model_rebuild()
