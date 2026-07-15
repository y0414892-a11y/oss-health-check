# OSS Health Check

OSS Health Check is a small command-line tool that scans a repository and
reports whether it has the basic files expected from a friendly open-source
project.

It is designed for beginners who want a useful first open-source project:
small enough to understand, but practical enough to improve over time.

## What It Checks

- README
- License
- Contributing guide
- Tests
- Continuous integration workflow
- Issue templates
- Pull request template
- Security policy
- Changelog

## Quick Start

Run it from this repository:

```powershell
python -m oss_health_check .
```

Scan another project:

```powershell
python -m oss_health_check C:\path\to\another\repo
```

Use strict mode when you want missing checks to fail the command:

```powershell
python -m oss_health_check . --strict
```

Set a minimum score for automation:

```powershell
python -m oss_health_check . --fail-under 80
```

Output JSON for scripts and automation:

```powershell
python -m oss_health_check . --json
```

## GitHub Action

Use this repository as a GitHub Action in another project:

```yaml
name: OSS Health Check

on:
  pull_request:
  push:
    branches: [main]

jobs:
  health-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
      - uses: y0414892-a11y/oss-health-check@main
        with:
          fail-under: "80"
```

## Example Output

```text
OSS Health Check: .
Score: 7/9 (78%)

[ok] README
     Found a README file.
[missing] Security policy
     Add SECURITY.md with vulnerability reporting instructions.
```

## Why This Project Matters

Many useful projects fail to attract contributors because they are hard to
understand, hard to run, or unclear about how people can help. This tool makes
those gaps visible and gives maintainers a simple checklist to improve their
repositories.

## Roadmap

- Add GitHub Action examples for common project types.
- Add GitHub API checks for repository metadata.
- Add language-specific checks for Python, JavaScript, and Rust projects.
- Add scoring categories for documentation, community, and maintenance.
- Publish the package to PyPI.

## Learning Path

1. Read `oss_health_check/scanner.py` to understand the core scan logic.
2. Add one new check and one matching test.
3. Improve the README with a screenshot or terminal output.
4. Open your first issue describing a planned improvement.
5. Create a branch, commit the improvement, and open a pull request.

## Development

Run tests with the standard library test runner:

```powershell
python -m unittest discover -s tests
```

No third-party dependencies are required.

## Publishing

See `PUBLISHING.md` for the GitHub publishing checklist.
