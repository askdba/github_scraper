#!/usr/bin/env python3
"""
Example usage scripts for GitHub Pulse scrapers
"""

from github_pulse_scraper import GitHubPulseScraper
import os
from datetime import datetime, timedelta, timezone

# ============================================================================
# Example 1: Basic usage with console report
# ============================================================================
def example_basic_report():
    """Generate a basic console report"""
    print("Example 1: Basic Console Report")
    print("=" * 80)
    
    scraper = GitHubPulseScraper(
        owner="Altinity",
        repo="altinityknowledgebase",
        token=os.getenv("GITHUB_TOKEN")  # Optional: set GITHUB_TOKEN env var
    )
    
    scraper.generate_report(period_days=30)


# ============================================================================
# Example 2: Export to JSON for analysis
# ============================================================================
def example_json_export():
    """Export pulse data to JSON"""
    print("\nExample 2: JSON Export")
    print("=" * 80)
    
    scraper = GitHubPulseScraper(
        owner="Altinity",
        repo="altinityknowledgebase",
        token=os.getenv("GITHUB_TOKEN")
    )
    
    output_file = f"pulse_report_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    scraper.export_json(period_days=30, output_file=output_file)
    print(f"\nData saved to: {output_file}")


# ============================================================================
# Example 3: Compare different time periods
# ============================================================================
def example_time_comparison():
    """Compare activity across different time periods"""
    print("\nExample 3: Time Period Comparison")
    print("=" * 80)
    
    scraper = GitHubPulseScraper(
        owner="Altinity",
        repo="altinityknowledgebase",
        token=os.getenv("GITHUB_TOKEN")
    )
    
    periods = [7, 14, 30, 90]
    
    for days in periods:
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        commits = scraper.get_commits(since_date)
        issues = scraper.get_issues(since_date)
        prs = scraper.get_pull_requests(since_date)
        contributors = scraper.analyze_contributors(commits)
        
        print(f"\nLast {days} days:")
        print(f"  Commits: {len(commits)}")
        print(f"  Active contributors: {len(contributors)}")
        print(f"  Issues: {len(issues)}")
        print(f"  Pull requests: {len(prs)}")


# ============================================================================
# Example 4: Detailed contributor analysis
# ============================================================================
def example_contributor_analysis():
    """Analyze contributor activity in detail"""
    print("\nExample 4: Contributor Analysis")
    print("=" * 80)
    
    scraper = GitHubPulseScraper(
        owner="Altinity",
        repo="altinityknowledgebase",
        token=os.getenv("GITHUB_TOKEN")
    )
    
    since_date = datetime.now(timezone.utc) - timedelta(days=90)  # Last 3 months
    commits = scraper.get_commits(since_date)
    contributors = scraper.analyze_contributors(commits)
    
    print(f"\nContributor activity (last 90 days):")
    print(f"Total commits: {len(commits)}")
    print(f"Total contributors: {len(contributors)}")
    print("\nTop 10 contributors:")
    
    for i, (author, count) in enumerate(list(contributors.items())[:10], 1):
        percentage = (count / len(commits)) * 100
        print(f"  {i}. {author:20} - {count:3} commits ({percentage:5.1f}%)")


# ============================================================================
# Example 5: Batch process multiple repositories
# ============================================================================
def example_batch_processing():
    """Process multiple repositories"""
    print("\nExample 5: Batch Processing Multiple Repos")
    print("=" * 80)
    
    repos = [
        ("Altinity", "altinityknowledgebase"),
        ("Altinity", "clickhouse-operator"),
        # Add more repos as needed
    ]
    
    token = os.getenv("GITHUB_TOKEN")
    
    for owner, repo in repos:
        print(f"\n{'=' * 80}")
        print(f"Processing: {owner}/{repo}")
        print('=' * 80)
        
        try:
            scraper = GitHubPulseScraper(owner, repo, token)
            
            # Quick summary
            since_date = datetime.now(timezone.utc) - timedelta(days=30)
            commits = scraper.get_commits(since_date)
            issues = scraper.get_issues(since_date)
            prs = scraper.get_pull_requests(since_date)
            
            print(f"Last 30 days:")
            print(f"  Commits: {len(commits)}")
            print(f"  Issues: {len(issues)}")
            print(f"  Pull requests: {len(prs)}")
            
            # Export to JSON
            output_file = f"{repo}_pulse_30d.json"
            scraper.export_json(period_days=30, output_file=output_file)
            
        except Exception as e:
            print(f"Error processing {owner}/{repo}: {e}")


