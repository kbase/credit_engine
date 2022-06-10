# Auto generated from metadata.yaml by pythongen.py version: 0.9.0
# Generation date: 2022-06-10T10:36:52
# Schema: metadata
#
# id: https://kbase/credit_engine/schema/metadata
# description:
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import sys
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import String

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
ORCID = CurieNamespace('ORCID', 'https://orcid.org/')
CREDIT = CurieNamespace('credit', 'https://casrai.org/credit/')
DATACITE = CurieNamespace('datacite', 'https://support.datacite.org/docs/schema-optional-properties-v44')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
SCHEMA = CurieNamespace('schema', 'http://schema.org/')
DEFAULT_ = CurieNamespace('', 'https://kbase/credit_engine/schema/metadata/')


# Types

# Class references
class ContributorOrcid(extended_str):
    pass


class ResolvablePIDId(extended_str):
    pass


@dataclass
class Dataset(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://kbase/credit_engine/schema/metadata/Dataset")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Dataset"
    class_model_uri: ClassVar[URIRef] = URIRef("https://kbase/credit_engine/schema/metadata/Dataset")

    title: str = None
    version: Optional[str] = None
    access_date: Optional[str] = None
    contributors: Optional[Union[Dict[Union[str, ContributorOrcid], Union[dict, "Contributor"]], List[Union[dict, "Contributor"]]]] = empty_dict()
    resolvable_persistent_identifiers: Optional[Union[Dict[Union[str, ResolvablePIDId], Union[dict, "ResolvablePID"]], List[Union[dict, "ResolvablePID"]]]] = empty_dict()
    funding_references: Optional[Union[Union[dict, "FundingReference"], List[Union[dict, "FundingReference"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.title):
            self.MissingRequiredField("title")
        if not isinstance(self.title, str):
            self.title = str(self.title)

        if self.version is not None and not isinstance(self.version, str):
            self.version = str(self.version)

        if self.access_date is not None and not isinstance(self.access_date, str):
            self.access_date = str(self.access_date)

        self._normalize_inlined_as_list(slot_name="contributors", slot_type=Contributor, key_name="orcid", keyed=True)

        self._normalize_inlined_as_list(slot_name="resolvable_persistent_identifiers", slot_type=ResolvablePID, key_name="id", keyed=True)

        if not isinstance(self.funding_references, list):
            self.funding_references = [self.funding_references] if self.funding_references is not None else []
        self.funding_references = [v if isinstance(v, FundingReference) else FundingReference(**as_dict(v)) for v in self.funding_references]

        super().__post_init__(**kwargs)


@dataclass
class Contributor(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://kbase/credit_engine/schema/metadata/Contributor")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Contributor"
    class_model_uri: ClassVar[URIRef] = URIRef("https://kbase/credit_engine/schema/metadata/Contributor")

    orcid: Union[str, ContributorOrcid] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    affiliation: Optional[str] = None
    contributor_role: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.orcid):
            self.MissingRequiredField("orcid")
        if not isinstance(self.orcid, ContributorOrcid):
            self.orcid = ContributorOrcid(self.orcid)

        if self.first_name is not None and not isinstance(self.first_name, str):
            self.first_name = str(self.first_name)

        if self.last_name is not None and not isinstance(self.last_name, str):
            self.last_name = str(self.last_name)

        if self.full_name is not None and not isinstance(self.full_name, str):
            self.full_name = str(self.full_name)

        if self.affiliation is not None and not isinstance(self.affiliation, str):
            self.affiliation = str(self.affiliation)

        if self.contributor_role is not None and not isinstance(self.contributor_role, str):
            self.contributor_role = str(self.contributor_role)

        super().__post_init__(**kwargs)


@dataclass
class FundingReference(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://kbase/credit_engine/schema/metadata/FundingReference")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "FundingReference"
    class_model_uri: ClassVar[URIRef] = URIRef("https://kbase/credit_engine/schema/metadata/FundingReference")

    funder_name: str = None
    funder_id: Optional[str] = None
    award_id: Optional[str] = None
    award_title: Optional[str] = None
    award_uri: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.funder_name):
            self.MissingRequiredField("funder_name")
        if not isinstance(self.funder_name, str):
            self.funder_name = str(self.funder_name)

        if self.funder_id is not None and not isinstance(self.funder_id, str):
            self.funder_id = str(self.funder_id)

        if self.award_id is not None and not isinstance(self.award_id, str):
            self.award_id = str(self.award_id)

        if self.award_title is not None and not isinstance(self.award_title, str):
            self.award_title = str(self.award_title)

        if self.award_uri is not None and not isinstance(self.award_uri, str):
            self.award_uri = str(self.award_uri)

        super().__post_init__(**kwargs)


@dataclass
class ResolvablePID(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = URIRef("https://kbase/credit_engine/schema/metadata/ResolvablePID")
    class_class_curie: ClassVar[str] = None
    class_name: ClassVar[str] = "Resolvable_PID"
    class_model_uri: ClassVar[URIRef] = URIRef("https://kbase/credit_engine/schema/metadata/ResolvablePID")

    id: Union[str, ResolvablePIDId] = None
    uri: Optional[str] = None
    description: Optional[str] = None
    repository: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.id):
            self.MissingRequiredField("id")
        if not isinstance(self.id, ResolvablePIDId):
            self.id = ResolvablePIDId(self.id)

        if self.uri is not None and not isinstance(self.uri, str):
            self.uri = str(self.uri)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.repository is not None and not isinstance(self.repository, str):
            self.repository = str(self.repository)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.dataset__title = Slot(uri=DEFAULT_.title, name="dataset__title", curie=DEFAULT_.curie('title'),
                   model_uri=DEFAULT_.dataset__title, domain=None, range=str)

slots.dataset__version = Slot(uri=DEFAULT_.version, name="dataset__version", curie=DEFAULT_.curie('version'),
                   model_uri=DEFAULT_.dataset__version, domain=None, range=Optional[str])

slots.dataset__access_date = Slot(uri=DEFAULT_.access_date, name="dataset__access_date", curie=DEFAULT_.curie('access_date'),
                   model_uri=DEFAULT_.dataset__access_date, domain=None, range=Optional[str])

slots.dataset__contributors = Slot(uri=DEFAULT_.contributors, name="dataset__contributors", curie=DEFAULT_.curie('contributors'),
                   model_uri=DEFAULT_.dataset__contributors, domain=None, range=Optional[Union[Dict[Union[str, ContributorOrcid], Union[dict, Contributor]], List[Union[dict, Contributor]]]])

slots.dataset__resolvable_persistent_identifiers = Slot(uri=DEFAULT_.resolvable_persistent_identifiers, name="dataset__resolvable_persistent_identifiers", curie=DEFAULT_.curie('resolvable_persistent_identifiers'),
                   model_uri=DEFAULT_.dataset__resolvable_persistent_identifiers, domain=None, range=Optional[Union[Dict[Union[str, ResolvablePIDId], Union[dict, ResolvablePID]], List[Union[dict, ResolvablePID]]]])

slots.dataset__funding_references = Slot(uri=DEFAULT_.funding_references, name="dataset__funding_references", curie=DEFAULT_.curie('funding_references'),
                   model_uri=DEFAULT_.dataset__funding_references, domain=None, range=Optional[Union[Union[dict, FundingReference], List[Union[dict, FundingReference]]]])

slots.contributor__orcid = Slot(uri=DEFAULT_.orcid, name="contributor__orcid", curie=DEFAULT_.curie('orcid'),
                   model_uri=DEFAULT_.contributor__orcid, domain=None, range=URIRef)

slots.contributor__first_name = Slot(uri=DEFAULT_.first_name, name="contributor__first_name", curie=DEFAULT_.curie('first_name'),
                   model_uri=DEFAULT_.contributor__first_name, domain=None, range=Optional[str])

slots.contributor__last_name = Slot(uri=DEFAULT_.last_name, name="contributor__last_name", curie=DEFAULT_.curie('last_name'),
                   model_uri=DEFAULT_.contributor__last_name, domain=None, range=Optional[str])

slots.contributor__full_name = Slot(uri=SCHEMA.name, name="contributor__full_name", curie=SCHEMA.curie('name'),
                   model_uri=DEFAULT_.contributor__full_name, domain=None, range=Optional[str])

slots.contributor__affiliation = Slot(uri=DEFAULT_.affiliation, name="contributor__affiliation", curie=DEFAULT_.curie('affiliation'),
                   model_uri=DEFAULT_.contributor__affiliation, domain=None, range=Optional[str])

slots.contributor__contributor_role = Slot(uri=DEFAULT_.contributor_role, name="contributor__contributor_role", curie=DEFAULT_.curie('contributor_role'),
                   model_uri=DEFAULT_.contributor__contributor_role, domain=None, range=Optional[str])

slots.fundingReference__funder_name = Slot(uri=DEFAULT_.funder_name, name="fundingReference__funder_name", curie=DEFAULT_.curie('funder_name'),
                   model_uri=DEFAULT_.fundingReference__funder_name, domain=None, range=str)

slots.fundingReference__funder_id = Slot(uri=DEFAULT_.funder_id, name="fundingReference__funder_id", curie=DEFAULT_.curie('funder_id'),
                   model_uri=DEFAULT_.fundingReference__funder_id, domain=None, range=Optional[str])

slots.fundingReference__award_id = Slot(uri=DEFAULT_.award_id, name="fundingReference__award_id", curie=DEFAULT_.curie('award_id'),
                   model_uri=DEFAULT_.fundingReference__award_id, domain=None, range=Optional[str])

slots.fundingReference__award_title = Slot(uri=DEFAULT_.award_title, name="fundingReference__award_title", curie=DEFAULT_.curie('award_title'),
                   model_uri=DEFAULT_.fundingReference__award_title, domain=None, range=Optional[str])

slots.fundingReference__award_uri = Slot(uri=DEFAULT_.award_uri, name="fundingReference__award_uri", curie=DEFAULT_.curie('award_uri'),
                   model_uri=DEFAULT_.fundingReference__award_uri, domain=None, range=Optional[str])

slots.resolvablePID__id = Slot(uri=DEFAULT_.id, name="resolvablePID__id", curie=DEFAULT_.curie('id'),
                   model_uri=DEFAULT_.resolvablePID__id, domain=None, range=URIRef)

slots.resolvablePID__uri = Slot(uri=DEFAULT_.uri, name="resolvablePID__uri", curie=DEFAULT_.curie('uri'),
                   model_uri=DEFAULT_.resolvablePID__uri, domain=None, range=Optional[str])

slots.resolvablePID__description = Slot(uri=SCHEMA.description, name="resolvablePID__description", curie=SCHEMA.curie('description'),
                   model_uri=DEFAULT_.resolvablePID__description, domain=None, range=Optional[str])

slots.resolvablePID__repository = Slot(uri=DEFAULT_.repository, name="resolvablePID__repository", curie=DEFAULT_.curie('repository'),
                   model_uri=DEFAULT_.resolvablePID__repository, domain=None, range=Optional[str])