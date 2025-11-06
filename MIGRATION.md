# Migration Guide: github-script to github-python-script

This guide helps you convert your `actions/github-script` workflows to use `github-python-script`.

## Basic Conversion

### JavaScript (github-script)
```yaml
- uses: actions/github-script@v8
  with:
    script: |
      console.log(`Hello ${context.actor}!`)
      core.info(`Event: ${context.eventName}`)
```

### Python (github-python-script)
```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      print(f"Hello {context.actor}!")
      core.info(f"Event: {context.event_name}")
```

## Key Differences

### 1. Property Naming Convention

JavaScript uses camelCase, Python uses snake_case:

| JavaScript | Python |
|------------|--------|
| `context.eventName` | `context.event_name` |
| `context.runId` | `context.run_id` |
| `context.runNumber` | `context.run_number` |

### 2. Object Access

**JavaScript:**
```javascript
const owner = context.repo.owner;
const repo = context.repo.repo;
```

**Python:**
```python
owner = context.repo["owner"]
repo = context.repo["repo"]
```

### 3. String Formatting

**JavaScript:**
```javascript
core.info(`PR #${pr.number}: ${pr.title}`)
```

**Python:**
```python
core.info(f"PR #{pr.number}: {pr.title}")
# or
core.info("PR #{}: {}".format(pr.number, pr.title))
```

## API Conversion Examples

### Creating Issue Comments

**JavaScript:**
```javascript
await github.rest.issues.createComment({
  issue_number: context.issue.number,
  owner: context.repo.owner,
  repo: context.repo.repo,
  body: '👋 Thanks for reporting!'
})
```

**Python:**
```python
github.rest.issues.create_comment(
    issue_number=context.issue["number"],
    owner=context.repo["owner"],
    repo=context.repo["repo"],
    body="👋 Thanks for reporting!"
)
```

### Adding Labels

**JavaScript:**
```javascript
await github.rest.issues.addLabels({
  issue_number: context.issue.number,
  owner: context.repo.owner,
  repo: context.repo.repo,
  labels: ['bug', 'triage']
})
```

**Python:**
```python
github.rest.issues.add_labels(
    issue_number=context.issue["number"],
    owner=context.repo["owner"],
    repo=context.repo["repo"],
    labels=["bug", "triage"]
)
```

### Listing Issues

**JavaScript:**
```javascript
const issues = await github.rest.issues.listForRepo({
  owner: context.repo.owner,
  repo: context.repo.repo,
  state: 'open'
})

for (const issue of issues.data) {
  console.log(`#${issue.number}: ${issue.title}`)
}
```

**Python:**
```python
issues = github.rest.issues.list_for_repo(
    owner=context.repo["owner"],
    repo=context.repo["repo"],
    state="open"
)

for issue in issues:
    print(f"#{issue.number}: {issue.title}")
```

### GraphQL Queries

**JavaScript:**
```javascript
const query = `query($owner:String!, $name:String!) {
  repository(owner:$owner, name:$name) {
    issues(first:10) {
      nodes {
        number
        title
      }
    }
  }
}`;

const variables = {
  owner: context.repo.owner,
  name: context.repo.repo
}

