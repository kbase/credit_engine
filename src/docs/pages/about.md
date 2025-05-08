# Dataset Citation Metadata

LinkML schema for dataset citation metadata, as used by [KBase](https://kbase.us).

- [Dataset Citation Metadata](#dataset-citation-metadata)
  - [About the Dataset Citation Metadata Schema](#about-the-dataset-citation-metadata-schema)
    - [Required Elements](#required-elements)
    - [Example Dataset Citation](#example-dataset-citation)
    - [Other Elements](#other-elements)
    - [Sources used in Schema Design](#sources-used-in-schema-design)
    - [References](#references)

## About the Dataset Citation Metadata Schema

The Dataset Citation Metadata (DCM) schema is designed to capture accurate credit information for scientific datasets whilst maintaining compatibility with DOI minting authorities such as [DataCite](https://datacite.org), [Crossref](https://www.crossref.org), and the US Department of Energy's [Office of Scientific and Technical Information](https://www.osti.gov).

The schema is based heavily on the [DataCite Metadata Schema](https://schema.datacite.org) and [Commonmeta](https://docs.commonmeta.org), with some alterations and additions to allow more accurate capture of dataset-relevant information.

It aims to satisfy the data citation recommendations published in [Ten simple rules for getting and giving credit for data](https://doi.org/10.1371/journal.pcbi.1010476) [^1] and [Data Citation Guidelines for Earth Science Data, Version 2](https://doi.org/10.6084/m9.figshare.8441816.v1) [^2].


### Required Elements

The core elements required for a data citation are as follows:

- contributor(s): people and/or organisations involved in generating the dataset.

- title: the formal name of the dataset.

- resolvable permanent identifier: a unique, resolvable identifier that can be used to access the data. We recommend the use of [CURIEs (Compact URI)](https://en.wikipedia.org/wiki/CURIE) with prefixes registered at [Bioregistry](https://bioregistry.io), which allows the CURIE to be resolved into the corresponding URI.

- version: the version of the dataset; not all projects provide a version for their datasets, so the publication date of the dataset may be used instead.

- access date: when the dataset was accessed; this is important as datasets may change over time, and not all resources version their datasets.

- repository: organisation that hosts, archives, publishes, distributes, produces, etc., the dataset.


### Example Dataset Citation

Cline, D., R. Armstrong, R. Davis, K. Elder, and G. Liston. 2003. CLPX-Ground: ISA snow depth transects and related measurements ver. 2.0. Edited by M. A. Parsons and M. J. Brodzik. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5060/D4MW2F23. Accessed 2008-05-14.


### Other Elements

The DCM schema also has the capacity to track other dataset-related information, including the funding information and the roles of contributors. These are not necessary for dataset citation but provide a more complete picture of the context for the dataset.

### Sources used in Schema Design

Data producers, consumers, providers, and managers whose data citation information informed the development of this schema include (but are not limited to):

* [Commonmeta](https://docs.commonmeta.org)
* [Contributor Role Taxonomy](https://credit.niso.org/contributor-roles/)
* [Crossref](https://www.crossref.org)
* [DataCite Metadata Schema](https://schema.datacite.org)
* [Environmental Molecular Sciences Laboratory](https://www.emsl.pnnl.gov)
* [Environmental System Science Data Infrastructure for a Virtual Ecosystem](https://ess-dive.lbl.gov)
* [Joint Genome Institute](https://jgi.doe.gov)
* [KBase](https://kbase.us)
* [National Microbiome Data Collaborative](https://microbiomedata.org)
* [National Center for Biotechnology Information](https://www.ncbi.nlm.nih.gov)
* [Office of Scientific and Technical Information](https://www.osti.gov)
* [ORCID](https://orcid.org)
* [Research Organization Registry](http://identifiers.org/ror/)
* [Schema.org](https://schema.org)
* [SPDX](https://spdx.dev)


### References

[^1]: Wood-Charlson EM, Crockett Z, Erdmann C, Arkin AP, Robinson CB (2022) Ten simple rules for getting and giving credit for data. PLoS Comput Biol 18(9): e1010476. [https://doi.org/10.1371/journal.pcbi.1010476](https://doi.org/10.1371/journal.pcbi.1010476)

[^2]: ESIP Data Preservation and Stewardship Committee (2019). Data Citation Guidelines for Earth Science Data, Version 2. ESIP. Online resource. [https://doi.org/10.6084/m9.figshare.8441816.v1](https://doi.org/10.6084/m9.figshare.8441816.v1)
