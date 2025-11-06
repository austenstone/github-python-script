"""GitHub Python Script - Python runtime for GitHub Actions"""
import json
import os
import sys
from typing import Any, Dict, Optional
from github import Github, GithubException, Auth
from github.GithubRetry import GithubRetry
import urllib3.util.retry


class Core:
    """Wrapper for @actions/core functionality"""
    
    @staticmethod
    def debug(message: str) -> None:
        print(f"::debug::{message}")
    
    @staticmethod
    def info(message: str) -> None:
        print(message)
    
    @staticmethod
    def warning(message: str) -> None:
        print(f"::warning::{message}")
    
    @staticmethod
    def error(message: str) -> None:
        print(f"::error::{message}")
    
    @staticmethod
    def set_failed(message: str) -> None:
        print(f"::error::{message}")
        sys.exit(1)
    
    @staticmethod
    def set_output(name: str, value: Any) -> None:
        output_file = os.getenv("GITHUB_OUTPUT")
        if output_file:
            with open(output_file, "a") as f:
                f.write(f"{name}={value}\n")
    
    @staticmethod
    def export_variable(name: str, value: Any) -> None:
        env_file = os.getenv("GITHUB_ENV")
        if env_file:
            with open(env_file, "a") as f:
                f.write(f"{name}={value}\n")
    
    @staticmethod
    def set_secret(secret: str) -> None:
        print(f"::add-mask::{secret}")
    
    @staticmethod
    def get_input(name: str, required: bool = False) -> str:
        val = os.getenv(f"INPUT_{name.upper().replace('-', '_')}", "")
        if required and not val:
            raise ValueError(f"Input required and not supplied: {name}")
        return val


class Context:
    """Wrapper for GitHub Actions context"""
    
    def __init__(self):
        self.payload = self._load_payload()
        self.event_name = os.getenv("GITHUB_EVENT_NAME", "")
        self.sha = os.getenv("GITHUB_SHA", "")
        self.ref = os.getenv("GITHUB_REF", "")
        self.workflow = os.getenv("GITHUB_WORKFLOW", "")
        self.action = os.getenv("GITHUB_ACTION", "")
        self.actor = os.getenv("GITHUB_ACTOR", "")
        self.job = os.getenv("GITHUB_JOB", "")
        self.run_number = int(os.getenv("GITHUB_RUN_NUMBER", "0"))
        self.run_id = int(os.getenv("GITHUB_RUN_ID", "0"))
        self.api_url = os.getenv("GITHUB_API_URL", "https://api.github.com")
        self.server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
        self.graphql_url = os.getenv("GITHUB_GRAPHQL_URL", "https://api.github.com/graphql")
    
    def _load_payload(self) -> Dict[str, Any]:
        event_path = os.getenv("GITHUB_EVENT_PATH")
        if event_path and os.path.exists(event_path):
            with open(event_path, "r") as f:
                return json.load(f)
        return {}
    
    @property
    def repo(self) -> Dict[str, str]:
        repository = os.getenv("GITHUB_REPOSITORY", "/")
        owner, repo = repository.split("/", 1)
        return {"owner": owner, "repo": repo}
    
    @property
    def issue(self) -> Dict[str, Any]:
        payload = self.payload
        return {
            "owner": self.repo["owner"],
            "repo": self.repo["repo"],
            "number": (
                payload.get("issue", {}).get("number") or
                payload.get("pull_request", {}).get("number") or
                payload.get("number", 0)
            )
        }


