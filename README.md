![PR Workflow](https://github.com/kbase/credit_engine/actions/workflows/on_pr.yaml/badge.svg)
[![Codecov](https://codecov.io/gh/kbase/credit_engine/branch/develop/graph/badge.svg?token=vOUaMmH86Z)](https://codecov.io/gh/kbase/credit_engine)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/dd36ff4877b94ce48f67a18aa4638dc8)](https://www.codacy.com/gh/kbase/credit_engine/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=kbase/credit_engine&amp;utm_campaign=Badge_Grade)

# KBase Credit Engine

This repo holds the schema and associated scripts used by the KBase Credit Engine.

The KBase Credit Engine is a project aimed at ensuring that appropriate citation information exists for data entering and/or produced by the [KBase software and data science platform](https://kbase.us) to allow credit to be attributed to those who produced the data.

- [KBase Credit Engine](#kbase-credit-engine)
  - [Metadata Schema](#metadata-schema)
    - [Schema Diagram](#schema-diagram)
  - [Software Installation](#software-installation)
    - [Useful commands](#useful-commands)
      - [JSONschema data validation](#jsonschema-data-validation)

## Metadata Schema

The KBase credit metadata schema is maintained in [linkml format](https://linkml.io); other formats (including the python class) can be generated from the [linkml schema file](schema/kbase/linkml/credit_metadata.yaml).

See the [linkml documentation](https://linkml.io/linkml/index.html) for full details on using the linkml format and the related tools.

Full schema documentation can be found at [https://kbase.github.io/credit_engine/](https://kbase.github.io/credit_engine/).

### Schema Diagram

Generated from the [Pydantic version](schema/kbase/python/credit_metadata_pydantic.py) of the KBase Citation Metadata Schema using [erdantic](https://erdantic.drivendata.org/stable/).

![KBase metadata schema diagram](schema/kbase/kbase-schema.png "Entity-relationship diagram for KBase citation metadata schema")

See below for how to regenerate the ER diagram after making changes to the schema.

## Software Installation

This repo uses [uv](https://docs.astral.sh/uv/) to manage the python environment and dependencies.

See the [uv docs](https://docs.astral.sh/uv/) for uv installation instructions.

Install the project dependencies and create a virtual environment:

```sh
uv sync
```

Run tests or other scripts:

```sh
uv run <command>
uv run pytest tests/
```

### Useful commands

These assume that you have already run `uv sync` to install the credit engine virtual environment and dependencies.

generate derived files in all formats:
```sh
uv run gen-project -d schema/kbase/ schema/kbase/linkml/credit_metadata.yaml
```

lint the KBase linkml schema file:
```sh
uv run linkml-lint -f terminal schema/kbase/linkml/credit_metadata.yaml
```

validate data (in file `data.yaml`) against the schema:
```sh
uv run linkml-validate -s schema/kbase/linkml/credit_metadata.yaml data.yaml
```

generate JSONschema version:
```sh
uv run gen-json-schema schema/kbase/linkml/credit_metadata.yaml > schema/kbase/jsonschema/credit_metadata.schema.json
```

generate Python classes:
```sh
uv run gen-python schema/kbase/linkml/credit_metadata.yaml > schema/kbase/python/credit_metadata.py
```

generate Pydantic classes:
```sh
uv run gen-pydantic schema/kbase/linkml/credit_metadata.yaml > schema/kbase/python/credit_metadata_pydantic.py
```

generate an ER diagram from the Pydantic classes using [erdantic](https://erdantic.drivendata.org/stable/) (assumes that erdantic has been installed already):
```sh
uv run erdantic schema.kbase.python.credit_metadata_pydantic.CreditMetadata -o schema/kbase/kbase-schema.png
```

generate a YUML schema diagram (can be visualised at yuml.me):
```sh
uv run gen-yuml schema/kbase/linkml/credit_metadata.yaml
```

#### JSONschema data validation

install the [JSONschema check](https://check-jsonschema.readthedocs.io/en/latest/) script:

```sh
brew install check-jsonschema
```

To test a file or files against the schema, use the command:
```sh
check-jsonschema --schemafile schema/kbase/jsonschema/credit_metadata.schema.json data_file_1.json data_file_2.json
```
or
```sh
check-jsonschema --schemafile schema/kbase/jsonschema/credit_metadata.schema.json sample_data/**/*kbcms.json
```
