# GitHub App for MCP automations

This repository supports authenticating to the GitHub API using a GitHub App (recommended) instead of a user PAT.

## Why use a GitHub App?
- Least-privilege access per org/repo
- Scoped, expiring installation tokens (no long-lived user PATs)
- Easier org-wide governance and revocation

## Steps

1) Create the GitHub App (Org level)
- Go to: Organization Settings > Developer settings > GitHub Apps > New GitHub App
- App name: MCP Automation (or similar)
- Homepage URL: https://github.com/arturdr-org/org-automation (or your site)
- Webhook: not required for this workflow
- Permissions (minimum for labels sync):
  - Repository permissions:
    - Contents: Read
    - Issues: Read and Write (labels live under Issues)
    - Metadata: Read
  - Organization permissions: (optional)
    - Members: Read (helps some org lookups)
- Where can this GitHub App be installed? Only on this account (organization)
- Create the App, then Generate a Private key (you will download a .pem file).
- Note the App ID.

2) Install the App in the organization
- On the App page, click Install App > arturdr-org > Install (all repos or select repos)

3) Add the secrets to this repo
- In arturdr-org/org-automation > Settings > Secrets and variables > Actions > New repository secret:
  - ORG_APP_ID: the numeric App ID
  - ORG_APP_PRIVATE_KEY: contents of the PEM file (include header/footer)
- Optional (fallback): ORG_AUTOMATION_PAT for user PAT if needed

4) Run the workflow
- Actions > Run GitHub MCP > set inputs (dry_run=true for testing), Run workflow
- When ready, run with dry_run=false

## How it works
- The workflow exports ORG_APP_ID and ORG_APP_PRIVATE_KEY to the job
- The MCP script builds a short-lived App JWT, resolves the installation for the org, then requests an installation access token
- The token is used to authenticate PyGithub and perform label sync
- If App auth fails, it falls back to ORG_AUTOMATION_PAT (if present)

## Troubleshooting
- 401 Bad credentials: ensure the App is installed in arturdr-org and has Issues: Read/Write. Confirm secrets are set and PEM is valid.
- 404 installation not found: ensure the App is installed in the org (Install App) and the org name matches ORG_NAME input.
- Missing labels updates: verify the App has access to the target repos (All repositories or selected repositories include them).
