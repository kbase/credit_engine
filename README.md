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

## Metadata Schema

The KBase credit metadata schema is maintained in [linkml format](https://linkml.io); other formats (including the python class) can be generated from the [linkml schema file](schema/kbase/linkml/credit_metadata.yaml).

See the [linkml documentation](https://linkml.io/linkml/index.html) for full details on using the linkml format and the related tools.

Full schema documentation can be found at [https://kbase.github.io/credit_engine/](https://kbase.github.io/credit_engine/).

### Schema Diagram

Generated using [erdantic](https://erdantic.drivendata.org/stable/)

![KBase metadata schema diagram](schema/kbase/kbase-schema.png "Entity-relationship diagram for KBase metadata schema")

## Software Installation

This repo uses [poetry](https://python-poetry.org/) to manage the python environment and dependencies.

See the [poetry docs](https://python-poetry.org/docs/) for poetry installation instructions.

Install the project dependencies and create a virtual environment:

```sh
poetry install
```

Activate the virtual environment:

```sh
poetry shell
```

Run tests or other scripts:

```sh
poetry run <command>
poetry run pytest tests/
```

### Useful commands

These assume that you have already run `poetry shell` to activate the credit engine virtual environment.

generate derived files in all formats:
```sh
gen-project -d schema/kbase/ schema/kbase/linkml/credit_metadata.yaml
```

lint the KBase linkml schema file:
```sh
linkml-lint -f terminal schema/kbase/linkml/credit_metadata.yaml
```

validate data (in file `data.yaml`) against the schema:
```sh
linkml-validate -s schema/kbase/linkml/credit_metadata.yaml data.yaml
```

generate Python models:
```sh
gen-python schema/kbase/linkml/credit_metadata.yaml > schema/kbase/linkml/credit_metadata.py
```

generate a schema diagram (can be visualised at yuml.me):
```sh
gen-yuml schema/kbase/linkml/credit_metadata.yaml
```
