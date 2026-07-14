# Publishing to GitHub

This guide publishes the project as a public GitHub repository.

## 1. Install Local Tools

Install Git for Windows:

```powershell
winget install --id Git.Git -e
```

Install Python from python.org or with winget:

```powershell
winget install --id Python.Python.3.12 -e
```

Restart PowerShell, then verify:

```powershell
git --version
python --version
```

## 2. Test the Project

From the project directory:

```powershell
cd oss-health-check
python -m unittest discover -s tests
python -m oss_health_check . --strict
```

## 3. Create the GitHub Repository

On GitHub:

1. Click **New repository**.
2. Repository name: `oss-health-check`.
3. Description: `A small CLI that checks whether a repository is ready for open-source contributors.`
4. Visibility: **Public**.
5. Do not add a README, license, or gitignore on GitHub because this project already has them.
6. Click **Create repository**.

## 4. Push the Local Project

Replace `<your-github-name>` with your GitHub username:

```powershell
git init
git add .
git commit -m "Initial release"
git branch -M main
git remote add origin https://github.com/<your-github-name>/oss-health-check.git
git push -u origin main
```

## 5. Make the First Release

On GitHub:

1. Open the repository.
2. Click **Releases**.
3. Click **Draft a new release**.
4. Tag: `v0.1.0`.
5. Title: `OSS Health Check 0.1.0`.
6. Summary: `First working version with repository checks, CLI output, tests, and CI.`
7. Publish the release.

## 6. First Learning Issues

Create these GitHub issues after publishing:

- Add JSON output.
- Add a `--fail-under` score threshold.
- Detect Python packaging files.
- Improve the report with grouped categories.
- Add screenshots to the README.

