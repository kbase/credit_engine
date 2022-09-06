# KBase Credit Engine

This repo holds the schema and associated scripts used by the KBase Credit Engine.

- [KBase Credit Engine](#kbase-credit-engine)
  - [Installation](#installation)
  - [Metadata Schema](#metadata-schema)
    - [Schema Diagram](#schema-diagram)
    - [Useful commands:](#useful-commands)

## Installation

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

## Metadata Schema

The metadata schema is maintained in [linkml format](https://linkml.io); other formats (including the python class) can be generated from the [linkml schema file](schema/kbase/linkml/metadata.yaml).

See the [linkml documentation](https://linkml.io/linkml/index.html) for full details on using the linkml format and the related tools.

### Schema Diagram

Generated using [erdantic](https://erdantic.drivendata.org/stable/)

![KBase metadata schema diagram](schema/kbase/kbase-schema.png "Entity-relationship diagram for KBase metadata schema")

### Useful commands:

generate derived files in all formats:
```sh
gen-project -d schema/ schema/linkml/metadata.yaml
```

validate data (in file `data.yaml`) against the schema:
```sh
linkml-validate -s schema/metadata.yaml data.yaml
```

generate Python models:
```sh
gen-python schema/metadata.yaml > src/metadata.py
```

generate a schema diagram (can be visualised at yuml.me):
```sh
gen-yuml schema/metadata.yaml
```
