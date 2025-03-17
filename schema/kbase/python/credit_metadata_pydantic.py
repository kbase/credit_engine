"""Credit Metadata model, Pydantic version."""

from __future__ import annotations

import re
from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

metamodel_version = "None"
version = "0.0.4"


CURIE_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9.-_]+:\S")


def validate_pattern(
    field_name: str, v: list[str] | str, pattern: re.Pattern = CURIE_PATTERN
) -> list[str] | str:
    """
    Ensure that a value or list of values match a pattern.

    :param field_name: name of the field to be tested
    :type field_name: str
    :param v: value or list of values to test
    :type v: list[str] | str
    :param pattern: regex to match against
    :type pattern: re.Pattern
    :raises ValueError: if the values do not match the pattern
    :return: validated values
    :rtype: list[str] | str
    """
    errs = []
    if isinstance(v, list):
        errs = [el for el in v if not pattern.match(el)]
    elif isinstance(v, str) and not pattern.match(v):
        errs.append(v)

    if errs:
        err_msg = f"Invalid {field_name} format: " + ", ".join(errs)
        raise ValueError(err_msg)

    return v


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )


class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
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
        "default_prefix": "kbcms",
        "default_range": "string",
        "description": "Schema for KBase resource credit metadata. This version "
        "brings the schema into closer alignment with the commonmeta "
        "citation schema, https://commonmeta.org.",
        "id": "https://github.com/kbase/credit_engine/schema/kbase/linkml",
        "imports": ["linkml:types"],
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
            "ROR": {"prefix_prefix": "ROR", "prefix_reference": "http://identifiers.org/ror/"},
            "biolink": {
                "prefix_prefix": "biolink",
                "prefix_reference": "https://w3id.org/biolink/vocab/",
            },
            "bioportal": {
                "prefix_prefix": "bioportal",
                "prefix_reference": "https://bioportal.bioontology.org/ontologies/",
            },
            "crcr": {
                "prefix_prefix": "crcr",
                "prefix_reference": "https://credit.niso.org/contributor-roles/",
            },
            "gdmt": {
                "prefix_prefix": "gdmt",
                "prefix_reference": "http://vocab.fairdatacollective.org/fdc-gdmt/en/page/",
            },
            "kbcms": {
                "prefix_prefix": "kbcms",
                "prefix_reference": "https://kbase.github.io/credit_engine/",
            },
            "linkml": {"prefix_prefix": "linkml", "prefix_reference": "https://w3id.org/linkml/"},
            "rdfs": {
                "prefix_prefix": "rdfs",
                "prefix_reference": "http://www.w3.org/2000/01/rdf-schema#",
            },
            "schema": {"prefix_prefix": "schema", "prefix_reference": "http://schema.org/"},
            "xsd": {
                "prefix_prefix": "xsd",
                "prefix_reference": "http://www.w3.org/2001/XMLSchema#",
            },
        },
        "source_file": "schema/kbase/linkml/credit_metadata.yaml",
    }
)


