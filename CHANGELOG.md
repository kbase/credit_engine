# Changelog

## [#156](https://github.com/kbase/credit_engine/pull/156) - 2023-07-18

### Changed

- Switching linter over to using Ruff instead of isort + a billion flake8 modules.


## [#151](https://github.com/kbase/credit_engine/pull/151) - 2023-06-29

### Changed

- Converted file formats into an enum.


## [#152](https://github.com/kbase/credit_engine/pull/152) - 2023-06-30

### Changed

- XML now refers to Crossref's unixsd format.

### Removed

- Remove support Crossref unixref format as it contains less information.


## [#150](https://github.com/kbase/credit_engine/pull/150) - 2023-06-29

### Changed

- Standardise line endings in XML files to use `\n`
- Reorganise various test files
- Switch to using real DOIs for client-specific tests and many of the tests in `clients/base.py`

### Removed

- Remove support for Python 3.9


## 2023-05-01

### Updated

Bump python deps
