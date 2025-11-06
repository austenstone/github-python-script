# GitHub Python Script Examples

This document provides additional examples for using `github-python-script`.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Working with Issues](#working-with-issues)
- [Working with Pull Requests](#working-with-pull-requests)
- [Advanced Patterns](#advanced-patterns)
- [Error Handling](#error-handling)

## Basic Usage

### Hello World

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      core.info("Hello from Python! 🐍")
      core.info(f"Triggered by: {context.actor}")
```

### Access Context Information

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      core.info(f"Event: {context.event_name}")
      core.info(f"Repository: {context.repo['owner']}/{context.repo['repo']}")
      core.info(f"SHA: {context.sha}")
      core.info(f"Ref: {context.ref}")
      core.info(f"Actor: {context.actor}")
      core.info(f"Workflow: {context.workflow}")
```

## Working with Issues

### Create Issue Comment

```yaml
on:
  issues:
    types: [opened, edited]

jobs:
  comment:
    runs-on: ubuntu-latest
    steps:
      - uses: austenstone/github-python-script@v1
        with:
          script: |
            github.rest.issues.create_comment(
                owner=context.repo["owner"],
                repo=context.repo["repo"],
                issue_number=context.issue["number"],
                body="Thank you for your contribution! 🎉"
            )
```

### Add Multiple Labels

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      labels = ["bug", "needs-triage", "priority-high"]
      github.rest.issues.add_labels(
          owner=context.repo["owner"],
          repo=context.repo["repo"],
          issue_number=context.issue["number"],
          labels=labels
      )
```

### Close Stale Issues

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      import datetime
      
      repo = github.get_repo(f"{context.repo['owner']}/{context.repo['repo']}")
      issues = repo.get_issues(state="open")
      
      stale_days = 30
      now = datetime.datetime.now(datetime.timezone.utc)
      
      for issue in issues:
          days_old = (now - issue.updated_at).days
          
          if days_old > stale_days:
              issue.create_comment("Closing due to inactivity. Feel free to reopen!")
              issue.edit(state="closed")
              core.info(f"Closed stale issue #{issue.number}")
```

## Working with Pull Requests

### Auto-approve Dependabot PRs

```yaml
on:
  pull_request_target:
    types: [opened]

jobs:
  auto-approve:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'
    steps:
      - uses: austenstone/github-python-script@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            pr = context.payload["pull_request"]
            
            # Approve the PR
            repo = github.get_repo(f"{context.repo['owner']}/{context.repo['repo']}")
            pull = repo.get_pull(pr["number"])
            pull.create_review(
                body="Auto-approved Dependabot PR ✅",
                event="APPROVE"
            )
            
            core.info(f"Approved PR #{pr['number']}")
```

### Check PR Title Format

```yaml
on:
  pull_request:
    types: [opened, edited]

jobs:
  check-title:
    runs-on: ubuntu-latest
    steps:
      - uses: austenstone/github-python-script@v1
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        with:
          script: |
            import re
            
            title = os.getenv("PR_TITLE")
            pattern = r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"
            
            if not re.match(pattern, title):
                core.set_failed(
                    f"PR title '{title}' doesn't match conventional commit format!"
                )
            else:
                core.info("✅ PR title format is valid")
```

### Add Size Labels to PRs

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      pr = context.payload["pull_request"]
      
      additions = pr["additions"]
      deletions = pr["deletions"]
      total_changes = additions + deletions
      
      # Determine size label
      if total_changes < 10:
          size_label = "size/XS"
      elif total_changes < 50:
          size_label = "size/S"
      elif total_changes < 200:
          size_label = "size/M"
      elif total_changes < 500:
          size_label = "size/L"
      else:
          size_label = "size/XL"
      
      # Remove old size labels
      repo = github.get_repo(f"{context.repo['owner']}/{context.repo['repo']}")
      issue = repo.get_issue(pr["number"])
      
      for label in issue.labels:
          if label.name.startswith("size/"):
              issue.remove_from_labels(label)
      
      # Add new size label
      issue.add_to_labels(size_label)
      core.info(f"Added label: {size_label} ({total_changes} changes)")
```

## Advanced Patterns

### Using GraphQL

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      query = """
      query($owner: String!, $repo: String!) {
        repository(owner: $owner, name: $repo) {
          pullRequests(first: 5, states: OPEN) {
            nodes {
              number
              title
              author {
                login
              }
            }
          }
        }
      }
      """
      
      variables = {
          "owner": context.repo["owner"],
          "repo": context.repo["repo"]
      }
      
      result = github.graphql(query, variables)
      prs = result["data"]["repository"]["pullRequests"]["nodes"]
      
      for pr in prs:
          core.info(f"PR #{pr['number']}: {pr['title']} by {pr['author']['login']}")
```

### Process Webhook Payload

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      payload = context.payload
      
      if context.event_name == "pull_request":
          pr = payload["pull_request"]
          action = payload["action"]
          
          core.info(f"PR #{pr['number']} was {action}")
          core.info(f"Title: {pr['title']}")
          core.info(f"Author: {pr['user']['login']}")
          
          if pr.get("mergeable") is False:
              core.warning("⚠️ PR has merge conflicts!")
```

### Pagination Example

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      repo = github.get_repo(f"{context.repo['owner']}/{context.repo['repo']}")
      
      # Get all issues (automatically handles pagination)
      issues = repo.get_issues(state="all")
      
      total_issues = 0
      open_issues = 0
      
      for issue in issues:
          total_issues += 1
          if issue.state == "open":
              open_issues += 1
      
      core.info(f"Total issues: {total_issues}")
      core.info(f"Open issues: {open_issues}")
      core.info(f"Closed issues: {total_issues - open_issues}")
```

### Working with Multiple Repositories

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      repos_to_check = ["repo1", "repo2", "repo3"]
      owner = context.repo["owner"]
      
      for repo_name in repos_to_check:
          try:
              repo = github.get_repo(f"{owner}/{repo_name}")
              core.info(f"✅ {repo_name}: {repo.stargazers_count} stars")
          except Exception as e:
              core.warning(f"❌ {repo_name}: {str(e)}")
```

## Error Handling

### Basic Error Handling

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      try:
          issue = github.rest.issues.get(
              owner=context.repo["owner"],
              repo=context.repo["repo"],
              issue_number=9999999
          )
      except Exception as e:
          core.warning(f"Issue not found: {str(e)}")
          core.info("Continuing with default behavior...")
```

### Retry with Custom Logic

```yaml
- uses: austenstone/github-python-script@v1
  with:
    retries: 3
    script: |
      import time
      
      max_attempts = 3
      attempt = 0
      
      while attempt < max_attempts:
          try:
              repo = github.get_repo(f"{context.repo['owner']}/{context.repo['repo']}")
              core.info(f"✅ Successfully fetched repo on attempt {attempt + 1}")
              break
          except Exception as e:
              attempt += 1
              if attempt >= max_attempts:
                  core.set_failed(f"Failed after {max_attempts} attempts: {str(e)}")
              else:
                  core.warning(f"Attempt {attempt} failed, retrying...")
                  time.sleep(2 ** attempt)  # Exponential backoff
```

### Graceful Degradation

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      # Try to use an API feature, fall back if not available
      try:
          repo = github.get_repo(f"{context.repo['owner']}/{context.repo['repo']}")
          license_info = repo.get_license()
          core.info(f"License: {license_info.license.name}")
      except:
          core.info("No license information available")
      
      # Continue with other operations
      core.info(f"Repository description: {repo.description}")
```

## Tips & Best Practices

### 1. Use Environment Variables for Security

```yaml
# ❌ Don't do this (vulnerable to injection)
- uses: austenstone/github-python-script@v1
  with:
    script: |
      title = "${{ github.event.issue.title }}"

# ✅ Do this instead
- uses: austenstone/github-python-script@v1
  env:
    ISSUE_TITLE: ${{ github.event.issue.title }}
  with:
    script: |
      title = os.getenv("ISSUE_TITLE")
```

### 2. Structure Complex Scripts

```yaml
- uses: actions/checkout@v4

- uses: austenstone/github-python-script@v1
  with:
    script: |
      # Import your custom module
      import sys
      sys.path.append("./scripts")
      
      from my_module import process_issue
      
      process_issue(github, context, core)
```

### 3. Use Type Hints for Better Code

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      from typing import Dict, Any
      
      def process_payload(payload: Dict[str, Any]) -> None:
          if "issue" in payload:
              issue_number: int = payload["issue"]["number"]
              core.info(f"Processing issue #{issue_number}")
      
      process_payload(context.payload)
```

### 4. Log Meaningful Information

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      core.info("Starting process...")
      core.debug("Debug information here")
      
      try:
          # Do something
          core.info("✅ Operation successful")
      except Exception as e:
          core.error(f"❌ Operation failed: {str(e)}")
          core.set_failed("Process failed")
```
