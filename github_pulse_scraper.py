#!/usr/bin/env python3
"""
GitHub Repository Pulse Data Scraper
Fetches contribution data for a repository similar to the GitHub Pulse page
"""

import os
import requests
import json
import argparse
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from dotenv import load_dotenv
from utils import logger, export_to_json, format_timestamp, print_scorecard_report

# Load environment variables from .env file
load_dotenv()

class GitHubPulseScraper:
    def __init__(self, owner, repo, token=None):
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
        elif os.getenv("GITHUB_TOKEN"):
            self.headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"
    
    def get_repo_info(self):
        """Get basic repository information"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_commits(self, since_date):
        """Get commits since a specific date"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/commits"
        params = {
            "since": since_date.isoformat(),
            "per_page": 100
        }
        
        all_commits = []
        page = 1
        
        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            commits = response.json()
            if not commits:
                break
                
            all_commits.extend(commits)
            
            # Check if there are more pages
            if "next" not in response.links:
                break
            page += 1
        
        return all_commits
    
    def get_issues(self, since_date, state="all"):
        """Get issues since a specific date"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        params = {
            "since": since_date.isoformat(),
            "state": state,
            "per_page": 100
        }
        
        all_issues = []
        page = 1
        
        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            issues = response.json()
            if not issues:
                break
            
            # Filter out pull requests (they appear in issues endpoint too)
            issues = [i for i in issues if "pull_request" not in i]
            all_issues.extend(issues)
            
            if "next" not in response.links:
                break
            page += 1
        
        return all_issues
    
    def get_pull_requests(self, since_date, state="all"):
        """Get pull requests since a specific date"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls"
        params = {
            "state": state,
            "per_page": 100,
            "sort": "updated",
            "direction": "desc"
        }
        
        all_prs = []
        page = 1
        
        while True:
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            prs = response.json()
            if not prs:
                break
            
            # Filter PRs updated since the date
            filtered_prs = [
                pr for pr in prs 
                if datetime.fromisoformat(pr["updated_at"].replace("Z", "+00:00")) >= since_date
            ]
            
            if not filtered_prs:
                break
                
            all_prs.extend(filtered_prs)
            
            if "next" not in response.links:
                break
            page += 1
        
        return all_prs
    
    def analyze_contributors(self, commits):
        """Analyze contributor activity from commits"""
        contributors = defaultdict(int)
        for commit in commits:
            if commit.get("author"):
                author = commit["author"].get("login", "Unknown")
                contributors[author] += 1
        return dict(sorted(contributors.items(), key=lambda x: x[1], reverse=True))
    
    def generate_report(self, period_days=30):
        """Generate a comprehensive pulse report"""
        since_date = datetime.now(timezone.utc) - timedelta(days=period_days)
        
        try:
            # --- DATA FETCHING ---
            repo_info = self.get_repo_info()
            commits = self.get_commits(since_date)
            issues = self.get_issues(since_date)
            prs = self.get_pull_requests(since_date)
            
            # --- DATA PROCESSING ---
            contributors = self.analyze_contributors(commits)
            
            issues_opened = [i for i in issues if datetime.fromisoformat(i["created_at"].replace("Z", "+00:00")) >= since_date]
            issues_closed = [i for i in issues if i["state"] == "closed" and i.get("closed_at") and datetime.fromisoformat(i["closed_at"].replace("Z", "+00:00")) >= since_date]
            
            prs_opened = [p for p in prs if datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")) >= since_date]
            closed_prs = [p for p in prs if p["state"] == "closed" and p.get("closed_at") and datetime.fromisoformat(p["closed_at"].replace("Z", "+00:00")) >= since_date]
            prs_merged = [p for p in closed_prs if p.get("merged_at")]
            prs_closed_unmerged = [p for p in closed_prs if not p.get("merged_at")]

            # --- REPORTING ---
            print_scorecard_report(
                repo_info,
                commits,
                contributors,
                issues_opened,
                issues_closed,
                prs_opened,
                prs_merged,
                prs_closed_unmerged,
                period_days
            )
            
        except Exception as e:
            logger.error(f"An error occurred during report generation: {e}")
            # Optionally re-raise or handle specific exceptions
            return

        print("\n" + "=" * 80)
        print("Report complete!")
        
    def export_json(self, period_days=30, output_file="pulse_report.json"):
        """Export pulse data as JSON"""
        since_date = datetime.now(timezone.utc) - timedelta(days=period_days)
        
        data = {
            "repository": f"{self.owner}/{self.repo}",
            "period_days": period_days,
            "since_date": since_date.isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            data["repository_info"] = self.get_repo_info()
            data["commits"] = self.get_commits(since_date)
            data["issues"] = self.get_issues(since_date)
            data["pull_requests"] = self.get_pull_requests(since_date)
            data["contributors"] = self.analyze_contributors(data["commits"])
            
            return export_to_json(data, output_file)
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="GitHub Repository Pulse Data Scraper")
    parser.add_argument("--owner", default="Altinity", help="Repository owner")
    parser.add_argument("--repo", default="altinityknowledgebase", help="Repository name")
    parser.add_argument("--days", type=int, default=30, help="Period in days (default: 30)")
    parser.add_argument("--token", help="GitHub Personal Access Token")
    parser.add_argument("--export", help="Output JSON filename")
    
    args = parser.parse_args()
    
    # Create scraper instance
    scraper = GitHubPulseScraper(args.owner, args.repo, args.token)
    
    # Generate report
    try:
        scraper.generate_report(period_days=args.days)
        
        # Optionally export to JSON
        if args.export:
            scraper.export_json(period_days=args.days, output_file=args.export)
        else:
            print("\n" + "=" * 80)
            do_export = input("Export data to JSON? (y/n): ").strip().lower()
            if do_export == 'y':
                output_file = input("Output filename (default: pulse_report.json): ").strip()
                if not output_file:
                    output_file = "pulse_report.json"
                scraper.export_json(period_days=args.days, output_file=output_file)
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            logger.error("Rate limit exceeded! Consider adding a GitHub token.")
            print("To fix: Set GITHUB_TOKEN in .env or use --token argument.")
        else:
            logger.error(f"HTTP Error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