class ContributorRole(str, Enum):
    """The type of contribution made by a contributor."""

    # Person with knowledge of how to access, troubleshoot, or otherwise field issues related to the resource. May also be "Point of Contact" in organisation that controls access to the resource, if that organisation is different from Publisher, Distributor, Data Manager.
    contact_person = "DataCite:ContactPerson"
    # Person/institution responsible for finding, gathering/collecting data under the guidelines of the author(s) or Principal Investigator (PI). May also use when crediting survey conductors, interviewers, event or condition observers, person responsible for monitoring key instrument data.
    data_collector = "DataCite:DataCollector"
    # Person tasked with reviewing, enhancing, cleaning, or standardizing metadata and the associated data submitted for storage, use, and maintenance within a data centre or repository. While the "DataManager" is concerned with digital maintenance, the DataCurator's role encompasses quality assurance focused on content and metadata. This includes checking whether the submitted dataset is complete, with all files and components as described by submitter, whether the metadata is standardized to appropriate systems and schema, whether specialized metadata is needed to add value and ensure access across disciplines, and determining how the metadata might map to search engines, database products, and automated feeds.
    data_curator = "DataCite:DataCurator"
    # Person (or organisation with a staff of data managers, such as a data centre) responsible for maintaining the finished resource. The work done by this person or organisation ensures that the resource is periodically "refreshed" in terms of software/hardware support, is kept available or is protected from unauthorized access, is stored in accordance with industry standards, and is handled in accordance with the records management requirements applicable to it.
    data_manager = "DataCite:DataManager"
    # Institution tasked with responsibility to generate/disseminate copies of the resource in either electronic or print form. Works stored in more than one archive/repository may credit each as a distributor.
    distributor = "DataCite:Distributor"
    # A person who oversees the details related to the publication format of the resource. N.b. if the Editor is to be credited in place of multiple creators, the Editor's name may be supplied as Creator, with "(Ed.)" appended to the name.
    editor = "DataCite:Editor"
    # Typically, the organisation allowing the resource to be available on the internet through the provision of its hardware/software/operating support. May also be used for an organisation that stores the data offline. Often a data centre (if that data centre is not the "publisher" of the resource.)
    hosting_institution = "DataCite:HostingInstitution"
    # Typically a person or organisation responsible for the artistry and form of a media product. In the data industry, this may be a company "producing" DVDs that package data for future dissemination by a distributor.
    producer = "DataCite:Producer"
    # Person officially designated as head of project team or sub- project team instrumental in the work necessary to development of the resource. The Project Leader is not "removed" from the work that resulted in the resource; he or she remains intimately involved throughout the life of the particular project team.
    project_leader = "DataCite:ProjectLeader"
    # Person officially designated as manager of a project. Project may consist of one or many project teams and sub-teams. The manager of a project normally has more administrative responsibility than actual work involvement.
    project_manager = "DataCite:ProjectManager"
    # Person on the membership list of a designated project/project team. This vocabulary may or may not indicate the quality, quantity, or substance of the person's involvement.
    project_member = "DataCite:ProjectMember"
    # Institution/organisation officially appointed by a Registration Authority to handle specific tasks within a defined area of responsibility. DataCite is a Registration Agency for the International DOI Foundation (IDF). One of DataCite's tasks is to assign DOI prefixes to the allocating agents who then assign the full, specific character string to data clients, provide metadata back to the DataCite registry, etc.
    registration_agency = "DataCite:RegistrationAgency"
    # A standards-setting body from which Registration Agencies obtain official recognition and guidance. The IDF serves as the Registration Authority for the International Standards Organisation (ISO) in the area/domain of Digital Object Identifiers.
    registration_authority = "DataCite:RegistrationAuthority"
    # A person without a specifically defined role in the development of the resource, but who is someone the author wishes to recognize. This person could be an author's intellectual mentor, a person providing intellectual leadership in the discipline or subject domain, etc.
    related_person = "DataCite:RelatedPerson"
    # A person involved in analyzing data or the results of an experiment or formal study. May indicate an intern or assistant to one of the authors who helped with research but who was not so "key" as to be listed as an author. Should be a person, not an institution. Note that a person involved in the gathering of data would fall under the contributorType "DataCollector." The researcher may find additional data online and correlate it to the data collected for the experiment or study, for example.
    researcher = "DataCite:Researcher"
    # Typically refers to a group of individuals with a lab, department, or division; the group has a particular, defined focus of activity. May operate at a narrower level of scope; may or may not hold less administrative responsibility than a project team.
    research_group = "DataCite:ResearchGroup"
    # Person or institution owning or managing property rights, including intellectual property rights over the resource.
    rights_holder = "DataCite:RightsHolder"
    # Person or organisation that issued a contract or under the auspices of which a work has been written, printed, published, developed, etc. Includes organisations that provide in-kind support, through donation, provision of people or a facility or instrumentation necessary for the development of the resource, etc.
    sponsor = "DataCite:Sponsor"
    # Designated administrator over one or more groups/teams working to produce a resource or over one or more steps of a development process.
    supervisor = "DataCite:Supervisor"
    # A Work Package is a recognized data product, not all of which is included in publication. The package, instead, may include notes, discarded documents, etc. The Work Package Leader is responsible for ensuring the comprehensive contents, versioning, and availability of the Work Package during the development of the resource.
    work_package_leader = "DataCite:WorkPackageLeader"
    # Any person or institution making a significant contribution to the development and/or maintenance of the resource, but whose contribution does not "fit" other controlled vocabulary for contributorType. Could be a photographer, artist, or writer whose contribution helped to publicize the resource (as opposed to creating it), a reviewer of the resource, someone providing administrative services to the author (such as depositing updates into an online repository, analysing usage, etc.), or one of many other roles.
    other = "DataCite:Other"
    # Ideas; formulation or evolution of overarching research goals and aims.
    conceptualization = "crcr:conceptualization"
    # Management activities to annotate (produce metadata), scrub data and maintain research data (including software code, where it is necessary for interpreting the data itself) for initial use and later re-use.
    data_curation = "crcr:data-curation"
    # Application of statistical, mathematical, computational, or other formal techniques to analyze or synthesize study data.
    formal_analysis = "crcr:formal-analysis"
    # Acquisition of the financial support for the project leading to this publication.
    funding_acquisition = "crcr:funding-acquisition"
    # Conducting a research and investigation process, specifically performing the experiments, or data/evidence collection.
    investigation = "crcr:investigation"
    # Development or design of methodology; creation of models.
    methodology = "crcr:methodology"
    # Management and coordination responsibility for the research activity planning and execution.
    project_administration = "crcr:project-administration"
    # Provision of study materials, reagents, materials, patients, laboratory samples, animals, instrumentation, computing resources, or other analysis tools.
    resources = "crcr:resources"
    # Programming, software development; designing computer programs; implementation of the computer code and supporting algorithms; testing of existing code components.
    software = "crcr:software"
    # Oversight and leadership responsibility for the research activity planning and execution, including mentorship external to the core team.
    supervision = "crcr:supervision"
    # Verification, whether as a part of the activity or separate, of the overall replication/reproducibility of results/experiments and other research outputs.
    validation = "crcr:validation"
    # Preparation, creation and/or presentation of the published work, specifically visualization/data presentation.
    visualization = "crcr:visualization"
    # Preparation, creation and/or presentation of the published work, specifically writing the initial draft (including substantive translation).
    writing_original_draft = "crcr:writing-original-draft"
    # Preparation, creation and/or presentation of the published work by those from the original research group, specifically critical review, commentary or revision -- including pre- or post-publication stages.
    writing_review_andSOLIDUSor_editing = "crcr:writing-review-editing"


