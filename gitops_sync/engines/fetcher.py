import os
import yaml
from github import Github
from github.GithubException import GithubException


def load_environment_config(
    repo_name: str,
    environment: str,
    file_path: str = "gitops-config.yaml",
    token_env: str = "GITHUB_TOKEN",
) -> dict:
    """
    Load a specific environment configuration from a YAML file stored in a GitHub repository.

    Args:
        repo_name (str): Repository in the format "owner/repo"
        environment (str): Target environment (e.g. "dev", "prod")
        file_path (str): Path to the YAML file in the repository
        token_env (str): Name of the environment variable containing the GitHub token

    Returns:
        dict: Configuration of the requested environment

    Raises:
        ValueError: If token or environment is missing
        FileNotFoundError: If the file does not exist
        RuntimeError: If a GitHub API error occurs
    """

    # 1. Read GitHub token from environment variable
    token = os.getenv(token_env)
    if not token:
        raise ValueError(f"Environment variable '{token_env}' not found")

    try:
        github_client = Github(token)
        repo = github_client.get_repo(repo_name)
        file_content = repo.get_contents(file_path)
        yaml_text = file_content.decoded_content.decode("utf-8")
        config = yaml.safe_load(yaml_text)

        if not config or "environments" not in config:
            raise ValueError("Invalid YAML structure: 'environments' key missing")

        environments = config["environments"]

        if environment not in environments:
            raise ValueError(f"Environment '{environment}' not found")

        return environments[environment]

    except GithubException as e:
        raise RuntimeError(f"GitHub API error: {e.data}") from e
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}") from e