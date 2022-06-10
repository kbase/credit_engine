# KBase Credit Engine

This repo holds the schema and associated scripts used by the KBase Credit Engine.


### Installation

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


### Metadata Schema

The metadata schema is maintained in [linkml format](https://linkml.io), with other formats (including the python class) generated from the [linkml schema file](schema/metadata.yaml).

![Schema diagram](/schema/metadata_schema.png "Metadata schema diagram")

See the [linkml documentation](https://linkml.io/linkml/index.html) for full details on using the linkml format and the related tools.

Useful commands:

generate derived files in all formats:
```sh
gen-project -d schema/ schema/metadata.yaml
```

validate data (in file `data.yaml`) against the schema:
```sh
linkml-validate -s schema/metadata.yaml data.yaml
```

generate Python models:
```sh
gen-python schema/metadata.yaml > src/metadata.yaml
```

generate a schema diagram (can be visualised at yuml.me):
```sh
gen-yuml schema/metadata.yaml
```
