# Contributing

Thank you for your interest in contributing to the project! Here are some guidelines to help you get started.

## Requirements

Make sure you have [Poetry](https://python-poetry.org/docs/#installation) installed on your system before getting started.

## Installing Dependencies

### 1. Install Build Dependency

To add a build dependency, use the following command:

```sh
poetry add boto3
```
### 2. Install Development Dependencies
To add development dependencies, use the following command:

```sh
poetry add --dev coverage black pytest
```

## Running Tests
### 3. Run Unit Tests
To run unit tests, use the following command:

```sh
poetry run pytest -v
```

### 4. Run Coverage Tests
To run coverage tests and generate a report, use the following command:

```sh
poetry run coverage run -m pytest && poetry run coverage report -m
```

## Building the Project
### 5. Build the Project
To build the project, use the following command:

```sh
poetry build
```

## Publishing the Project
### 6. Publish the Project
To publish the project, use the following command:

```sh
poetry publish
```

## Formatting Code
To format code using Black, use the following command:

```sh
poetry run black .
```

### Additional Guidelines
Follow the coding standards and best practices.
Write clear and concise commit messages.
Ensure all tests pass before submitting a pull request.
Include documentation where applicable.
Thank you for your contributions!