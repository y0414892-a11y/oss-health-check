# Contributing

Thank you for improving OSS Health Check.

## Good First Contributions

- Add a new repository check.
- Improve the report wording.
- Add tests for an existing check.
- Improve the README examples.
- Add support for another output format.

## Local Development

Run the test suite:

```powershell
python -m unittest discover -s tests
```

Run the CLI against this repository:

```powershell
python -m oss_health_check .
```

## Contribution Workflow

1. Open an issue for the change you want to make.
2. Create a branch with a short name, such as `add-json-output`.
3. Make the smallest useful change.
4. Add or update tests.
5. Open a pull request and describe what changed.

## Code Style

- Prefer clear standard-library Python.
- Keep checks simple and easy to test.
- Do not add dependencies unless they solve a real problem.