const result = await github.graphql(query, variables)
console.log(result)
```

**Python:**
```python
query = """
query($owner:String!, $name:String!) {
  repository(owner:$owner, name:$name) {
    issues(first:10) {
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
print(result)
```

## Advanced Patterns

### Pagination

**JavaScript:**
```javascript
const opts = github.rest.issues.listForRepo.endpoint.merge({
  ...context.repo,
  state: 'all'
})
const issues = await github.paginate(opts)
```

**Python:**
```python
repo = github.get_repo(f"{context.repo['owner']}/{context.repo['repo']}")
issues = github.paginate(repo.get_issues, state="all")
```

### Async/Await vs Standard Functions

**JavaScript:**
```javascript
// JavaScript requires async/await
const issue = await github.rest.issues.get({
  owner: context.repo.owner,
  repo: context.repo.repo,
  issue_number: 1
})
```

**Python:**
```python
# Python calls are synchronous
issue = github.rest.issues.get(
    owner=context.repo["owner"],
    repo=context.repo["repo"],
    issue_number=1
)
```

### Accessing Nested Data

**JavaScript:**
```javascript
const prTitle = context.payload.pull_request.title
const prAuthor = context.payload.pull_request.user.login
```

**Python:**
```python
pr_title = context.payload["pull_request"]["title"]
pr_author = context.payload["pull_request"]["user"]["login"]
```

## Return Values

### JavaScript
```javascript
const result = {
  status: 'success',
  count: 42
}
return result
```

### Python
```python
__result__ = {
    "status": "success",
    "count": 42
}
```

## Error Handling

### JavaScript
```javascript
try {
  await github.rest.issues.get({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: 9999
  })
} catch (error) {
  core.warning(`Issue not found: ${error.message}`)
}
```

### Python
```python
try:
    github.rest.issues.get(
        owner=context.repo["owner"],
        repo=context.repo["repo"],
        issue_number=9999
    )
except Exception as error:
    core.warning(f"Issue not found: {str(error)}")
```

## External Modules

### JavaScript
```javascript
const execa = require('execa')
const { stdout } = await execa('echo', ['hello'])
console.log(stdout)
```

### Python
```python
import subprocess
result = subprocess.run(['echo', 'hello'], capture_output=True, text=True)
print(result.stdout)
```

## Full Example Comparison

### JavaScript (github-script)
```yaml
name: Welcome Contributors
on: pull_request_target

jobs:
  welcome:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v8
        with:
          script: |
            const creator = context.payload.sender.login
            const opts = github.rest.issues.listForRepo.endpoint.merge({
              ...context.repo,
              creator,
              state: 'all'
            })
            const issues = await github.paginate(opts)

            for (const issue of issues) {
              if (issue.number === context.issue.number) continue
              if (issue.pull_request) return
            }

            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '**Welcome**, new contributor! 🎉'
            })
```

### Python (github-python-script)
```yaml
name: Welcome Contributors
on: pull_request_target

jobs:
  welcome:
    runs-on: ubuntu-latest
    steps:
      - uses: austenstone/github-python-script@v1
        with:
          script: |
            creator = context.payload["sender"]["login"]
            repo = github.get_repo(f"{context.repo['owner']}/{context.repo['repo']}")
            issues = repo.get_issues(creator=creator, state="all")

            for issue in issues:
                if issue.number == context.issue["number"]:
                    continue
                if issue.pull_request:
                    exit()

            github.rest.issues.create_comment(
                issue_number=context.issue["number"],
                owner=context.repo["owner"],
                repo=context.repo["repo"],
                body="**Welcome**, new contributor! 🎉"
            )
```

## Quick Reference Table

| Feature | JavaScript | Python |
|---------|-----------|--------|
| Variables | `const`, `let`, `var` | No keyword needed |
| String formatting | `` `Hello ${name}` `` | `f"Hello {name}"` |
| Array/List | `[1, 2, 3]` | `[1, 2, 3]` |
| Object/Dict | `{key: value}` | `{"key": value}` |
| Comments | `// comment` or `/* */` | `# comment` |
| Print | `console.log()` | `print()` |
| Async calls | `await` keyword | Not needed |
| Property access | `obj.property` | `obj["property"]` or `obj.property` |
| Function calls | `camelCase()` | `snake_case()` |
| Boolean | `true`, `false` | `True`, `False` |
| Null | `null` | `None` |

## Tips for Migration

1. **Test incrementally**: Convert one workflow at a time
2. **Check property names**: Remember camelCase → snake_case
3. **Dictionary access**: Use `[]` notation for context objects
4. **Remove await**: Python calls are synchronous
5. **Function names**: GitHub API methods use snake_case in Python
6. **Return values**: Use `__result__` variable instead of `return`
7. **Imports**: Python has built-in modules - no need to `require()`

## Need Help?

- Check the [README](README.md) for more examples
- Review [EXAMPLES.md](EXAMPLES.md) for advanced patterns
- Open an issue if you encounter problems during migration
