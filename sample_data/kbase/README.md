## KBase Credit Metadata Schema example data

The subdirectories in this folder contain dataset citation metadata in several forms, including the KBase citation metadata schema.

The files are named by according to their DOI or other unique identifier, with a suffix indicating the data source/format:

* `_datacite`: [DataCite](https://support.datacite.org/docs/api)
* `_elink`: [OSTI elink](https://www.osti.gov/elink/241-6api.jsp)
* `_jdp`: [JGI Data Portal](https://files.jgi.doe.gov/apidoc/)
* `_kbcms`: KBase Credit Metadata Schema

All KBCMS files were hand-crafted by a fallible human, so may contain mistakes.

See `schema/kbase/jsonschema/credit_metadata.schema.json` for the KBCMS schema details. The schema has been edited somewhat to bring it into closer alignment with the commonmeta jsonschema.

Note that the linkml schema and documentation have not been updated.
