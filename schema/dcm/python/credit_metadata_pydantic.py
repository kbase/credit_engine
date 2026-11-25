from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Literal, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer,
)


metamodel_version = "1.12.0"
version = "0.0.8"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias=True,
        validate_by_name=True,
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
        "default_prefix": "dcm",
        "default_range": "string",
        "description": "The Dataset Citation Metadata (DCM) schema is designed to "
        "capture accurate credit (citation) information for scientific "
        "datasets whilst maintaining compatibility with DOI minting "
        "authorities such as [DataCite](https://datacite.org), "
        "[Crossref](https://www.crossref.org), and the US Department "
        "of Energy's [Office of Scientific and Technical "
        "Information](https://www.osti.gov).\n"
        "\n"
        "The schema is based heavily on the [DataCite Metadata "
        "Schema](https://schema.datacite.org) and "
        "[Commonmeta](https://docs.commonmeta.org), with some "
        "alterations and additions to allow more accurate capture of "
        "dataset-relevant information.\n"
        "\n"
        "Schema documentation is available at "
        "https://kbase.github.io/credit_engine/.\n",
        "id": "https://kbase.github.io/credit_engine/linkml/credit_metadata",
        "imports": ["components", "linkml:types"],
        "name": "credit_metadata",
        "prefixes": {
            "Crossref": {"prefix_prefix": "Crossref", "prefix_reference": "https://crossref.org/"},
            "DOI": {"prefix_prefix": "DOI", "prefix_reference": "http://identifiers.org/doi/"},
            "DataCite": {"prefix_prefix": "DataCite", "prefix_reference": "http://purl.org/spar/datacite/"},
            "JGI": {"prefix_prefix": "JGI", "prefix_reference": "https://data.jgi.doe.gov/search/"},
            "ORCID": {"prefix_prefix": "ORCID", "prefix_reference": "http://identifiers.org/orcid/"},
            "OSTI.ARTICLE": {"prefix_prefix": "OSTI.ARTICLE", "prefix_reference": "https://www.osti.gov/biblio/"},
            "biolink": {"prefix_prefix": "biolink", "prefix_reference": "https://w3id.org/biolink/vocab/"},
            "commonmeta": {"prefix_prefix": "commonmeta", "prefix_reference": "https://commonmeta.org/"},
            "dcm": {"prefix_prefix": "dcm", "prefix_reference": "https://kbase.github.io/credit_engine/linkml/"},
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

    contact_person = "contact_person"
    """
    Person with knowledge of how to access, troubleshoot, or otherwise field issues related to the resource. May also be "Point of Contact" in organisation that controls access to the resource, if that organisation is different from Publisher, Distributor, Data Manager.
    """
    data_collector = "data_collector"
    """
    Person/institution responsible for finding, gathering/collecting data under the guidelines of the author(s) or Principal Investigator (PI). May also use when crediting survey conductors, interviewers, event or condition observers, person responsible for monitoring key instrument data.
    """
    data_curator = "data_curator"
    """
    Person tasked with reviewing, enhancing, cleaning, or standardizing metadata and the associated data submitted for storage, use, and maintenance within a data centre or repository. While the "DataManager" is concerned with digital maintenance, the DataCurator's role encompasses quality assurance focused on content and metadata. This includes checking whether the submitted dataset is complete, with all files and components as described by submitter, whether the metadata is standardized to appropriate systems and schema, whether specialized metadata is needed to add value and ensure access across disciplines, and determining how the metadata might map to search engines, database products, and automated feeds.
    """
    data_manager = "data_manager"
    """
    Person (or organisation with a staff of data managers, such as a data centre) responsible for maintaining the finished resource. The work done by this person or organisation ensures that the resource is periodically "refreshed" in terms of software/hardware support, is kept available or is protected from unauthorized access, is stored in accordance with industry standards, and is handled in accordance with the records management requirements applicable to it.
    """
    distributor = "distributor"
    """
    Institution tasked with responsibility to generate/disseminate copies of the resource in either electronic or print form. Works stored in more than one archive/repository may credit each as a distributor.
    """
    editor = "editor"
    """
    A person who oversees the details related to the publication format of the resource. N.b. if the Editor is to be credited in place of multiple creators, the Editor's name may be supplied as Creator, with "(Ed.)" appended to the name.
    """
    hosting_institution = "hosting_institution"
    """
    Typically, the organisation allowing the resource to be available on the internet through the provision of its hardware/software/operating support. May also be used for an organisation that stores the data offline. Often a data centre (if that data centre is not the "publisher" of the resource).
    """
    producer = "producer"
    """
    Typically a person or organisation responsible for the artistry and form of a media product. In the data industry, this may be a company "producing" DVDs that package data for future dissemination by a distributor.
    """
    project_leader = "project_leader"
    """
    Person officially designated as head of project team or sub- project team instrumental in the work necessary to development of the resource. The Project Leader is not "removed" from the work that resulted in the resource; he or she remains intimately involved throughout the life of the particular project team.
    """
    project_manager = "project_manager"
    """
    Person officially designated as manager of a project. Project may consist of one or many project teams and sub-teams. The manager of a project normally has more administrative responsibility than actual work involvement.
    """
    project_member = "project_member"
    """
    Person on the membership list of a designated project/project team. This vocabulary may or may not indicate the quality, quantity, or substance of the person's involvement.
    """
    registration_agency = "registration_agency"
    """
    Institution/organisation officially appointed by a Registration Authority to handle specific tasks within a defined area of responsibility. DataCite is a Registration Agency for the International DOI Foundation (IDF). One of DataCite's tasks is to assign DOI prefixes to the allocating agents who then assign the full, specific character string to data clients, provide metadata back to the DataCite registry, etc.
    """
    registration_authority = "registration_authority"
    """
    A standards-setting body from which Registration Agencies obtain official recognition and guidance. The IDF serves as the Registration Authority for the International Standards Organisation (ISO) in the area/domain of Digital Object Identifiers.
    """
    related_person = "related_person"
    """
    A person without a specifically defined role in the development of the resource, but who is someone the author wishes to recognize. This person could be an author's intellectual mentor, a person providing intellectual leadership in the discipline or subject domain, etc.
    """
    researcher = "researcher"
    """
    A person involved in analyzing data or the results of an experiment or formal study. May indicate an intern or assistant to one of the authors who helped with research but who was not so "key" as to be listed as an author. Should be a person, not an institution. Note that a person involved in the gathering of data would fall under the contributorType "data_collector." The researcher may find additional data online and correlate it to the data collected for the experiment or study, for example.
    """
    research_group = "research_group"
    """
    Typically refers to a group of individuals with a lab, department, or division; the group has a particular, defined focus of activity. May operate at a narrower level of scope; may or may not hold less administrative responsibility than a project team.
    """
    rights_holder = "rights_holder"
    """
    Person or institution owning or managing property rights, including intellectual property rights over the resource.
    """
    sponsor = "sponsor"
    """
    Person or organisation that issued a contract or under the auspices of which a work has been written, printed, published, developed, etc. Includes organisations that provide in-kind support, through donation, provision of people or a facility or instrumentation necessary for the development of the resource, etc.
    """
    supervisor = "supervisor"
    """
    Designated administrator over one or more groups/teams working to produce a resource or over one or more steps of a development process.
    """
    translator = "translator"
    """
    Person, organisation or automated system responsible for rendering the content of a resource from one language into another.
    """
    work_package_leader = "work_package_leader"
    """
    A Work Package is a recognized data product, not all of which is included in publication. The package, instead, may include notes, discarded documents, etc. The Work Package Leader is responsible for ensuring the comprehensive contents, versioning, and availability of the Work Package during the development of the resource.
    """
    other = "other"
    """
    Any person or institution making a significant contribution to the development and/or maintenance of the resource, but whose contribution does not "fit" other controlled vocabulary for contributorType. Could be a photographer, artist, or writer whose contribution helped to publicize the resource (as opposed to creating it), a reviewer of the resource, someone providing administrative services to the author (such as depositing updates into an online repository, analysing usage, etc.), or one of many other roles.
    """
    author = "author"
    """
    A creator of the resource. Equivalent to a DataCite creator.
    """
    chair = "chair"
    """
    Person who chairs a conference, committee, or other body responsible for the resource.
    """
    corresponding_author = "corresponding_author"
    """
    The author responsible for correspondence about the resource.
    """
    maintainer = "maintainer"
    """
    Person or organisation responsible for the ongoing maintenance of the resource, e.g. a software package or a database.
    """
    reader = "reader"
    """
    Person who reads the resource aloud, e.g. for an audio recording.
    """
    reviewer = "reviewer"
    """
    Person who reviews the resource, e.g. a peer reviewer.
    """
    review_assistant = "review_assistant"
    """
    Person who assists a reviewer.
    """
    external_reviewer = "reviewer_external"
    """
    Reviewer from outside the organisation or editorial board responsible for the review process.
    """
    statistical_reviewer = "stats_reviewer"
    """
    Reviewer who assesses the statistical methods and analysis used in the resource.
    """
    conceptualization = "conceptualization"
    """
    Ideas; formulation or evolution of overarching research goals and aims.
    """
    data_curation = "data_curation"
    """
    Management activities to annotate (produce metadata), scrub data and maintain research data (including software code, where it is necessary for interpreting the data itself) for initial use and later re-use.
    """
    formal_analysis = "formal_analysis"
    """
    Application of statistical, mathematical, computational, or other formal techniques to analyze or synthesize study data.
    """
    funding_acquisition = "funding_acquisition"
    """
    Acquisition of the financial support for the project leading to this publication.
    """
    investigation = "investigation"
    """
    Conducting a research and investigation process, specifically performing the experiments, or data/evidence collection.
    """
    methodology = "methodology"
    """
    Development or design of methodology; creation of models.
    """
    project_administration = "project_administration"
    """
    Management and coordination responsibility for the research activity planning and execution.
    """
    resources = "resources"
    """
    Provision of study materials, reagents, materials, patients, laboratory samples, animals, instrumentation, computing resources, or other analysis tools.
    """
    software = "software"
    """
    Programming, software development; designing computer programs; implementation of the computer code and supporting algorithms; testing of existing code components.
    """
    supervision = "supervision"
    """
    Oversight and leadership responsibility for the research activity planning and execution, including mentorship external to the core team.
    """
    validation = "validation"
    """
    Verification, whether as a part of the activity or separate, of the overall replication/reproducibility of results/experiments and other research outputs.
    """
    visualization = "visualization"
    """
    Preparation, creation and/or presentation of the published work, specifically visualization/data presentation.
    """
    writing_original_draft = "writing_original_draft"
    """
    Preparation, creation and/or presentation of the published work, specifically writing the initial draft (including substantive translation).
    """
    writing_review_andSOLIDUSor_editing = "writing_review_editing"
    """
    Preparation, creation and/or presentation of the published work by those from the original research group, specifically critical review, commentary or revision -- including pre- or post-publication stages.
    """


class ContributorType(str, Enum):
    """
    The type of contributor being represented.
    """

    Person = "Person"
    """
    A person.
    """
    Organization = "Organization"
    """
    An organization.
    """


class DescriptionType(str, Enum):
    """
    The type of text being represented.
    """

    abstract = "abstract"
    """
    A brief description of the resource and the context in which the resource was created.
    """
    description = "description"
    summary = "summary"
    methods = "methods"
    """
    The methodology employed for the study or research.
    """
    series_information = "series_information"
    """
    Information about a repeating series, such as volume, issue, or number.
    """
    table_of_contents = "table_of_contents"
    """
    A listing of the table of contents.
    """
    technical_info = "technical_info"
    """
    Detailed information that may be associated with design, implementation, operation, use, and/or maintenance of a process, system, or instrument. For software, this may include the contents of a README file.
    """
    acknowledgement = "acknowledgement"
    """
    Acknowledgement of contributions to the resource that are not otherwise credited.
    """
    accessibility_statement = "accessibility_statement"
    """
    Statement about the accessibility of the resource.
    """
    ai_use_statement = "ai_use_statement"
    """
    Statement about the use of artificial intelligence tools in the creation of the resource.
    """
    conflict_of_interest_statement = "conflict_of_interest_statement"
    """
    Statement disclosing any competing interests of the creators.
    """
    copyright_statement = "copyright_statement"
    """
    Statement of copyright for the resource.
    """
    data_availability_statement = "data_availability_statement"
    """
    Statement about where the data underlying the resource can be accessed, and any conditions of access.
    """
    ethics_statement = "ethics_statement"
    """
    Statement about ethical approval or ethical considerations for the work.
    """
    funding_statement = "funding_statement"
    """
    Free text statement of the funding received for the work. Use 'funding' for structured funding information.
    """
    versioning_statement = "versioning_statement"
    """
    Statement describing the version of the resource and how it differs from other versions.
    """
    other = "other"
    """
    Other description information that does not fit into an existing category.
    """


class EventType(str, Enum):
    """
    The type of date being represented.
    """

    accepted = "accepted"
    """
    The date that the publisher accepted the resource into their system. To indicate the start of an embargo period, use Submitted or Accepted, as appropriate.

    """
    accessed = "accessed"
    """
    The date the resource was accessed, e.g. when the resource content was retrieved for use in another resource.

    """
    approved = "approved"
    """
    The date on which a dissertation was accepted by the institution awarding the degree, a report was approved, or a standard was accepted.

    """
    available = "available"
    """
    The date the resource is made publicly available. To indicate the end of an embargo period, use Available.

    """
    copyrighted = "copyrighted"
    """
    The specific, documented date at which the resource receives a copyrighted status, if applicable.

    """
    collected = "collected"
    """
    The date or date range in which the resource content was collected. To indicate precise or particular timeframes in which research was conducted.

    """
    coverage = "coverage"
    """
    The date or date range that the content of the resource is about, e.g. the time period covered by a set of observations or a report.

    """
    created = "created"
    """
    The date the resource itself was put together; this could refer to a timeframe in ancient history, be a date range or a single date for a final component, e.g., the finalized file with all of the data.

    """
    issued = "issued"
    """
    The date that the resource is published or distributed e.g. to a data centre

    """
    submitted = "submitted"
    """
    The date the creator submits the resource to the publisher. This could be different from Accepted if the publisher then applies a selection process. To indicate the start of an embargo period, use Submitted or Accepted, as appropriate.

    """
    updated = "updated"
    """
    The date of the last update to the resource, when the resource is being added to.

    """
    valid = "valid"
    """
    The date (or date range) during which the dataset or resource is accurate.

    """
    withdrawn = "withdrawn"
    """
    The date the resource is removed.

    """
    other = "other"


class RelationshipType(str, Enum):
    """
    The relationship between two entities. For example, when a PermanentID class is used to represent objects in the CreditMetadata field 'related_identifiers', the 'relationship_type' field captures the relationship between the resource being registered (A) and this ID (B).
    """

    based_on_data = "based_on_data"
    cites = "cites"
    """
    Indicates that A includes B in a citation.
    """
    collects = "collects"
    """
    Indicates that A is used to collect B, e.g. an instrument (A) used to collect a dataset (B).
    """
    compiles = "compiles"
    """
    Indicates B is the result of a compile or creation event using A. May be used for software and text, as a compiler can be a computer program or a person.
    """
    continues = "continues"
    """
    Indicates A is a continuation of the work B.
    """
    describes = "describes"
    """
    Indicates A describes B.
    """
    documents = "documents"
    """
    Indicates A is documentation about B; e.g. points to software documentation.
    """
    finances = "finances"
    has_comment = "has_comment"
    has_derivation = "has_derivation"
    has_expression = "has_expression"
    has_format = "has_format"
    has_manifestation = "has_manifestation"
    has_manuscript = "has_manuscript"
    has_metadata = "has_metadata"
    """
    Indicates resource A has additional metadata B.
    """
    has_part = "has_part"
    """
    Indicates A includes the part B. Primarily this relation is applied to container-contained type relationships. May be used for individual software modules; note that code repository-to-version relationships should be modeled using IsVersionOf and HasVersion.
    """
    has_preprint = "has_preprint"
    has_related_material = "has_related_material"
    has_reply = "has_reply"
    has_review = "has_review"
    has_translation = "has_translation"
    """
    Indicates B is a translation of A.
    """
    has_version = "has_version"
    """
    Indicates A has a version (B). The registered resource such as a software package or code repository has a versioned instance (indicates A has the instance B) e.g. it may be used to relate an un-versioned code repository to one of its specific software versions.
    """
    is_based_on = "is_based_on"
    is_basis_for = "is_basis_for"
    is_cited_by = "is_cited_by"
    """
    Indicates that B includes A in a citation.
    """
    is_collected_by = "is_collected_by"
    """
    Indicates that A is collected by B, e.g. a dataset (A) collected using an instrument (B).
    """
    is_comment_on = "is_comment_on"
    is_compiled_by = "is_compiled_by"
    """
    Indicates B is used to compile or create A. May be used for software and text, as a compiler can be a computer program or a person.
    """
    is_continued_by = "is_continued_by"
    """
    Indicates A is continued by the work B.
    """
    is_data_basis_for = "is_data_basis_for"
    is_derived_from = "is_derived_from"
    """
    Indicates B is a source upon which A is based. IsDerivedFrom should be used for a resource that is a derivative of an original resource. For example, 'A isDerivedFrom B' could describe a dataset (A) derived from a larger dataset (B) where data values have been manipulated from their original state.
    """
    is_described_by = "is_described_by"
    """
    Indicates A is described by B.
    """
    is_documented_by = "is_documented_by"
    """
    Indicates B is documentation about/explaining A; e.g. points to software documentation.
    """
    is_expression_of = "is_expression_of"
    is_financed_by = "is_financed_by"
    is_format_of = "is_format_of"
    is_identical_to = "is_identical_to"
    """
    Indicates that A is identical to B, for use when there is a need to register two separate instances of the same resource. Should be used for a resource that is the same as the registered resource but is saved in another location, e.g. another institution.
    """
    is_manifestation_of = "is_manifestation_of"
    is_manuscript_of = "is_manuscript_of"
    is_metadata_for = "is_metadata_for"
    """
    Indicates additional metadata A for a resource B.
    """
    is_new_version_of = "is_new_version_of"
    """
    Indicates A is a new edition of B, where the new edition has been modified or updated.
    """
    is_obsoleted_by = "is_obsoleted_by"
    """
    Indicates A is replaced by B.
    """
    is_original_form_of = "is_original_form_of"
    """
    Indicates A is the original form of B. May be used for different software operating systems or compiler formats, for example.
    """
    is_part_of = "is_part_of"
    """
    Indicates A is a portion of B; may be used for elements of a series. Primarily this relation is applied to container-contained type relationships. May be used for individual software modules; note that code repository-to-version relationships should be modeled using IsVersionOf and HasVersion.
    """
    is_preprint_of = "is_preprint_of"
    is_previous_version_of = "is_previous_version_of"
    """
    Indicates A is a previous edition of B.
    """
    is_published_in = "is_published_in"
    """
    Indicates A is published inside B, but is independent of other things published inside of B.
    """
    is_referenced_by = "is_referenced_by"
    """
    Indicates A is used as a source of information by B.
    """
    is_related_material = "is_related_material"
    is_replaced_by = "is_replaced_by"
    is_reply_to = "is_reply_to"
    is_required_by = "is_required_by"
    """
    Indicates A is required by B. May be used to indicate software dependencies.
    """
    is_review_of = "is_review_of"
    is_reviewed_by = "is_reviewed_by"
    """
    Indicates that A is reviewed by B.
    """
    is_same_as = "is_same_as"
    is_source_of = "is_source_of"
    """
    Indicates A is a source upon which B is based. IsSourceOf is the original resource from which a derivative resource was created. For example, 'A isSourceOf B' could describe a dataset (A) which acts as the source of a derived dataset (B) where the values have been manipulated.
    """
    is_supplement_to = "is_supplement_to"
    """
    Indicates that A is a supplement to B.
    """
    is_supplemented_by = "is_supplemented_by"
    """
    Indicates that B is a supplement to A.
    """
    is_translation_of = "is_translation_of"
    """
    Indicates A is a translation of B.
    """
    is_variant_form_of = "is_variant_form_of"
    """
    Indicates A is a variant or different form of B. Use for a different form of one thing. May be used for different software operating systems or compiler formats, for example.
    """
    is_version_of = "is_version_of"
    """
    Indicates A is a version of B. The registered resource is an instance of a target resource (indicates that A is an instance of B) e.g. it may be used to relate a specific version of a software package to its software code repository.
    """
    obsoletes = "obsoletes"
    """
    Indicates A replaces B.
    """
    other = "other"
    """
    Indicates A is related to B in a way not covered by the other relationship types. Describe the relationship in the 'relationship_type_information' field.
    """
    references = "references"
    """
    Indicates B is used as a source of information for A.
    """
    replaces = "replaces"
    requires = "requires"
    """
    Indicates A requires B. May be used to indicate software dependencies.
    """
    reviews = "reviews"
    """
    Indicates that A is a review of B.
    """
    unknown = "unknown"
    """
    The relationship between subject and object is unknown.
    """


class ResourceType(str, Enum):
    """
        The type of resource being represented.

    Values combine the [DataCite resourceTypeGeneral](https://datacite-metadata-schema.readthedocs.io/en/4.7/appendices/appendix-1/resourceTypeGeneral/) vocabulary (v4.7) with the resource types used by [Commonmeta](https://docs.commonmeta.org), Crossref, and OSTI. Where a resource type exists in DataCite, the DataCite term is used.

    """

    article = "article"
    """
    An article not published in a journal or proceedings, e.g. a magazine or newspaper article.
    """
    audiovisual = "audiovisual"
    """
    A series of visual representations imparting an impression of motion when shown in succession. May or may not include sound.
    """
    award = "award"
    """
    Funding or support provided to an individual or organization to conduct research or academic work, e.g. a grant.
    """
    blog = "blog"
    """
    A blog; a collection of blog posts.
    """
    blog_post = "blog_post"
    """
    A single post in a blog.
    """
    book = "book"
    """
    A medium for recording information in the form of writing or images, typically composed of many pages bound together and protected by a cover.
    """
    book_chapter = "book_chapter"
    """
    One of the main divisions of a book.
    """
    book_part = "book_part"
    """
    A part of a book that is larger than a chapter.
    """
    book_section = "book_section"
    """
    A section of a book that is smaller than a chapter.
    """
    book_series = "book_series"
    """
    A series of books.
    """
    book_set = "book_set"
    """
    A set of books published together, e.g. a multi-volume work.
    """
    collection = "collection"
    """
    An aggregation of resources, which may encompass collections of one resource type as well as those of mixed types.
    """
    component = "component"
    """
    A component of another resource, e.g. a figure, table, or supplementary file.
    """
    computational_notebook = "computational_notebook"
    """
    A virtual notebook environment used for literate programming.
    """
    conference_paper = "conference_paper"
    """
    Article that is written with the goal of being accepted to a conference.
    """
    conference_proceeding = "conference_proceeding"
    """
    Collection of academic papers published in the context of an academic conference.
    """
    data_paper = "data_paper"
    """
    A factual and objective publication with a focused intent to identify and describe specific data, sets of data, or data collections to facilitate discoverability.
    """
    database = "database"
    """
    A database, i.e. an organized collection of datasets or records.
    """
    dataset = "dataset"
    """
    Data encoded in a defined structure.
    """
    dissertation = "dissertation"
    """
    A written essay, treatise, or thesis, especially one written by a candidate for the degree of Doctor of Philosophy.
    """
    document = "document"
    """
    A document that does not fit into the other text-based categories.
    """
    entry = "entry"
    """
    An entry in a reference work, e.g. an encyclopedia or dictionary.
    """
    event = "event"
    """
    A non-persistent, time-based occurrence.
    """
    image = "image"
    """
    A visual representation other than text.
    """
    instrument = "instrument"
    """
    A device, tool or apparatus used to obtain, measure and/or analyze data.
    """
    interactive_resource = "interactive_resource"
    """
    A resource requiring interaction from the user to be understood, executed, or experienced.
    """
    journal = "journal"
    """
    A scholarly publication consisting of articles that is published regularly throughout the year.
    """
    journal_article = "journal_article"
    """
    A written composition on a topic of interest, which forms a separate part of a journal.
    """
    journal_issue = "journal_issue"
    """
    An issue of a journal.
    """
    journal_volume = "journal_volume"
    """
    A volume of a journal.
    """
    letter = "letter"
    """
    A short communication, e.g. a letter to the editor.
    """
    model = "model"
    """
    An abstract, conceptual, graphical, mathematical or visualization model that represents empirical objects, phenomena, or physical processes.
    """
    output_management_plan = "output_management_plan"
    """
    A formal document that outlines how research outputs are to be handled both during a research project and after the project is completed, e.g. a data management plan.
    """
    patent = "patent"
    """
    A patent or patent application.
    """
    peer_review = "peer_review"
    """
    Evaluation of scientific, academic, or professional work by others working in the same field.
    """
    physical_object = "physical_object"
    """
    An inanimate, three-dimensional object or substance, e.g. a physical sample.
    """
    poster = "poster"
    """
    A visual presentation of research, typically displayed at a conference.
    """
    preprint = "preprint"
    """
    A version of a scholarly or scientific paper that precedes formal peer review and publication in a peer-reviewed scholarly or scientific journal.
    """
    presentation = "presentation"
    """
    A set of slides or other material used to deliver a talk.
    """
    proceedings_series = "proceedings_series"
    """
    A series of conference proceedings.
    """
    project = "project"
    """
    A planned endeavor or activity, frequently collaborative, intended to achieve a particular aim using allocated resources such as budget, time, and expertise.
    """
    protocol = "protocol"
    """
    A detailed description of the procedures used in an experiment or study.
    """
    registered_report = "registered_report"
    """
    A study design and analysis plan that is peer reviewed before the research is conducted.
    """
    report = "report"
    """
    A document that presents information in an organized format for a specific audience and purpose, e.g. a technical report.
    """
    report_component = "report_component"
    """
    A component of a report, e.g. a chapter.
    """
    report_series = "report_series"
    """
    A series of reports.
    """
    service = "service"
    """
    An organized system of apparatus, appliances, staff, etc., for supplying some function(s) required by end users.
    """
    software = "software"
    """
    A computer program other than a computational notebook, in either source code (text) or compiled form.
    """
    sound = "sound"
    """
    A resource primarily intended to be heard.
    """
    standard = "standard"
    """
    Something established by authority, custom, or general consent as a model, example, or point of reference.
    """
    study_registration = "study_registration"
    """
    A detailed, time-stamped description of a research plan, often openly shared in a registry or published in a journal before the study is conducted.
    """
    text = "text"
    """
    A resource consisting primarily of words for reading that is not covered by any other textual resource type.
    """
    web_page = "web_page"
    """
    A web page or web site.
    """
    workflow = "workflow"
    """
    A structured series of steps which can be executed to produce a final outcome, allowing users a means to specify and enact their work in a more reproducible manner.
    """
    other = "other"
    """
    A resource that does not fit into any of the other categories. Describe the resource type in the 'resource_type_detail' field.
    """


class TitleType(str, Enum):
    """
    The type of title being represented.
    """

    subtitle = "subtitle"
    """
    Any subtitle for the resource.
    """
    alternative_title = "alternative_title"
    """
    Other title(s) or names for the resource.
    """
    translated_title = "translated_title"
    """
    Translation of the title into another language.
    """
    other = "other"
    """
    Anything that doesn't fit into the above categories.
    """


class Contributor(ConfiguredBaseModel):
    """
    Represents a contributor to the resource.

    Contributors must have a 'contributor_type', either 'Person' or 'Organization', and
    one of the 'name' fields: either 'given_name' and 'family_name' (for a person), or 'name' (for an organization or a person).

    The 'contributor_role' field takes values from the DataCite and CRediT contributor
    roles vocabularies. For more information on these resources and choosing
    appropriate roles, please see the following links:

    DataCite contributor roles: [https://support.datacite.org/docs/datacite-metadata-schema-v44-recommended-and-optional-properties#7a-contributortype](https://support.datacite.org/docs/datacite-metadata-schema-v44-recommended-and-optional-properties#7a-contributortype)

    CRediT contributor role taxonomy: [https://credit.niso.org](https://credit.niso.org).

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
            "from_schema": "https://kbase.github.io/credit_engine/linkml/components",
        }
    )

    contributor_type: Optional[ContributorType] = Field(
        default=None,
        description="""Must be either 'Person' or 'Organization'.""",
        json_schema_extra={
            "linkml_meta": {
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
    contributor_id: Optional[str] = Field(
        default=None,
        description="""Persistent unique identifier for the contributor; this might be an ORCID for an individual, or a ROR ID for an organization.""",
        json_schema_extra={
            "linkml_meta": {
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
    name: Optional[str] = Field(
        default=None,
        description="""Contributor name. For organizations, this should be the full (unabbreviated) name; can also be used for a person if the given name/family name format is not applicable.""",
        json_schema_extra={
            "linkml_meta": {
                "close_mappings": ["OSTI.ARTICLE:author", "OSTI.ARTICLE:contributor"],
                "domain_of": ["Contributor", "License"],
                "exact_mappings": ["JGI:organisms.pi.name", "ORCID:name"],
                "examples": [
                    {"value": "National Institute of Mental Health"},
                    {"value": "Madonna"},
                    {"value": "Ransome the Clown"},
                ],
                "related_mappings": ["DataCite:attributes.creators.name", "DataCite:attributes.contributors.name"],
                "slot_uri": "schema:name",
            }
        },
    )
    given_name: Optional[str] = Field(
        default=None,
        description="""The given name(s) of the contributor.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Contributor"],
                "examples": [{"value": "Marionetta Cecille de la"}, {"value": "Helena"}, {"value": "Hubert George"}],
                "related_mappings": [
                    "DataCite:attributes.contributors.givenName",
                    "DataCite:attributes.creators.givenName",
                ],
            }
        },
    )
    family_name: Optional[str] = Field(
        default=None,
        description="""The family name(s) of the contributor.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Contributor"],
                "examples": [{"value": "Carte-Postale"}, {"value": "Bonham Carter"}, {"value": "Wells"}],
                "related_mappings": [
                    "DataCite:attributes.contributors.familyName",
                    "DataCite:attributes.creators.familyName",
                ],
            }
        },
    )
    affiliations: Optional[list[Organization]] = Field(
        default=None,
        description="""List of organizations with which the contributor is affiliated. For contributors that represent an organization, this may be a parent organization (e.g. KBase, US DOE; Arkin lab, LBNL).""",
        json_schema_extra={
            "linkml_meta": {
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
    contributor_roles: Optional[list[ContributorRole]] = Field(
        default=None,
        description="""List of roles played by the contributor when working on the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "close_mappings": ["ORCID:contributor.role", "OSTI.ARTICLE:contributor.contributorType"],
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
        pattern = re.compile(r"^[a-zA-Z0-9.-_]+:\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid contributor_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid contributor_id format: {v}"
            raise ValueError(err_msg)
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
            "from_schema": "https://kbase.github.io/credit_engine/linkml/components",
        }
    )

    access_timestamp: int = Field(
        default=...,
        description="""Unix timestamp for when the data was retrieved from that source.""",
        json_schema_extra={
            "linkml_meta": {
                "comments": ["This could be added programmatically when updates occur."],
                "domain_of": ["DataSource"],
            }
        },
    )
    source_data_updated: Optional[datetime] = Field(
        default=None,
        description="""The date when the data source was last updated, if available.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["DataSource"]}},
    )
    source_name: Optional[str] = Field(
        default=None,
        description="""Where the data was retrieved from.""",
        json_schema_extra={
            "linkml_meta": {
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
                "domain_of": ["DataSource"],
                "examples": [
                    {"value": "https://figshare.com/articles/dataset/Blue_Hole_Metagenome-assembled_Genomes/12644081"},
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
        {"from_schema": "https://kbase.github.io/credit_engine/linkml/components"}
    )

    description_text: str = Field(
        default=...,
        description="""The text content of the informational element.""",
        json_schema_extra={
            "linkml_meta": {
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
                "domain_of": ["Description"],
                "examples": [{"value": "abstract"}, {"value": "description"}, {"value": "summary"}],
            }
        },
    )


class EventDate(ConfiguredBaseModel):
    """
    Represents an event in the lifecycle of a resource and the date it occurred on.

    See [DataCite documentation on date events](https://support.datacite.org/docs/datacite-metadata-schema-v44-recommended-and-optional-properties#8-date) for more information on the events.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://kbase.github.io/credit_engine/linkml/components"}
    )

    date: str = Field(
        default=...,
        description="""The date associated with the event. The date may be in the format YYYY, YYYY-MM, YYYY-MM-DD, or an ISO 8601 date-time (YYYY-MM-DDThh:mm:ssTZD).

A date range may be given using the [RKMS-ISO8601](https://www.ukoln.ac.uk/metadata/dcmi/collection-RKMS-ISO8601/) notation, e.g. 2020-01-01/2020-06-30. The start of the range may be 'unknown'; the end may be 'unknown' or 'open'. Date ranges are useful for 'collected', 'coverage', and 'valid' events.
""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["EventDate"],
                "examples": [
                    {"value": "2001"},
                    {"value": "2021-05"},
                    {"value": "1998-02-15"},
                    {"value": "2022-05-03T14:21:07Z"},
                    {"value": "2019-04-01/2019-09-30"},
                ],
            }
        },
    )
    event: EventType = Field(
        default=...,
        description="""The nature of the resource-related event that occurred on that date.""",
        json_schema_extra={
            "linkml_meta": {"domain_of": ["EventDate"], "examples": [{"value": "available"}, {"value": "updated"}]}
        },
    )
    event_information: Optional[str] = Field(
        default=None,
        description="""Free text information about the event or date.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["EventDate"],
                "exact_mappings": ["DataCite:attributes.dates.date_information"],
                "examples": [
                    {"value": "Embargo period ended."},
                    {"value": "Samples collected during the 2019 field season."},
                ],
            }
        },
    )

    @field_validator("date")
    def pattern_date(cls, v):
        pattern = re.compile(
            r"^(\d{4}(-\d{2}){0,2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?|unknown)(/(\d{4}(-\d{2}){0,2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?|unknown|open))?$"
        )
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid date format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid date format: {v}"
            raise ValueError(err_msg)
        return v