# ============================================================================
# Example 6: Weekly digest email format
# ============================================================================
def example_weekly_digest():
    """Generate a weekly digest format suitable for email"""
    print("\nExample 6: Weekly Digest")
    print("=" * 80)
    
    scraper = GitHubPulseScraper(
        owner="Altinity",
        repo="altinityknowledgebase",
        token=os.getenv("GITHUB_TOKEN")
    )
    
    since_date = datetime.now(timezone.utc) - timedelta(days=7)
    commits = scraper.get_commits(since_date)
    issues = scraper.get_issues(since_date)
    prs = scraper.get_pull_requests(since_date)
    contributors = scraper.analyze_contributors(commits)
    
    # Format as email digest
    digest = f"""
Weekly Activity Digest - Altinity Knowledge Base
Week ending: {datetime.now(timezone.utc).strftime('%B %d, %Y')}
{'=' * 80}

📊 SUMMARY
  • {len(commits)} commits by {len(contributors)} contributors
  • {len(issues)} issues updated
  • {len(prs)} pull requests active

👥 TOP CONTRIBUTORS THIS WEEK
"""
    
    for i, (author, count) in enumerate(list(contributors.items())[:5], 1):
        digest += f"  {i}. {author} - {count} commits\n"
    
    digest += f"\n🔨 RECENT COMMITS\n"
    for commit in commits[:5]:
        sha = commit["sha"][:7]
        author = commit["commit"]["author"]["name"]
        message = commit["commit"]["message"].split("\n")[0][:50]
        digest += f"  • [{sha}] {message} - {author}\n"
    
    digest += f"\n📝 ACTIVE ISSUES\n"
    opened_issues = [i for i in issues 
                    if datetime.fromisoformat(i["created_at"].replace("Z", "+00:00")) >= since_date]
    for issue in opened_issues[:3]:
        digest += f"  • #{issue['number']}: {issue['title']}\n"
    
    print(digest)
    
    # Save to file
    with open("weekly_digest.txt", "w") as f:
        f.write(digest)
    print("\nDigest saved to: weekly_digest.txt")


# ============================================================================
# Example 7: Custom metrics calculation
# ============================================================================
def example_custom_metrics():
    """Calculate custom metrics"""
    print("\nExample 7: Custom Metrics")
    print("=" * 80)
    
    scraper = GitHubPulseScraper(
        owner="Altinity",
        repo="altinityknowledgebase",
        token=os.getenv("GITHUB_TOKEN")
    )
    
    since_date = datetime.now(timezone.utc) - timedelta(days=30)
    commits = scraper.get_commits(since_date)
    issues = scraper.get_issues(since_date)
    prs = scraper.get_pull_requests(since_date)
    
    # Calculate metrics
    opened_issues = [i for i in issues 
                    if datetime.fromisoformat(i["created_at"].replace("Z", "+00:00")) >= since_date]
    closed_issues = [i for i in issues 
                    if i["state"] == "closed" and i.get("closed_at") 
                    and datetime.fromisoformat(i["closed_at"].replace("Z", "+00:00")) >= since_date]
    
    opened_prs = [pr for pr in prs 
                 if datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00")) >= since_date]
    merged_prs = [pr for pr in prs 
                 if pr.get("merged_at") 
                 and datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00")) >= since_date]
    
    print("\nCustom Metrics (Last 30 days):")
    print(f"  Commits per day: {len(commits) / 30:.1f}")
    print(f"  Issue close rate: {len(closed_issues) / max(len(opened_issues), 1) * 100:.1f}%")
    print(f"  PR merge rate: {len(merged_prs) / max(len(opened_prs), 1) * 100:.1f}%")
    
    # Contributor diversity
    contributors = scraper.analyze_contributors(commits)
    if contributors:
        top_contributor_percentage = (list(contributors.values())[0] / len(commits)) * 100
        print(f"  Top contributor share: {top_contributor_percentage:.1f}%")


# ============================================================================
# Main menu
# ============================================================================
def main():
    """Main menu to run examples"""
    print("GitHub Pulse Scraper - Usage Examples")
    print("=" * 80)
    print("\nAvailable examples:")
    print("  1. Basic console report")
    print("  2. Export to JSON")
    print("  3. Time period comparison")
    print("  4. Contributor analysis")
    print("  5. Batch process multiple repos")
    print("  6. Weekly digest")
    print("  7. Custom metrics")
    print("  8. Run all examples")
    print("  0. Exit")
    
    examples = {
        "1": example_basic_report,
        "2": example_json_export,
        "3": example_time_comparison,
        "4": example_contributor_analysis,
        "5": example_batch_processing,
        "6": example_weekly_digest,
        "7": example_custom_metrics,
    }
    
    while True:
        choice = input("\nSelect example (0-8): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "8":
            for func in examples.values():
                func()
                print("\n" + "=" * 80 + "\n")
        elif choice in examples:
            examples[choice]()
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    # Set your GitHub token as environment variable:
    # export GITHUB_TOKEN="your_token_here"
    
    # Or set it here (not recommended for security):
    # os.environ["GITHUB_TOKEN"] = "your_token_here"
    
    main()
