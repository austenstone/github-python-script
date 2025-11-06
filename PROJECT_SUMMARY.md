# 🐍 GitHub Python Script - Project Summary

A GitHub Action that lets you execute Python scripts with full access to the GitHub API and workflow context - just like `actions/github-script`, but for Python!

## 📁 Project Structure

```
github-python-script/
├── .github/
│   └── workflows/
│       └── test.yml          # Test workflow
├── dist/                      # Built action (generated)
├── python/
│   ├── github_script.py      # Python wrapper for GitHub API
│   └── requirements.txt      # Python dependencies
├── src/
│   ├── index.ts             # Main TypeScript entry point
│   └── local.ts             # Local testing script
├── action.yml               # Action metadata
├── EXAMPLES.md              # Comprehensive examples
├── MIGRATION.md             # Migration guide from github-script
└── README.md                # Main documentation
```

## 🎯 What Was Built

### 1. Action Configuration (`action.yml`)
- **Inputs**: script, github-token, result-encoding, retries, retry-exempt-status-codes, base-url, python-version
- **Outputs**: result (the return value from the script)
- **Runtime**: Node.js 20

### 2. Python Wrapper (`python/github_script.py`)
Provides three main classes:

#### `Core` Class
Wraps @actions/core functionality:
- `debug()`, `info()`, `warning()`, `error()`
- `set_failed()`, `set_output()`, `export_variable()`
- `set_secret()`, `get_input()`

#### `Context` Class
Provides workflow context:
- `payload` - Event payload
- `repo` - Repository info
- `issue` - Issue/PR info
- `sha`, `ref`, `workflow`, `actor`, `event_name`, etc.

#### `GitHubWrapper` Class
Wraps PyGithub with octokit-like interface:
- `github.rest.issues.*` - Issues API
- `github.rest.repos.*` - Repos API
- `github.rest.pulls.*` - Pull Requests API
- `github.graphql()` - GraphQL support
- `github.paginate()` - Pagination support
- Automatic retry configuration

### 3. TypeScript Handler (`src/index.ts`)
- Installs Python dependencies
- Creates temporary Python script with context
- Executes Python code
- Captures and processes output
- Handles errors and sets results

### 4. Documentation
- **README.md**: Complete user guide with examples
- **EXAMPLES.md**: Advanced usage patterns
- **MIGRATION.md**: Guide for converting from github-script

## 🚀 Key Features

### ✨ Similar API to github-script
- Familiar `github`, `context`, and `core` objects
- Easy migration path for JavaScript users
- Comprehensive examples

### 🐍 Python-Specific Benefits
- Use Python's rich ecosystem
- Familiar syntax for Python developers
- Type hints and modern Python features
- Synchronous API calls (no async/await needed)

### 🔧 Advanced Features
- Configurable retries for API calls
- Support for GitHub Enterprise
- GraphQL query support
- Pagination helpers
- JSON and string output encoding
- Environment variable security patterns

## 📝 Usage Examples

### Basic
```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      core.info(f"Hello {context.actor}!")
```

### Issue Comment
```yaml
- uses: austenstone/github-python-script@v1
  with:
    script: |
      github.rest.issues.create_comment(
          owner=context.repo["owner"],
          repo=context.repo["repo"],
          issue_number=context.issue["number"],
          body="👋 Thanks!"
      )
```

### Return Values
```yaml
- uses: austenstone/github-python-script@v1
  id: get-info
  with:
    result-encoding: json
    script: |
      __result__ = {
          "actor": context.actor,
          "repo": context.repo["repo"]
      }
```

## 🔑 Key Differences from github-script

| Feature | github-script (JS) | github-python-script (Python) |
|---------|-------------------|------------------------------|
| Async calls | `await` required | Synchronous |
| Property names | camelCase | snake_case |
| Object access | `obj.property` | `obj["property"]` |
| Return values | `return value` | `__result__ = value` |
| String format | `` `text ${var}` `` | `f"text {var}"` |

## 🧪 Testing

Test workflow included in `.github/workflows/test.yml`:
- Basic context printing
- Repository information retrieval
- Return value testing (string and JSON)
- Multiple test scenarios

## 📦 Dependencies

### Python
- PyGithub >= 2.1.1
- requests >= 2.31.0

### Node.js
- @actions/core
- @actions/exec
- @actions/github

## 🎨 Design Decisions

1. **PyGithub**: Chosen for its mature API and community support
2. **Temporary Script Execution**: Safer than eval, allows proper error handling
3. **snake_case Conversion**: Follows Python conventions while maintaining familiar API
4. **Synchronous Calls**: Simpler Python code, no async complexity
5. **`__result__` Variable**: Clear way to return values without complex parsing

## 🔮 Future Enhancements

Potential improvements:
- [ ] Cache Python dependencies for faster execution
- [ ] Support for Python virtual environments
- [ ] More GitHub API wrappers (Projects, Discussions, etc.)
- [ ] Type stubs for better IDE support
- [ ] Pre-commit hooks example
- [ ] Integration with Python testing frameworks

## 🤝 Comparison with Original

This action maintains the same **ease of use** and **powerful features** as `actions/github-script`, but adapted for Python developers who prefer:
- Python's syntax and idioms
- Rich Python standard library
- Extensive Python package ecosystem
- Type hints and modern Python features

## 📊 Metrics

- **Lines of Python**: ~300
- **Lines of TypeScript**: ~120
- **Documentation**: 3 comprehensive guides
- **Examples**: 20+ use cases
- **Test Coverage**: Basic workflow testing

## 🎯 Success Criteria Met

✅ Execute Python scripts in GitHub Actions
✅ Provide GitHub API access similar to github-script
✅ Include context and core utilities
✅ Support retries and error handling
✅ Comprehensive documentation
✅ Migration guide for existing users
✅ Working examples and test workflow

---

**Built with 🐍 and ❤️ by Austen Stone**