class FundingReference(ConfiguredBaseModel):
    """
    Represents a funding source for a resource, including the funding body and the grant awarded.

    One (or more) of the fields 'grant_id', 'grant_url', or 'funder.organization_name' is required; others are optional.

    Recommended resources for organization identifiers include:
      - [Research Organization Registry](http://ror.org)
      - [International Standard Name Identifier](https://isni.org)
      - [Crossref Funder Registry](https://www.crossref.org/services/funder-registry/) (to be subsumed into ROR)

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
            "from_schema": "https://kbase.github.io/credit_engine/linkml/components",
        }
    )

    funder: Optional[Organization] = Field(
        default=None,
        description="""The funder for the grant or award.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["FundingReference"], "slot_uri": "schema:funder"}},
    )
    grant_id: Optional[str] = Field(
        default=None,
        description="""Code for the grant, assigned by the funder.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["FundingReference"],
                "exact_mappings": ["DataCite:attributes.funding_references.award_number", "Crossref:message.award"],
                "examples": [{"value": "1296"}, {"value": "CBET-0756451"}, {"value": "DOI:10.46936/10.25585/60000745"}],
                "narrow_mappings": ["OSTI.ARTICLE:award_doi", "OSTI.ARTICLE:award_number"],
                "slot_uri": "schema:identifier",
            }
        },
    )
    grant_title: Optional[str] = Field(
        default=None,
        description="""Title for the grant.""",
        json_schema_extra={
            "linkml_meta": {
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
    grant_url: Optional[str] = Field(
        default=None,
        description="""URL for the grant.""",
        json_schema_extra={
            "linkml_meta": {
                "close_mappings": ["OSTI.ARTICLE:award_doi"],
                "domain_of": ["FundingReference"],
                "exact_mappings": ["DataCite:attributes.funding_references.award_url"],
                "examples": [
                    {"value": "https://genome.jgi.doe.gov/portal/Metanaintenssite/Metanaintenssite.info.html"}
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
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid grant_url format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid grant_url format: {v}"
            raise ValueError(err_msg)
        return v


class License(ConfiguredBaseModel):
    """
    License or rights information for the resource.

    One (or more) of 'id', 'url', or 'name' is required.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "any_of": [
                {"slot_conditions": {"id": {"name": "id", "required": True}}},
                {"slot_conditions": {"url": {"name": "url", "required": True}}},
                {"slot_conditions": {"name": {"name": "name", "required": True}}},
            ],
            "from_schema": "https://kbase.github.io/credit_engine/linkml/components",
        }
    )

    id: Optional[str] = Field(
        default=None,
        description="""String representing the license, from the [SPDX license identifiers](https://spdx.org/licenses/).""",
        json_schema_extra={
            "linkml_meta": {
                "close_mappings": ["DataCite:attributes.rights_list.rights_identifier"],
                "domain_of": ["License", "PermanentID"],
                "exact_mappings": ["commonmeta:license.id"],
                "examples": [{"value": "CC-BY-NC-ND-4.0"}, {"value": "Apache-2.0"}],
            }
        },
    )
    url: Optional[str] = Field(
        default=None,
        description="""URL for the license.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["License", "CreditMetadata"],
                "exact_mappings": [
                    "commonmeta:license.url",
                    "DataCite:attributes.rights_list.rights_uri",
                    "Crossref:message.license.URL",
                ],
                "examples": [{"value": "https://jgi.doe.gov/user-programs/pmo-overview/policies/"}],
            }
        },
    )
    name: Optional[str] = Field(
        default=None,
        description="""Full name of the license or a rights statement, if no SPDX identifier is available. Include version information if applicable.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Contributor", "License"],
                "exact_mappings": ["DataCite:attributes.rights_list.rights"],
                "examples": [
                    {"value": "Creative Commons Attribution 4.0 International"},
                    {"value": "JGI Data Usage Policy"},
                ],
            }
        },
    )


