# GitHub Python Script 🐍

[![CI](https://github.com/austenstone/github-python-script/actions/workflows/ci.yml/badge.svg)](https://github.com/austenstone/github-python-script/actions/workflows/ci.yml)

This action makes it easy to quickly write a Python script in your workflow that uses the GitHub API and the workflow run context.

Inspired by [actions/github-script](https://github.com/actions/github-script), but for Python lovers! 🐍✨

## Usage

To use this action, provide an input named `script` that contains the body of a Python script. The following objects will be available in your script:

- `github` - A pre-authenticated PyGithub client with retry support
- `context` - An object containing the context of the workflow run (similar to `@actions/github` context)
- `core` - Functions for logging and setting outputs (similar to `@actions/core`)
- Standard Python libraries: `os`, `sys`, `json`

Since the `script` runs in an environment with these objects pre-defined, you don't have to import them!

### Basic Example

```yaml
on: push

jobs:
  hello-world:
    runs-on: ubuntu-latest
    steps:
      - uses: austenstone/github-python-script@v1
        with:
          script: |
            print(f"Hello {context.actor}!")
            core.info(f"Triggered by {context.event_name}")
```

## 📥 Inputs

| Name | Description | Default | Required |
| --- | --- | --- | --- |
| `script` | The Python script to execute | | ✅ |
| `github-token` | GitHub token for authentication | `${{ github.token }}` | ❌ |
| `result-encoding` | Encoding for the result output (`json` or `string`) | `json` | ❌ |
| `retries` | Number of times to retry failed API requests | `0` | ❌ |
| `retry-exempt-status-codes` | Comma-separated HTTP status codes to not retry | `400,401,403,404,422` | ❌ |
| `base-url` | Base URL for GitHub API (for GitHub Enterprise) | | ❌ |
| `python-version` | Python version to use | `3.x` | ❌ |

## 📤 Outputs

| Name | Description |
| --- | --- |
| `result` | The return value of the script (if `__result__` variable is set) |

## 🎯 Examples

### Comment on an Issue

```yaml
on:
  issues:
    types: [opened]

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
                body="👋 Thanks for opening this issue!"
            )
```

### Add Labels to an Issue

```yaml
on:
  issues:
    types: [opened]

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: austenstone/github-python-script@v1
        with:
          script: |
            github.rest.issues.add_labels(
                owner=context.repo["owner"],
                repo=context.repo["repo"],
                issue_number=context.issue["number"],
                labels=["triage", "needs-review"]
            )
```

### List Repository Issues

```yaml
on: workflow_dispatch

jobs:
  list-issues:
    runs-on: ubuntu-latest
    steps:
      - uses: austenstone/github-python-script@v1
        with:
          script: |
            issues = github.rest.issues.list_for_repo(
                owner=context.repo["owner"],
                repo=context.repo["repo"],
                state="open"
            )
            
            for issue in issues:
                core.info(f"#{issue.number}: {issue.title}")
```

### Welcome First-Time Contributors

```yaml
on: pull_request_target

jobs:
  welcome:
    runs-on: ubuntu-latest
    steps:
      - uses: austenstone/github-python-script@v1
        with:
          script: |
            creator = context.payload["sender"]["login"]
            
            # Get all issues created by the PR opener
            repo = github.get_repo(f"{context.repo['owner']}/{context.repo['repo']}")
            issues = repo.get_issues(creator=creator, state="all")
            
            # Check if they've contributed before
            for issue in issues:
                if issue.number != context.issue["number"] and issue.pull_request:
                    core.info(f"{creator} is already a contributor!")
                    exit()
            
            # Welcome new contributor
            github.rest.issues.create_comment(
                owner=context.repo["owner"],
                repo=context.repo["repo"],
                issue_number=context.issue["number"],
                body="""**Welcome**, new contributor! 🎉

Please make sure you've read our [contributing guide](CONTRIBUTING.md) and we look forward to reviewing your Pull Request shortly ✨"""
            )
```

### Use Return Values

```yaml
- uses: austenstone/github-python-script@v1
  id: get-user
  with:
    script: |
      __result__ = context.actor
      
- name: Print result
  run: echo "User is ${{ steps.get-user.outputs.result }}"
```

### Working with JSON Data

```yaml
- uses: austenstone/github-python-script@v1
  id: get-repo-info
  with:
    result-encoding: json
    script: |
      repo = github.get_repo(f"{context.repo['owner']}/{context.repo['repo']}")
      __result__ = {
          "stars": repo.stargazers_count,
          "forks": repo.forks_count,
          "watchers": repo.watchers_count
      }

- name: Display repo stats
  run: |
    echo "Stars: ${{ fromJson(steps.get-repo-info.outputs.result).stars }}"
    echo "Forks: ${{ fromJson(steps.get-repo-info.outputs.result).forks }}"
```

### Execute GraphQL Queries

```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      query = """
      query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
          issues(first: 10, states: OPEN) {
            nodes {
              number
              title
            }
          }
        }
      }
      """
      
      variables = {
          "owner": context.repo["owner"],
          "name": context.repo["repo"]
      }
      
      result = github.graphql(query, variables)
      
      for issue in result["data"]["repository"]["issues"]["nodes"]:
          core.info(f"#{issue['number']}: {issue['title']}")
```

### Using Environment Variables for Inputs

To avoid script injection vulnerabilities, use environment variables:

```yaml
- uses: austenstone/github-python-script@v1
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  with:
    script: |
      title = os.getenv("PR_TITLE")
      
      if title.startswith("feat:"):
          core.info("✨ Feature PR detected!")
          github.rest.issues.add_labels(
              owner=context.repo["owner"],
              repo=context.repo["repo"],
              issue_number=context.issue["number"],
              labels=["feature"]
          )
```

### API Retries

Configure automatic retries for failed API requests:

```yaml
- uses: austenstone/github-python-script@v1
  with:
    retries: 3
    retry-exempt-status-codes: 400,401
    script: |
      # This will retry up to 3 times on failures
      # (except for 400 and 401 status codes)
      issue = github.rest.issues.get(
          owner=context.repo["owner"],
          repo=context.repo["repo"],
          issue_number=1
      )
      core.info(f"Issue: {issue.title}")
```

### Using with GitHub Enterprise

```yaml
- uses: austenstone/github-python-script@v1
  with:
    github-token: ${{ secrets.GHE_TOKEN }}
    base-url: https://github.example.com/api/v3
    script: |
      core.info(f"Using GitHub Enterprise at {context.api_url}")
      # Your script here
```

## 🔍 API Reference

### `github` Object

The `github` object is a PyGithub client with the following methods:

- `github.rest.issues.*` - Issues API methods
  - `create_comment(owner, repo, issue_number, body)`
  - `add_labels(owner, repo, issue_number, labels)`
  - `list_for_repo(owner, repo, **kwargs)`
  - `get(owner, repo, issue_number)`

- `github.rest.repos.*` - Repositories API methods
  - `get(owner, repo)`
  - `get_commit(owner, repo, ref)`

- `github.rest.pulls.*` - Pull Requests API methods
  - `list(owner, repo, **kwargs)`
  - `get(owner, repo, pull_number)`

- `github.get_repo(name)` - Get a repository object
- `github.get_user(username)` - Get a user object
- `github.graphql(query, variables)` - Execute GraphQL queries
- `github.paginate(method, *args, **kwargs)` - Paginate through results

### `context` Object

The `context` object provides workflow run context:

- `context.payload` - The event payload
- `context.repo` - Repository info: `{"owner": "...", "repo": "..."}`
- `context.issue` - Issue/PR info: `{"owner": "...", "repo": "...", "number": ...}`
- `context.sha` - Commit SHA
- `context.ref` - Git ref
- `context.workflow` - Workflow name
- `context.actor` - User who triggered the workflow
- `context.event_name` - Event that triggered the workflow
- `context.run_id` - Workflow run ID
- `context.run_number` - Workflow run number

### `core` Object

The `core` object provides logging and output functions:

- `core.info(message)` - Log an info message
- `core.debug(message)` - Log a debug message
- `core.warning(message)` - Log a warning
- `core.error(message)` - Log an error
- `core.set_failed(message)` - Mark the action as failed
- `core.set_output(name, value)` - Set an output value
- `core.export_variable(name, value)` - Export an environment variable
- `core.set_secret(secret)` - Mask a value in logs
- `core.get_input(name, required=False)` - Get an input value

## 🛠️ Development

### Building

```bash
npm install
npm run build
```

### Testing Locally

Create a `.env` file with required environment variables and run:

```bash
npm run dev
```

## 📝 License

MIT - See [LICENSE](LICENSE) for details.

---

**Not into Python?** Check out the original [actions/github-script](https://github.com/actions/github-script) for JavaScript! 🚀
