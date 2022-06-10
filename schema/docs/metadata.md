
# metadata


**metamodel version:** 1.7.0

**version:** None





### Classes

 * [Contributor](Contributor.md)
 * [Dataset](Dataset.md)
 * [FundingReference](FundingReference.md)
 * [ResolvablePID](ResolvablePID.md)

### Mixins


### Slots

 * [➞affiliation](contributor__affiliation.md) - organisation that the contributor is associated with
 * [➞contributor_role](contributor__contributor_role.md) - should be a term from either CRedIT or DataCite
 * [➞first_name](contributor__first_name.md) - given name
 * [➞full_name](contributor__full_name.md) - Full name of the contributor
 * [➞last_name](contributor__last_name.md) - family name
 * [➞orcid](contributor__orcid.md) - ORCID
 * [➞access_date](dataset__access_date.md) - for unversioned datasets, the date of access of the dataset
 * [➞contributors](dataset__contributors.md) - people and/or organisations responsible for generating the dataset
 * [➞funding_references](dataset__funding_references.md) - funding sources for the dataset
 * [➞resolvable_persistent_identifiers](dataset__resolvable_persistent_identifiers.md) - unique IDs used to access the dataset or any ancestral datasets
 * [➞title](dataset__title.md) - formal title of the data set
 * [➞version](dataset__version.md) - dataset version (if available)
 * [➞award_id](fundingReference__award_id.md) - code assigned by the funder to the grant or award
 * [➞award_title](fundingReference__award_title.md) - human-readable title of the grant or award
 * [➞award_uri](fundingReference__award_uri.md) - URI for the award
 * [➞funder_id](fundingReference__funder_id.md) - ID for the funding entity
 * [➞funder_name](fundingReference__funder_name.md) - human-readable funding body name
 * [➞description](resolvablePID__description.md) - brief description of what the ID links to
 * [➞id](resolvablePID__id.md) - a CURIE (compact URI)
 * [➞repository](resolvablePID__repository.md) - entity within which the RPI is held
 * [➞uri](resolvablePID__uri.md) - URI for a resource

### Enums


### Subsets


### Types


#### Built in

 * **Bool**
 * **Decimal**
 * **ElementIdentifier**
 * **NCName**
 * **NodeIdentifier**
 * **URI**
 * **URIorCURIE**
 * **XSDDate**
 * **XSDDateTime**
 * **XSDTime**
 * **float**
 * **int**
 * **str**

#### Defined

 * [Boolean](types/Boolean.md)  (**Bool**)  - A binary (true or false) value
 * [Date](types/Date.md)  (**XSDDate**)  - a date (year, month and day) in an idealized calendar
 * [Datetime](types/Datetime.md)  (**XSDDateTime**)  - The combination of a date and time
 * [Decimal](types/Decimal.md)  (**Decimal**)  - A real number with arbitrary precision that conforms to the xsd:decimal specification
 * [Double](types/Double.md)  (**float**)  - A real number that conforms to the xsd:double specification
 * [Float](types/Float.md)  (**float**)  - A real number that conforms to the xsd:float specification
 * [Integer](types/Integer.md)  (**int**)  - An integer
 * [Ncname](types/Ncname.md)  (**NCName**)  - Prefix part of CURIE
 * [Nodeidentifier](types/Nodeidentifier.md)  (**NodeIdentifier**)  - A URI, CURIE or BNODE that represents a node in a model.
 * [Objectidentifier](types/Objectidentifier.md)  (**ElementIdentifier**)  - A URI or CURIE that represents an object in the model.
 * [String](types/String.md)  (**str**)  - A character string
 * [Time](types/Time.md)  (**XSDTime**)  - A time object represents a (local) time of day, independent of any particular day
 * [Uri](types/Uri.md)  (**URI**)  - a complete URI
 * [Uriorcurie](types/Uriorcurie.md)  (**URIorCURIE**)  - a URI or a CURIE
