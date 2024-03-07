# CLI: Command-line interaces powered by Typer and Pydantic.

---Here provide a brief description of the package---

## Overview

```bash
TOOD
```

## Installation

```bash
pip install git+ssh://git@github.com/sztal/cli.git
# From a specific branch, e.g. 'dev'
pip install git+ssh://git@github.com/sztal/cli.git@dev
```




## Development

### Environment setup and dev installation

```bash
# Clone the repo
git clone git+ssh://git@github.com/sztal/cli.git
# Or from a specific branch, e.g. 'dev'
git clone git+ssh://git@github.com/sztal/cli.git@dev
```

Configure the environment and install the package after cloning.
The make commands below also set up and configure version control (GIT).

```bash
cd cli
conda env create -f environment.yaml
conda activate cli
make init
```

`Makefile` defines several commands that are useful during development.

```bash
# Clean up auxiliary files
make clean
# List explicitly imported dependencies
make list-deps
```

### Testing

```bash
pytest
## With automatic debugger session
pytest --pdb
```

### Unit test coverage statistics

```bash
# Calculate and display
make coverage
# Only calculate
make cov-run
# Only display (based on previous calculations)
make cov-report
```
