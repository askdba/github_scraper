import pytest
import responses
from datetime import datetime, timedelta
from github_pulse_scraper import GitHubPulseScraper

@pytest.fixture
def scraper():
    return GitHubPulseScraper("test_owner", "test_repo", token="test_token")

@responses.activate
def test_get_repo_info(scraper):
    responses.add(
        responses.GET,
        "https://api.github.com/repos/test_owner/test_repo",
        json={"full_name": "test_owner/test_repo", "stargazers_count": 10},
        status=200
    )
    
    info = scraper.get_repo_info()
    assert info["full_name"] == "test_owner/test_repo"
    assert info["stargazers_count"] == 10

@responses.activate
def test_get_commits(scraper):
    since_date = datetime.now() - timedelta(days=7)
    responses.add(
        responses.GET,
        "https://api.github.com/repos/test_owner/test_repo/commits",
        json=[
            {"sha": "123", "author": {"login": "user1"}, "commit": {"message": "msg1", "author": {"name": "User 1", "date": "2024-01-01T00:00:00Z"}}},
            {"sha": "456", "author": {"login": "user2"}, "commit": {"message": "msg2", "author": {"name": "User 2", "date": "2024-01-02T00:00:00Z"}}}
        ],
        status=200
    )
    
    commits = scraper.get_commits(since_date)
    assert len(commits) == 2
    assert commits[0]["sha"] == "123"

def test_analyze_contributors(scraper):
    commits = [
        {"author": {"login": "user1"}},
        {"author": {"login": "user1"}},
        {"author": {"login": "user2"}},
        {"author": None},  # Test handle missing author
    ]
    
    contributors = scraper.analyze_contributors(commits)
    assert contributors["user1"] == 2
    assert contributors["user2"] == 1
    assert "Unknown" not in contributors # Since we filter by commit.get("author")

import subprocess
from unittest.mock import patch
from github_pulse_scraper import get_local_repo_info

def test_get_local_repo_info_https():
    with patch("subprocess.check_output", return_value=b"https://github.com/myorg/myrepo.git\n"):
        owner, repo = get_local_repo_info()
        assert owner == "myorg"
        assert repo == "myrepo"

def test_get_local_repo_info_ssh():
    with patch("subprocess.check_output", return_value=b"git@github.com:myorg/myrepo.git\n"):
        owner, repo = get_local_repo_info()
        assert owner == "myorg"
        assert repo == "myrepo"

def test_get_local_repo_info_fallback():
    with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "git")):
        owner, repo = get_local_repo_info()
        assert owner == "Altinity"
        assert repo == "altinityknowledgebase"

@responses.activate
def test_list_owner_repos_org(scraper):
    responses.add(
        responses.GET,
        "https://api.github.com/orgs/test_owner/repos",
        json=[{"name": "repo1"}, {"name": "repo2"}],
        status=200
    )
    repos = scraper.list_owner_repos()
    assert len(repos) == 2
    assert repos[0]["name"] == "repo1"

@responses.activate
def test_list_owner_repos_user_fallback(scraper):
    # Org endpoint returns 404
    responses.add(
        responses.GET,
        "https://api.github.com/orgs/test_owner/repos",
        json={"message": "Not Found"},
        status=404
    )
    # User endpoint succeeds
    responses.add(
        responses.GET,
        "https://api.github.com/users/test_owner/repos",
        json=[{"name": "user_repo1"}],
        status=200
    )
    repos = scraper.list_owner_repos()
    assert len(repos) == 1
    assert repos[0]["name"] == "user_repo1"

