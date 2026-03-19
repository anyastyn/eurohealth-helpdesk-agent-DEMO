# Publishing Guide

## Goal

Publish the polished portfolio demo to GitHub without uploading secrets, generated files, or unnecessary local artifacts.

Repository you created:

- `https://github.com/anyastyn/eurohealth-helpdesk-agent-DEMO`

## Files and folders you should publish

- `README.md`
- `LICENSE`
- `.gitignore`
- `.env.example`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `main.py`
- `src/`
- `scripts/`
- `tests/`
- `data/helpdesk/`
- `docs/agent-overview.md`
- `docs/demo-ui.html`
- `docs/publishing-guide.md`
- `governance/policies/`
- `.github/workflows/ci.yml`

## Files and folders you should NOT publish

- `.env`
- `logs/`
- `data/kb_index.json`
- `data/kb_quality_report.json`
- `__pycache__/`
- `.pytest_cache/`
- local temporary files

## Exact Commands

Run these commands from the project root:

```powershell
git init
git branch -M main
git add README.md LICENSE .gitignore .env.example requirements.txt Dockerfile docker-compose.yml main.py
git add src scripts tests .github
git add data/helpdesk
git add docs/agent-overview.md docs/demo-ui.html docs/publishing-guide.md
git add governance/policies
git commit -m "Initial public portfolio version of EuroHealth helpdesk agent"
git remote add origin https://github.com/anyastyn/eurohealth-helpdesk-agent-DEMO.git
git push -u origin main
```

## Before You Push

Check what will be uploaded:

```powershell
git status
```

If you see `.env`, `logs/`, `data/kb_index.json`, or `data/kb_quality_report.json`, stop and do not push yet.

## After You Push

Open the GitHub repo and verify:

- the README renders well
- `.env` is not present
- `logs/` is not present
- the source code and docs are visible
- the project description matches what you want employers to see
