import pytest
from utils import print_scorecard_report

def test_print_scorecard_report_includes_merged_prs(capsys):
    # Setup mock data
    repo_info = {"full_name": "test/repo", "description": "test repo"}
    commits = []
    contributors = {}
    issues_opened = []
    issues_closed = []
    
    prs_opened = [
        {"number": 1, "title": "Open PR 1", "user": {"login": "user1"}, "state": "open", "updated_at": "2024-01-01T00:00:00Z", "created_at": "2024-01-01T00:00:00Z"}
    ]
    prs_merged = [
        {"number": 2, "title": "Merged PR 2", "user": {"login": "user2"}, "state": "closed", "merged_at": "2024-01-02T00:00:00Z", "updated_at": "2024-01-02T00:00:00Z", "created_at": "2024-01-01T00:00:00Z"}
    ]
    prs_closed_unmerged = []
    
    print_scorecard_report(
        repo_info,
        commits,
        contributors,
        issues_opened,
        issues_closed,
        prs_opened,
        prs_merged,
        prs_closed_unmerged,
        period_days=30
    )
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify both opened and merged PRs are in the report
    assert "Open PR 1" in output
    assert "Merged PR 2" in output
    assert "Merged" in output
    assert "Open" in output

def test_print_scorecard_report_deduplicates_prs(capsys):
    # Setup mock data where same PR is in both opened and merged
    repo_info = {"full_name": "test/repo", "description": "test repo"}
    commits = []
    contributors = {}
    issues_opened = []
    issues_closed = []
    
    pr = {"number": 1, "title": "Both PR 1", "user": {"login": "user1"}, "state": "closed", "merged_at": "2024-01-02T00:00:00Z", "updated_at": "2024-01-02T00:00:00Z", "created_at": "2024-01-01T00:00:00Z"}
    
    prs_opened = [pr]
    prs_merged = [pr]
    prs_closed_unmerged = []
    
    print_scorecard_report(
        repo_info,
        commits,
        contributors,
        issues_opened,
        issues_closed,
        prs_opened,
        prs_merged,
        prs_closed_unmerged,
        period_days=30
    )
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify the PR is only listed once
    assert output.count("Both PR 1") == 1
    assert "Merged" in output