class ContributorType(str, Enum):
    """The type of contributor being represented."""

    # A person
    Person = "Person"
    # An organization
    Organization = "Organization"


class DescriptionType(str, Enum):
    """The type of text being represented."""

    # A brief description of the resource and the context in which the resource was created.
    abstract = "abstract"
    description = "description"
    summary = "summary"


class EventType(str, Enum):
    """The type of date being represented."""

    # The date that the publisher accepted the resource into their system. To indicate the start of an embargo period, use Submitted or Accepted, as appropriate.

    accepted = "accepted"
    # The date the resource is made publicly available. To indicate the end of an embargo period, use Available.

    available = "available"
    # The specific, documented date at which the resource receives a copyrighted status, if applicable.

    copyrighted = "copyrighted"
    # The date or date range in which the resource content was collected. To indicate precise or particular timeframes in which research was conducted.

    collected = "collected"
    # The date the resource itself was put together; this could refer to a timeframe in ancient history, be a date range or a single date for a final component, e.g., the finalized file with all of the data.

    created = "created"
    # The date that the resource is published or distributed e.g. to a data centre

    issued = "issued"
    # The date the creator submits the resource to the publisher. This could be different from Accepted if the publisher then applies a selection process. To indicate the start of an embargo period, use Submitted or Accepted, as appropriate.

    submitted = "submitted"
    # The date of the last update to the resource, when the resource is being added to.

    updated = "updated"
    # The date (or date range) during which the dataset or resource is accurate.

    valid = "valid"
    # The date the resource is removed.

    withdrawn = "withdrawn"
    other = "other"