class GitHubWrapper:
    """Wrapper around PyGithub to provide similar API to octokit"""
    
    def __init__(self, token: str, base_url: Optional[str] = None, retries: int = 0, 
                 retry_exempt_status_codes: Optional[list] = None):
        retry_exempt_status_codes = retry_exempt_status_codes or [400, 401, 403, 404, 422]
        
        if retries > 0:
            retry_config = GithubRetry(
                total=retries,
                backoff_factor=1,
                status_forcelist=[x for x in range(400, 600) if x not in retry_exempt_status_codes]
            )
        else:
            retry_config = None
        
        self._github = Github(
            auth=Auth.Token(token) if token else None,
            base_url=base_url or "https://api.github.com",
            retry=retry_config
        )
        self.rest = RestAPI(self._github)
        self._token = token
        self._base_url = base_url or "https://api.github.com"
    
    def get_repo(self, owner: str, repo: str):
        """Get repository object"""
        return self._github.get_repo(f"{owner}/{repo}")
    
    def get_user(self, username: str):
        """Get user object"""
        return self._github.get_user(username)
    
    def graphql(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute GraphQL query"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }
        
        data = {"query": query}
        if variables:
            data["variables"] = variables
        
        response = requests.post(
            f"{self._base_url}/graphql",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def paginate(self, method, *args, **kwargs):
        """Paginate through results"""
        results = method(*args, **kwargs)
        all_results = []
        
        if hasattr(results, 'totalCount'):
            # It's a paginated list
            for item in results:
                all_results.append(item)
        else:
            all_results.append(results)
        
        return all_results


class RestAPI:
    """REST API wrapper to match octokit's interface"""
    
    def __init__(self, github: Github):
        self._github = github
        self.issues = IssuesAPI(github)
        self.repos = ReposAPI(github)
        self.pulls = PullsAPI(github)
        self.actions = ActionsAPI(github)


class IssuesAPI:
    """Issues API wrapper"""
    
    def __init__(self, github: Github):
        self._github = github
    
    def create_comment(self, owner: str, repo: str, issue_number: int, body: str):
        """Create issue comment"""
        repository = self._github.get_repo(f"{owner}/{repo}")
        issue = repository.get_issue(issue_number)
        return issue.create_comment(body)
    
    def add_labels(self, owner: str, repo: str, issue_number: int, labels: list):
        """Add labels to issue"""
        repository = self._github.get_repo(f"{owner}/{repo}")
        issue = repository.get_issue(issue_number)
        return issue.add_to_labels(*labels)
    
    def list_for_repo(self, owner: str, repo: str, **kwargs):
        """List issues for repository"""
        repository = self._github.get_repo(f"{owner}/{repo}")
        return repository.get_issues(**kwargs)
    
    def get(self, owner: str, repo: str, issue_number: int):
        """Get a single issue"""
        repository = self._github.get_repo(f"{owner}/{repo}")
        return repository.get_issue(issue_number)


class ReposAPI:
    """Repos API wrapper"""
    
    def __init__(self, github: Github):
        self._github = github
    
    def get(self, owner: str, repo: str):
        """Get repository"""
        return self._github.get_repo(f"{owner}/{repo}")
    
    def get_commit(self, owner: str, repo: str, ref: str):
        """Get commit"""
        repository = self._github.get_repo(f"{owner}/{repo}")
        return repository.get_commit(ref)


class PullsAPI:
    """Pull requests API wrapper"""
    
    def __init__(self, github: Github):
        self._github = github
    
    def list(self, owner: str, repo: str, **kwargs):
        """List pull requests"""
        repository = self._github.get_repo(f"{owner}/{repo}")
        return repository.get_pulls(**kwargs)
    
    def get(self, owner: str, repo: str, pull_number: int):
        """Get a single pull request"""
        repository = self._github.get_repo(f"{owner}/{repo}")
        return repository.get_pull(pull_number)


class ActionsAPI:
    """Actions API wrapper"""
    
    def __init__(self, github: Github):
        self._github = github


def run_script(script: str, github: GitHubWrapper, context: Context, core: Core) -> Any:
    """Execute the Python script with provided context"""
    # Create execution environment
    exec_globals = {
        'github': github,
        'context': context,
        'core': core,
        'os': os,
        'sys': sys,
        'json': json,
    }
    
    # Execute the script
    exec(script, exec_globals)
    
    # Return the result if __result__ was set
    return exec_globals.get('__result__')
