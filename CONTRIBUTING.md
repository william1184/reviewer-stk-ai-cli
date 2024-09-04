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


### Publishing in QA Environment Local

1 - poetry config repositories.test-pypi https://test.pypi.org/legacy/

2 - poetry config pypi-token.test-pypi pypi-XXXXXXXX

3 - poetry version prerelease
    
    |rule	        before	after  |
    |major	        1.3.0	2.0.0  | 
    |minor	        2.1.4	2.2.0  | 
    |patch	        4.1.1	4.1.2  |
    |premajor	1.0.2	2.0.0a0|
    |preminor	1.0.2	1.1.0a0|
    |prepatch	1.0.2	1.0.3a0|
    |prerelease	1.0.2	1.0.3a0|
    |prerelease	1.0.3a0	1.0.3a1|
    |prerelease	1.0.3b0	1.0.3b1|

4 - poetry publish -r test-pypi --build


## Publishing in Prod Local
1 - poetry config pypi-token.pypi pypi-XXXXXXXX

2 - poetry publish

### Additional Guidelines
Follow the coding standards and best practices.
Write clear and concise commit messages.
Ensure all tests pass before submitting a pull request.
Include documentation where applicable.
Thank you for your contributions!