class Metadata(ConfiguredBaseModel):
    """
    Metadata for the credit metadata, including the schema version used, who submitted it, and the date of submission. When the credit metadata for a resource is added or updated, this additional metadata must be provided along with the credit information.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://kbase.github.io/credit_engine/linkml/components"}
    )

    credit_metadata_schema_version: str = Field(
        default=...,
        description="""The version of the credit metadata schema used.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Metadata"],
                "examples": [{"value": "1.1.0"}],
                "slot_uri": "schema:schemaVersion",
            }
        },
    )
    credit_metadata_source: Optional[list[DataSource]] = Field(
        default=None,
        description="""Information about where the credit metadata was sourced from.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Metadata"]}},
    )
    saved_by: str = Field(
        default=...,
        description="""PID for the user who added this entry.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["Metadata"], "slot_uri": "schema:sdPublisher"}},
    )
    timestamp: int = Field(
        default=...,
        description="""Unix timestamp for the addition of this set of credit metadata.""",
        json_schema_extra={
            "linkml_meta": {
                "comments": ["This could be added programmatically when updates occur."],
                "domain_of": ["Metadata"],
                "slot_uri": "schema:sdDatePublished",
            }
        },
    )


class Organization(ConfiguredBaseModel):
    """
    Represents an organization.

    Recommended resources for organization identifiers include:
      - [Research Organization Registry](http://ror.org)
      - [International Standard Name Identifier](https://isni.org)
      - [Crossref Funder Registry](https://www.crossref.org/services/funder-registry/) (to be subsumed into ROR)

    For example, the US DOE would be entered as:
      organization_name: United States Department of Energy
      organization_id:   ROR:01bj3aw27

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"class_uri": "schema:Organization", "from_schema": "https://kbase.github.io/credit_engine/linkml/components"}
    )

    organization_id: Optional[str] = Field(
        default=None,
        description="""Persistent unique identifier for the organization in the format <database name>:<identifier within database>.""",
        json_schema_extra={
            "linkml_meta": {
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
        default=...,
        description="""Common name of the organization; use the name recommended by ROR if possible.""",
        json_schema_extra={
            "linkml_meta": {
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
        pattern = re.compile(r"^[a-zA-Z0-9.-_]+:\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid organization_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid organization_id format: {v}"
            raise ValueError(err_msg)
        return v


class PermanentID(ConfiguredBaseModel):
    """
    Represents a persistent unique identifier for an entity and its relationship to some other entity.

    The 'id' field and 'relationship_type' fields are required.

    The values in the 'relationship_type' field come from controlled vocabularies maintained by DataCite and Crossref. See the documentation links below for more details.

    [DataCite relation types](https://support.datacite.org/docs/datacite-metadata-schema-v44-recommended-and-optional-properties#12b-relationtype)

    [Crossref relation types](https://www.crossref.org/documentation/schema-library/markup-guide-metadata-segments/relationships/)

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://kbase.github.io/credit_engine/linkml/components"}
    )

    id: str = Field(
        default=...,
        description="""Persistent unique ID for an entity. Should be in the format <database name>:<identifier within database>.""",
        json_schema_extra={
            "linkml_meta": {
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
    description: Optional[str] = Field(
        default=None,
        description="""Description of that entity.""",
        json_schema_extra={
            "linkml_meta": {
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
    relationship_type: Optional[RelationshipType] = Field(
        default=None,
        description="""The relationship between the ID and some other entity. For example, when a PermanentID class is used to represent objects in the CreditMetadata field 'related_identifiers', the 'relationship_type' field captures the relationship between the resource being registered and this ID.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PermanentID"],
                "exact_mappings": [
                    "DataCite:attributes.related_identifiers.relation_type",
                    "commonmeta:relations.type",
                    "OSTI.ARTICLE:related_identifiers.relation",
                ],
            }
        },
    )
    relationship_type_information: Optional[str] = Field(
        default=None,
        description="""Free text further describing the relationship, e.g. when the relationship type is 'other'.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["PermanentID"],
                "exact_mappings": ["DataCite:attributes.related_identifiers.relation_type_information"],
                "examples": [{"value": "Raw reads used to generate the assembly."}],
            }
        },
    )

    @field_validator("id")
    def pattern_id(cls, v):
        pattern = re.compile(r"^[a-zA-Z0-9.-_]+:\S")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class Title(ConfiguredBaseModel):
    """
    Represents the title or name of a resource, the type of that title, and the language used (if appropriate).

    The 'title' field is required; 'title_type' is only necessary if the text is not the primary title.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://kbase.github.io/credit_engine/linkml/components"}
    )

    language: Optional[str] = Field(
        default=None,
        description="""The language in which the title is written, using the appropriate IETF BCP-47 notation.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Title", "CreditMetadata"],
                "examples": [{"value": "ru-Cyrl"}, {"value": "fr"}],
            }
        },
    )
    title: str = Field(
        default=...,
        description="""A string used as a title for a resource.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["Title"],
                "exact_mappings": ["DataCite:attributes.titles.title", "Crossref:message.project.project-title.title"],
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


class CreditMetadata(ConfiguredBaseModel):
    """
    Represents the credit metadata associated with an object.

    In the following documentation, 'resource' is used to refer to the object
    that the CM pertains to, for example, a KBase Workspace object; a
    sample from NMDC or ESS-DIVE; sequence data from IMG.

    The 'resource_type' field takes values from the ResourceType enum, which combines
    the [DataCite resourceTypeGeneral](https://datacite-metadata-schema.readthedocs.io/en/4.7/appendices/appendix-1/resourceTypeGeneral/)
    vocabulary with the resource types used by Commonmeta, Crossref, and OSTI. A free
    text description of the resource type can be supplied in 'resource_type_detail'.

    One or more licenses may be supplied. Each license may be given as an URL pointing to licensing information for
    the resource, or using an SPDX license identifier from the list maintained at [https://spdx.org/licenses](https://spdx.org/licenses).

    Required fields are:
    - identifier
    - resource_type
    - versioning information: if the resource does not have an explicit version number,
    one or more dates should be supplied: ideally the date of resource publication and
    the last update (if applicable).
    - contributors (one or more required)
    - titles (one or more required)
    - meta

    The resource_type field is required; if no value is supplied, it is populated
    with 'dataset'.

    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "any_of": [
                {"slot_conditions": {"dates": {"name": "dates", "required": True}}},
                {"slot_conditions": {"version": {"name": "version", "required": True}}},
            ],
            "from_schema": "https://kbase.github.io/credit_engine/linkml/credit_metadata",
            "tree_root": True,
        }
    )

    comment: Optional[list[str]] = Field(
        default=None,
        description="""List of strings of freeform text providing extra information about this credit metadata.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["CreditMetadata"],
                "examples": [{"value": "This comment adds a lot of extra value!"}],
                "slot_uri": "schema:comment",
            }
        },
    )
    content_url: Optional[list[str]] = Field(
        default=None,
        description="""The URL of the content of the resource.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["CreditMetadata"]}},
    )
    contributors: list[Contributor] = Field(
        default=...,
        description="""A list of people and/or organizations who contributed to the resource.""",
        json_schema_extra={
            "linkml_meta": {
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
    dates: Optional[list[EventDate]] = Field(
        default=None,
        description="""A list of relevant lifecycle events for the resource. Note that these dates apply only to the resource itself, and not to the creation or update of the credit metadata record for the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "close_mappings": [
                    "DataCite:attributes.published",
                    "DataCite:attributes.updated",
                    "DataCite:attributes.dates",
                    "ORCID:publicationDate",
                    "OSTI.ARTICLE:publication_date",
                    "Crossref:message.deposited",
                    "commonmeta:date",
                    "Crossref:database_date",
                    "OSTI.ARTICLE:media_embargo_sunset_date",
                ],
                "domain_of": ["CreditMetadata"],
            }
        },
    )
    descriptions: Optional[list[Description]] = Field(
        default=None,
        description="""A brief description or abstract for the resource being represented.""",
        json_schema_extra={
            "linkml_meta": {
                "close_mappings": ["Crossref:abstract", "Crossref:statement_info", "OSTI.ARTICLE:description"],
                "domain_of": ["CreditMetadata"],
                "exact_mappings": ["DataCite:attributes.descriptions", "commonmeta:descriptions"],
                "slot_uri": "schema:description",
            }
        },
    )
    funding: Optional[list[FundingReference]] = Field(
        default=None,
        description="""Funding sources for the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "close_mappings": [
                    "DataCite:attributes.funding_references",
                    "Crossref:Message.project.funding",
                    "OSTI.ARTICLE:awards",
                ],
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
                "comments": ["can generate schema:url from the identifier"],
                "domain_of": ["CreditMetadata"],
                "exact_mappings": ["DataCite:id", "JGI:organisms.grouped_by"],
                "examples": [
                    {"value": "RefSeq:GCF_004214875.1"},
                    {"value": "GenBank:CP035949.1"},
                    {"value": "img.taxon:648028003"},
                ],
                "narrow_mappings": ["OSTI.ARTICLE:osti_id", "OSTI.ARTICLE:doi", "ORCID:doi", "ORCID:url"],
                "slot_uri": "schema:identifier",
            }
        },
    )
    language: Optional[str] = Field(
        default=None,
        description="""The primary language of the resource, using the appropriate IETF BCP-47 notation.""",
        json_schema_extra={
            "linkml_meta": {
                "close_mappings": ["OSTI.ARTICLE:languages"],
                "domain_of": ["Title", "CreditMetadata"],
                "exact_mappings": ["DataCite:attributes.language", "commonmeta:language", "Crossref:message.language"],
                "examples": [{"value": "ru-Cyrl"}, {"value": "en"}, {"value": "fr"}],
                "slot_uri": "schema:inLanguage",
            }
        },
    )
    licenses: Optional[list[License]] = Field(
        default=None,
        description="""Usage licenses or rights statements for the resource. For each license, use one of the SPDX license identifiers or provide a link to the license text if no SPDX ID is available.

Supply more than one license if different licenses apply to different versions or uses of the resource (see 'applies_to'), or if the resource is available under a choice of licenses.
""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["CreditMetadata"],
                "exact_mappings": ["biolink:license", "commonmeta:license"],
                "related_mappings": [
                    "DataCite:attributes.rights_list",
                    "Crossref:message.license",
                    "OSTI.ARTICLE:access_limitations",
                ],
                "slot_uri": "schema:license",
            }
        },
    )
    meta: Optional[Metadata] = Field(
        default=None,
        description="""Metadata for this credit information, including submitter, schema version, and timestamp.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["CreditMetadata"]}},
    )
    publisher: Optional[Organization] = Field(
        default=None,
        description="""The publisher of the resource. For a dataset, this is the repository where it is stored.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["CreditMetadata"],
                "narrow_mappings": ["ORCID:url", "OSTI.ARTICLE:site_url"],
                "slot_uri": "schema:provider",
            }
        },
    )
    related_identifiers: Optional[list[PermanentID]] = Field(
        default=None,
        description="""Other resolvable persistent unique IDs related to the resource.""",
        json_schema_extra={
            "linkml_meta": {
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
        default=ResourceType("dataset"),
        description="""The broad type of the resource. Defaults to 'dataset'.""",
        json_schema_extra={
            "linkml_meta": {
                "close_mappings": ["Crossref:message.type"],
                "domain_of": ["CreditMetadata"],
                "exact_mappings": [
                    "DataCite:attributes.types.resource_type_general",
                    "commonmeta:type",
                    "OSTI.ARTICLE:product_type",
                    "OSTI.ARTICLE:workType",
                    "DataCite:attributes.types.schema_org",
                ],
                "examples": [{"value": "dataset"}, {"value": "software"}, {"value": "workflow"}],
                "ifabsent": "ResourceType(dataset)",
                "narrow_mappings": ["OSTI.ARTICLE:dataset_type"],
                "slot_uri": "schema:@type",
            }
        },
    )
    titles: list[Title] = Field(
        default=...,
        description="""One or more titles for the resource.""",
        json_schema_extra={
            "linkml_meta": {
                "domain_of": ["CreditMetadata"],
                "exact_mappings": ["DataCite:attributes.titles", "ORCID:title", "OSTI.ARTICLE:title"],
            }
        },
    )
    url: Optional[str] = Field(
        default=None,
        description="""The URL of the resource.""",
        json_schema_extra={"linkml_meta": {"domain_of": ["License", "CreditMetadata"]}},
    )
    version: Optional[str] = Field(
        default=None,
        description="""The version of the resource. This must be an absolute version, not a relative version like 'latest'.""",
        json_schema_extra={
            "linkml_meta": {
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
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid identifier format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid identifier format: {v}"
            raise ValueError(err_msg)
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