class RelationshipType(str, Enum):
    """The relationship between two entities. For example, when a PermanentID class is used to represent objects in the CreditMetadata field 'related_identifiers', the 'relationship_type' field captures the relationship between the resource being registered (A) and this ID (B)."""

    based_on_data = "based_on_data"

    cites = "cites"
    compiles = "compiles"
    continues = "continues"
    describes = "describes"
    documents = "documents"
    finances = "finances"
    has_comment = "has_comment"
    has_derivation = "has_derivation"
    has_expression = "has_expression"
    has_format = "has_format"
    has_manifestation = "has_manifestation"
    has_manuscript = "has_manuscript"
    has_metadata = "has_metadata"
    has_part = "has_part"
    has_preprint = "has_preprint"
    has_related_material = "has_related_material"
    has_reply = "has_reply"
    has_review = "has_review"
    has_translation = "has_translation"
    has_version = "has_version"
    is_based_on = "is_based_on"
    is_basis_for = "is_basis_for"
    is_cited_by = "is_cited_by"
    is_comment_on = "is_comment_on"
    is_compiled_by = "is_compiled_by"
    is_continued_by = "is_continued_by"
    is_data_basis_for = "is_data_basis_for"
    is_derived_from = "is_derived_from"
    is_described_by = "is_described_by"
    is_documented_by = "is_documented_by"
    is_expression_of = "is_expression_of"
    is_financed_by = "is_financed_by"
    is_format_of = "is_format_of"
    is_identical_to = "is_identical_to"
    is_manifestation_of = "is_manifestation_of"
    is_manuscript_of = "is_manuscript_of"
    is_metadata_for = "is_metadata_for"
    is_new_version_of = "is_new_version_of"
    is_obsoleted_by = "is_obsoleted_by"
    is_original_form_of = "is_original_form_of"
    is_part_of = "is_part_of"
    is_preprint_of = "is_preprint_of"
    is_previous_version_of = "is_previous_version_of"
    is_published_in = "is_published_in"
    is_referenced_by = "is_referenced_by"
    is_related_material = "is_related_material"
    is_replaced_by = "is_replaced_by"
    is_reply_to = "is_reply_to"
    is_required_by = "is_required_by"
    is_review_of = "is_review_of"
    is_reviewed_by = "is_reviewed_by"
    is_same_as = "is_same_as"
    is_source_of = "is_source_of"
    is_supplement_to = "is_supplement_to"
    is_supplemented_by = "is_supplemented_by"
    is_translation_of = "is_translation_of"
    is_variant_form_of = "is_variant_form_of"
    is_version_of = "is_version_of"
    obsoletes = "obsoletes"
    references = "references"
    replaces = "replaces"
    requires = "requires"
    reviews = "reviews"
    unknown = "unknown"


class ResourceType(str, Enum):
    """The type of resource being represented."""

    # a dataset
    dataset = "dataset"


class TitleType(str, Enum):
    """The type of title being represented."""

    # any subtitle for the resource
    subtitle = "subtitle"
    # other title(s) or names for the resource
    alternative_title = "alternative_title"
    # translation of the title into another language
    translated_title = "translated_title"
    # anything that doesn't fit into the above categories
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

    CRediT contributor role taxonomy: https://credit.niso.org

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
            "from_schema": "https://github.com/kbase/credit_engine/schema/kbase/linkml",
        }
    )

    contributor_type: ContributorType | None = Field(
        None,
        description="""Must be either 'Person' or 'Organization'""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "contributor_type",
                "domain_of": ["Contributor"],
                "exact_mappings": [
                    "DataCite:attributes.contributors.name_type",
                    "DataCite:attributes.creators.name_type",
                ],
                "examples": [{"value": "Person"}, {"value": "Organization"}],
                "slot_uri": "schema:@type",
            }
        },
    )
    contributor_id: str | None = Field(
        None,
        description="""Persistent unique identifier for the contributor; this might be an ORCID for an individual, or a ROR ID for an organization.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "contributor_id",
                "domain_of": ["Contributor"],
                "exact_mappings": [
                    "DataCite:attributes.contributors.name_identifiers.name_identifier",
                    "DataCite:attributes.creators.name_identifiers.name_identifier",
                ],
                "examples": [{"value": "ORCID:0000-0001-9557-7715"}, {"value": "ROR:01znn6x10"}],
                "narrow_mappings": [
                    "ORCID:contributor.orcidId",
                    "OSTI.ARTICLE:author.orcid_id",
                    "OSTI.ARTICLE:contributor.orcid_id",
                    "Crossref:message.project.funding.funder.name",
                ],
                "slot_uri": "schema:identifier",
            }
        },
    )
    name: str | None = Field(
        None,
        description="""Contributor name. For organizations, this should be the full (unabbreviated) name; can also be used for a person if the given name/family name format is not applicable.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "close_mappings": ["OSTI.ARTICLE:author", "OSTI.ARTICLE:contributor"],
                "domain_of": ["Contributor"],
                "exact_mappings": ["JGI:organisms.pi.name", "ORCID:name"],
                "examples": [
                    {"value": "National Institute of Mental Health"},
                    {"value": "Madonna"},
                    {"value": "Ransome the Clown"},
                ],
                "related_mappings": [
                    "DataCite:attributes.creators.name",
                    "DataCite:attributes.contributors.name",
                ],
                "slot_uri": "schema:name",
            }
        },
    )
    given_name: str | None = Field(
        None,
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
                "related_mappings": [
                    "DataCite:attributes.contributors.givenName",
                    "DataCite:attributes.creators.givenName",
                ],
            }
        },
    )
    family_name: str | None = Field(
        None,
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
                "related_mappings": [
                    "DataCite:attributes.contributors.familyName",
                    "DataCite:attributes.creators.familyName",
                ],
            }
        },
    )
    affiliations: list[Organization] | None = Field(
        None,
        description="""List of organizations with which the contributor is affiliated. For contributors that represent an organization, this may be a parent organization (e.g. KBase, US DOE; Arkin lab, LBNL).""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "affiliations",
                "domain_of": ["Contributor"],
                "narrow_mappings": ["OSTI.ARTICLE:contributor.affiliation_name"],
                "related_mappings": [
                    "DataCite:attributes.contributors.affiliation",
                    "DataCite:attributes.creators.affiliation",
                    "JGI:organisms.pi.institution",
                ],
                "slot_uri": "schema:affiliation",
            }
        },
    )
    contributor_roles: list[ContributorRole] | None = Field(
        None,
        description="""List of roles played by the contributor when working on the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "contributor_roles",
                "close_mappings": [
                    "ORCID:contributor.role",
                    "OSTI.ARTICLE:contributor.contributorType",
                ],
                "domain_of": ["Contributor"],
                "exact_mappings": [
                    "DataCite:attributes.contributors.contributor_type",
                    "DataCite:attributes.creators.contributor_type",
                ],
                "related_mappings": ["JGI:organisms.pi"],
                "slot_uri": "schema:Role",
            }
        },
    )

    @field_validator("contributor_id")
    def pattern_contributor_id(cls, v):
        return validate_pattern("contributor_id", v)


class CreditMetadata(ConfiguredBaseModel):
    """
    Represents the credit metadata associated with an object.

    In the following documentation, 'Resource' is used to refer to the object
    that the CM pertains to, for example, a KBase Workspace object or a
    sample from the KBase Sample Service.

    The 'resource_type' field should be filled using values from the DataCite
    resourceTypeGeneral field:

    https://support.datacite.org/docs/datacite-metadata-schema-v44-mandatory-properties#10a-resourcetypegeneral

    Currently KBase only supports credit metadata for objects of type
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
            "from_schema": "https://github.com/kbase/credit_engine/schema/kbase/linkml",
            "tree_root": True,
        }
    )

    comment: list[str] | None = Field(
        None,
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
    content_url: list[str] | None = Field(
        None,
        description="""The URL of the content of the resource.""",
        json_schema_extra={
            "linkml_meta": {"alias": "content_url", "domain_of": ["CreditMetadata"]}
        },
    )
    contributors: list[Contributor] = Field(
        ...,
        description="""A list of people and/or organizations who contributed to the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "contributors",
                "domain_of": ["CreditMetadata"],
                "narrow_mappings": [
                    "DataCite:attributes.contributors",
                    "DataCite:attributes.creators",
                    "ORCID:contributors",
                    "OSTI.ARTICLE:contributors",
                    "OSTI.ARTICLE:authors",
                    "JGI:organisms.pi",
                ],
                "slot_uri": "schema:creator",
            }
        },
    )
    credit_metadata_source: list[str] | None = Field(
        None,
        description="""A list of CURIEs, URIs, or free text entries denoting the source of the credit metadata.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "credit_metadata_source",
                "domain_of": ["CreditMetadata"],
                "examples": [
                    {
                        "value": "https://figshare.com/articles/dataset/Blue_Hole_Metagenome-assembled_Genomes/12644081"
                    },
                    {"value": "DataCite"},
                    {"value": "DOI:10.13039/100000015"},
                ],
            }
        },
    )
    dates: list[EventDate] | None = Field(
        None,
        description="""A list of relevant lifecycle events for the resource. Note that these dates apply only to the resource itself, and not to the creation or update of the credit metadata record for the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "dates",
                "close_mappings": [
                    "DataCite:attributes.published",
                    "DataCite:attributes.updated",
                    "DataCite:attributes.dates",
                    "ORCID:publicationDate",
                    "OSTI.ARTICLE:publication_date",
                    "Crossref:message.deposited",
                ],
                "domain_of": ["CreditMetadata"],
            }
        },
    )
    descriptions: list[Description] | None = Field(
        None,
        description="""A brief description or abstract for the resource being represented.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "descriptions",
                "domain_of": ["CreditMetadata"],
                "slot_uri": "schema:description",
            }
        },
    )
    funding: list[FundingReference] | None = Field(
        None,
        description="""Funding sources for the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "funding",
                "close_mappings": [
                    "DataCite:attributes.funding_references",
                    "Crossref:Message.project.funding",
                    "OSTI.ARTICLE:awards",
                ],
                "domain_of": ["CreditMetadata"],
                "slot_uri": "schema:funding",
            }
        },
    )
    identifier: str = Field(
        ...,
        description="""Resolvable persistent unique identifier for the resource. Should be in the format <database name>:<identifier within database>.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "identifier",
                "domain_of": ["CreditMetadata"],
                "exact_mappings": ["DataCite:id", "JGI:organisms.grouped_by"],
                "examples": [
                    {"value": "RefSeq:GCF_004214875.1"},
                    {"value": "GenBank:CP035949.1"},
                    {"value": "img.taxon:648028003"},
                ],
                "narrow_mappings": [
                    "OSTI.ARTICLE:osti_id",
                    "OSTI.ARTICLE:doi",
                    "ORCID:doi",
                    "ORCID:url",
                ],
                "slot_uri": "schema:identifier",
            }
        },
    )
    license: License | None = Field(
        None,
        description="""Usage license for the resource. Use one of the SPDX license identifiers or provide a link to the license text if no SPDX ID is available.

All data published at KBase is done so under a Creative Commons 0 or Creative Commons 4.0 license.
""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "license",
                "domain_of": ["CreditMetadata"],
                "exact_mappings": ["biolink:license"],
                "related_mappings": ["DataCite:attributes.rights_list"],
                "slot_uri": "schema:license",
            }
        },
    )
    meta: Metadata = Field(
        ...,
        description="""Metadata for this credit information, including submitter, schema version, and timestamp.""",
        json_schema_extra={"linkml_meta": {"alias": "meta", "domain_of": ["CreditMetadata"]}},
    )
    publisher: Organization | None = Field(
        None,
        description="""The publisher of the resource. For a dataset, this is the repository where it is stored.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "publisher",
                "domain_of": ["CreditMetadata"],
                "narrow_mappings": ["ORCID:url", "OSTI.ARTICLE:site_url"],
                "slot_uri": "schema:provider",
            }
        },
    )
    related_identifiers: list[PermanentID] | None = Field(
        None,
        description="""Other resolvable persistent unique IDs related to the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "related_identifiers",
                "close_mappings": [
                    "DataCite:attributes.identifiers",
                    "DataCite:attributes.related_identifiers",
                    "DataCite:attributes.alternate_identifiers",
                    "ORCID:externalIds",
                    "OSTI.ARTICLE:related_identifiers",
                ],
                "domain_of": ["CreditMetadata"],
                "narrow_mappings": ["ORCID:doi", "OSTI.ARTICLE:doi"],
            }
        },
    )
    resource_type: ResourceType = Field(
        ...,
        description="""The broad type of the source data for this object. 'dataset' is currently the only valid value for KBase DOIs.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "resource_type",
                "domain_of": ["CreditMetadata"],
                "exact_mappings": [
                    "OSTI.ARTICLE:product_type",
                    "OSTI.ARTICLE:workType",
                    "DataCite:attributes.types.schema_org",
                ],
                "examples": [{"value": "dataset"}],
                "narrow_mappings": ["OSTI.ARTICLE:dataset_type"],
                "slot_uri": "schema:@type",
            }
        },
    )
    titles: list[Title] = Field(
        ...,
        description="""One or more titles for the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "titles",
                "domain_of": ["CreditMetadata"],
                "exact_mappings": [
                    "DataCite:attributes.titles",
                    "ORCID:title",
                    "OSTI.ARTICLE:title",
                ],
            }
        },
    )
    url: str | None = Field(
        None,
        description="""The URL of the resource.""",
        json_schema_extra={
            "linkml_meta": {"alias": "url", "domain_of": ["CreditMetadata", "License"]}
        },
    )
    version: str | None = Field(
        None,
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
        return validate_pattern("identifier", v)


class Description(ConfiguredBaseModel):
    """Textual information about the resource being represented."""

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://github.com/kbase/credit_engine/schema/kbase/linkml"}
    )

    description_text: str = Field(
        ...,
        description="""The text content of the informational element.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description_text",
                "domain_of": ["Description"],
                "examples": [
                    {"value": "This is the most interesting dataset ever to earn a " "DOI."}
                ],
            }
        },
    )
    description_type: DescriptionType | None = Field(
        None,
        description="""The type of text being represented""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description_type",
                "domain_of": ["Description"],
                "examples": [{"value": "abstract"}, {"value": "description"}, {"value": "summary"}],
            }
        },
    )
    language: str | None = Field(
        None,
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
        {"from_schema": "https://github.com/kbase/credit_engine/schema/kbase/linkml"}
    )

    date: str = Field(
        ...,
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
        ...,
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
        return validate_pattern("date", v, pattern=pattern)


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
            "from_schema": "https://github.com/kbase/credit_engine/schema/kbase/linkml",
        }
    )

    funder: Organization | None = Field(
        None,
        description="""The funder for the grant or award""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "funder",
                "domain_of": ["FundingReference"],
                "slot_uri": "schema:funder",
            }
        },
    )
    grant_id: str | None = Field(
        None,
        description="""Code for the grant, assigned by the funder""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "grant_id",
                "domain_of": ["FundingReference"],
                "exact_mappings": [
                    "DataCite:attributes.funding_references.award_number",
                    "Crossref:message.award",
                ],
                "examples": [
                    {"value": "1296"},
                    {"value": "CBET-0756451"},
                    {"value": "DOI:10.46936/10.25585/60000745"},
                ],
                "narrow_mappings": ["OSTI.ARTICLE:award_doi", "OSTI.ARTICLE:award_number"],
                "slot_uri": "schema:identifier",
            }
        },
    )
    grant_title: str | None = Field(
        None,
        description="""Title for the grant""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "grant_title",
                "domain_of": ["FundingReference"],
                "exact_mappings": ["DataCite:attributes.funding_references.award_title"],
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
    grant_url: str | None = Field(
        None,
        description="""URL for the grant""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "grant_url",
                "close_mappings": ["OSTI.ARTICLE:award_doi"],
                "domain_of": ["FundingReference"],
                "exact_mappings": ["DataCite:attributes.funding_references.award_url"],
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
        return validate_pattern("grant_url", v)


class License(ConfiguredBaseModel):
    """License information for the resource."""

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://github.com/kbase/credit_engine/schema/kbase/linkml"}
    )

    id: str | None = Field(
        None,
        description="""String representing the license, from the SPDX license identifiers at https://spdx.org/licenses/.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": ["License", "PermanentID"],
                "examples": [{"value": "CC-BY-NC-ND-4.0"}, {"value": "Apache-2.0"}],
            }
        },
    )
    url: str | None = Field(
        None,
        description="""URL for the license.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "url",
                "domain_of": ["CreditMetadata", "License"],
                "examples": [{"value": "https://jgi.doe.gov/user-programs/pmo-overview/policies/"}],
            }
        },
    )


class Metadata(ConfiguredBaseModel):
    """Metadata for the credit metadata, including the schema version used, who submitted it, and the date of submission. When the credit metadata for a resource is added or updated, this additional metadata must be provided along with the credit information."""

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://github.com/kbase/credit_engine/schema/kbase/linkml"}
    )

    credit_metadata_schema_version: str = Field(
        ...,
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
    saved_by: str = Field(
        ...,
        description="""KBase workspace ID of the user who added this entry.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "saved_by",
                "domain_of": ["Metadata"],
                "slot_uri": "schema:sdPublisher",
            }
        },
    )
    timestamp: int = Field(
        ...,
        description="""Unix timestamp for the addition of this set of credit metadata.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "timestamp",
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
            "from_schema": "https://github.com/kbase/credit_engine/schema/kbase/linkml",
        }
    )

    organization_id: str | None = Field(
        None,
        description="""Persistent unique identifier for the organization in the format <database name>:<identifier within database>""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "organization_id",
                "domain_of": ["Organization"],
                "exact_mappings": [
                    "DataCite:attributes.contributors.affiliation.affiliation_identifier",
                    "DataCite:attributes.creators.affiliation.affiliation_identifier",
                ],
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
        ...,
        description="""Common name of the organization; use the name recommended by ROR if possible.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "organization_name",
                "domain_of": ["Organization"],
                "exact_mappings": [
                    "DataCite:attributes.contributors.affiliation.name",
                    "DataCite:attributes.creators.affiliation.name",
                    "OSTI.ARTICLE:research_organization",
                    "JGI:organisms.pi.institution",
                ],
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
        return validate_pattern("organization_id", v)


class PermanentID(ConfiguredBaseModel):
    """
    Represents a persistent unique identifier for an entity and its relationship to some other entity.

    The 'id' field and 'relationship_type' fields are required.

    The values in the 'relationship_type' field come from controlled vocabularies maintained by DataCite and Crossref. See the documentation links below for more details.

    DataCite relation types: https://support.datacite.org/docs/datacite-metadata-schema-v44-recommended-and-optional-properties#12b-relationtype

    Crossref relation types: https://www.crossref.org/documentation/schema-library/markup-guide-metadata-segments/relationships/

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://github.com/kbase/credit_engine/schema/kbase/linkml"}
    )

    id: str = Field(
        ...,
        description="""Persistent unique ID for an entity. Should be in the format <database name>:<identifier within database>.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "id",
                "domain_of": ["License", "PermanentID"],
                "exact_mappings": [
                    "DataCite:attributes.identifier.value",
                    "DataCite:attributes.alternate_identifiers",
                    "DataCite:attributes.related_identifiers",
                    "DataCite:attributes.identifiers",
                ],
                "examples": [
                    {"value": "DOI:10.46936/10.25585/60000745"},
                    {"value": "GO:0005456"},
                    {"value": "HGNC:7470"},
                ],
                "related_mappings": ["OSTI.ARTICLE:site_url"],
                "slot_uri": "schema:identifier",
            }
        },
    )
    description: str | None = Field(
        None,
        description="""Description of that entity.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "description",
                "domain_of": ["PermanentID"],
                "exact_mappings": ["OSTI.ARTICLE:description"],
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
    relationship_type: RelationshipType | None = Field(
        None,
        description="""The relationship between the ID and some other entity.
For example, when a PermanentID class is used to represent objects in the CreditMetadata field 'related_identifiers', the 'relationship_type' field captures the relationship between the resource being registered and this ID.
""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "relationship_type",
                "domain_of": ["PermanentID"],
                "exact_mappings": ["DataCite:attributes.related_identifiers.relation_type"],
            }
        },
    )

    @field_validator("relationship_type", mode="before")
    @classmethod
    def relationship_type_fixed(cls, v: str) -> str:
        print(f"checking relationship_type with input {v}")

        def fix_str(matchobj) -> str:
            return matchobj.group(1) + "_" + matchobj.group(2)

        pattern = re.compile(r"\w+:(.+)")
        if re.match(pattern, v):
            suffix = re.match(pattern, v).group(1)
            print(f"suffix: {suffix}")

            fixed = re.sub(r"([a-z])([A-Z])", fix_str, suffix)
            print(f"fixed: {fixed}")
            return fixed.lower()

        return v

    @field_validator("id")
    def pattern_id(cls, v):
        return validate_pattern("id", v)


class Title(ConfiguredBaseModel):
    """
    Represents the title or name of a resource, the type of that title, and the language used (if appropriate).

    The 'title' field is required; 'title_type' is only necessary if the text is not the primary title.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://github.com/kbase/credit_engine/schema/kbase/linkml"}
    )

    language: str | None = Field(
        None,
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
        ...,
        description="""A string used as a title for a resource""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "title",
                "domain_of": ["Title"],
                "exact_mappings": [
                    "DataCite:attributes.titles.title",
                    "Crossref:message.project.project-title.title",
                ],
                "examples": [
                    {"value": "Amaranthus hypochondriacus genome"},
                    {"value": "Геном амаранта ипохондрического"},
                ],
                "slot_uri": "schema:name",
            }
        },
    )
    title_type: TitleType | None = Field(
        None,
        description="""A descriptor for the title for cases where the contents of the 'title' field is not the primary name or title.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "title_type",
                "domain_of": ["Title"],
                "exact_mappings": ["DataCite:attributes.title.titleType"],
                "examples": [
                    {"value": "subtitle"},
                    {"value": "alternative_title"},
                    {"value": "translated_title"},
                    {"value": "other"},
                ],
            }
        },
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Contributor.model_rebuild()
CreditMetadata.model_rebuild()
Description.model_rebuild()
EventDate.model_rebuild()
FundingReference.model_rebuild()
License.model_rebuild()
Metadata.model_rebuild()
Organization.model_rebuild()
PermanentID.model_rebuild()
Title.model_rebuild()
