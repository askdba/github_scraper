#!/usr/bin/env python3
"""
GitHub Pulse Web Scraper
Scrapes the GitHub Pulse page directly using Selenium
Alternative to API-based approach when API access is limited
"""

import os
import json
import time
import argparse
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils import logger, export_to_json, format_timestamp

class GitHubPulseWebScraper:
    def __init__(self, owner, repo, headless=True):
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://github.com/{owner}/{repo}"
        self.pulse_url = f"{self.base_url}/pulse"
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            logger.error(f"Error initializing Chrome driver: {e}")
            print("Make sure Chrome and ChromeDriver are installed.")
            print("Install: pip install selenium && download ChromeDriver from https://chromedriver.chromium.org/")
            raise
    
    def __del__(self):
        """Clean up the driver"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass
    
    def scrape_pulse(self, period="monthly"):
        """
        Scrape pulse data for a given period
        period: 'daily', 'weekly', or 'monthly'
        """
        url = f"{self.pulse_url}?period={period}"
        logger.info(f"Fetching: {url}")
        
        try:
            self.driver.get(url)
            # Wait for meaningful content to load
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.Box.mt-3")))
            except TimeoutException:
                logger.warning("Timed out waiting for summary section, continuing anyway...")
            
            time.sleep(1)  # Extra breathing room
            
            data = {
                "repository": f"{self.owner}/{self.repo}",
                "period": period,
                "url": url,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "summary": {},
                "commits": [],
                "issues": [],
                "pull_requests": [],
                "contributors": []
            }
            
            # Scrape summary statistics
            try:
                # Look for the summary section - try a few common selectors
                summary_section = None
                for selector in ["div.Box.mt-3", "div.pulse-section", "div.Layout-main"]:
                    try:
                        summary_section = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if summary_section: break
                    except:
                        continue
                
                if summary_section:
                    # Extract key metrics
                    metrics = summary_section.find_elements(By.CSS_SELECTOR, "div.d-flex")
                    for metric in metrics:
                        try:
                            text = metric.text
                            if "commit" in text.lower():
                                data["summary"]["commits"] = text
                            elif "author" in text.lower():
                                data["summary"]["authors"] = text
                            elif "pull request" in text.lower():
                                data["summary"]["pull_requests"] = text
                            elif "issue" in text.lower():
                                data["summary"]["issues"] = text
                        except:
                            continue
                
            except NoSuchElementException:
                logger.warning("Summary section not found")
            
            # Scrape commit list
            try:
                commits_section = self.driver.find_elements(By.CSS_SELECTOR, "li.commit, div.commit")
                logger.info(f"Found {len(commits_section)} commit elements")
                
                for commit_elem in commits_section[:20]:  # Get first 20 commits
                    try:
                        commit_data = {}
                        
                        # Get commit message
                        message_elem = None
                        for selector in ["a.message", "code.commit-link", "a[data-pjax]"]:
                            try:
                                message_elem = commit_elem.find_element(By.CSS_SELECTOR, selector)
                                if message_elem: break
                            except: continue
                        
                        if message_elem:
                            commit_data["message"] = message_elem.text.strip()
                            commit_data["url"] = message_elem.get_attribute("href")
                        
                        # Get author
                        try:
                            author_elem = commit_elem.find_element(By.CSS_SELECTOR, "a.commit-author, span.author, a[data-hovercard-type='user']")
                            commit_data["author"] = author_elem.text.strip()
                        except:
                            commit_data["author"] = "Unknown"
                        
                        # Get timestamp
                        try:
                            time_elem = commit_elem.find_element(By.CSS_SELECTOR, "relative-time, time")
                            commit_data["timestamp"] = time_elem.get_attribute("datetime")
                        except:
                            commit_data["timestamp"] = None
                        
                        if commit_data.get("message"):
                            data["commits"].append(commit_data)
                    except Exception as e:
                        logger.debug(f"Error parsing commit: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error scraping commits: {e}")
            
            # Scrape issue activity
            try:
                issues_section = self.driver.find_elements(By.CSS_SELECTOR, "div.Issues, div.pulse-issues")
                for issue_elem in issues_section:
                    try:
                        issue_links = issue_elem.find_elements(By.CSS_SELECTOR, "a")
                        for link in issue_links:
                            issue_data = {
                                "title": link.text.strip(),
                                "url": link.get_attribute("href")
                            }
                            if issue_data["title"] and "/issues/" in issue_data["url"]:
                                data["issues"].append(issue_data)
                    except:
                        continue
            except Exception as e:
                logger.error(f"Error scraping issues: {e}")
            
            # Scrape pull request activity  
            try:
                pr_section = self.driver.find_elements(By.CSS_SELECTOR, "div.PullRequests, div.pulse-prs")
                for pr_elem in pr_section:
                    try:
                        pr_links = pr_elem.find_elements(By.CSS_SELECTOR, "a")
                        for link in pr_links:
                            pr_data = {
                                "title": link.text.strip(),
                                "url": link.get_attribute("href")
                            }
                            if pr_data["title"] and "/pull/" in pr_data["url"]:
                                data["pull_requests"].append(pr_data)
                    except:
                        continue
            except Exception as e:
                logger.error(f"Error scraping PRs: {e}")
            
            # Scrape contributors
            try:
                contrib_section = self.driver.find_elements(By.CSS_SELECTOR, "a[data-hovercard-type='user']")
                seen_contributors = set()
                
                for contrib_elem in contrib_section:
                    try:
                        username = contrib_elem.text.strip()
                        if username and username not in seen_contributors and " " not in username:
                            seen_contributors.add(username)
                            data["contributors"].append({
                                "username": username,
                                "profile_url": contrib_elem.get_attribute("href")
                            })
                    except:
                        continue
                        
            except Exception as e:
                logger.error(f"Error scraping contributors: {e}")
            
            return data
            
        except TimeoutException:
            logger.error("Page load timeout")
            return None
        except Exception as e:
            logger.error(f"Error scraping pulse page: {e}")
            return None
    
    def generate_report(self, period="monthly"):
        """Generate a human-readable report"""
        data = self.scrape_pulse(period)
        
        if not data:
            print("Failed to scrape data")
            return
        
        print("\n" + "=" * 80)
        print(f"GITHUB PULSE REPORT: {data['repository']}")
        print(f"Period: {period}")
        print("=" * 80)
        
        print("\nSUMMARY:")
        print("-" * 80)
        for key, value in data["summary"].items():
            print(f"{key.title()}: {value}")
        
        if data["commits"]:
            print(f"\nRECENT COMMITS ({len(data['commits'])} shown):")
            print("-" * 80)
            for i, commit in enumerate(data["commits"][:10], 1):
                ts = format_timestamp(commit.get('timestamp'))
                print(f"{i}. {commit['message']}")
                print(f"   by {commit['author']} - {ts}")
                print(f"   {commit['url']}")
                print()
        
        if data["contributors"]:
            print(f"\nCONTRIBUTORS ({len(data['contributors'])}):")
            print("-" * 80)
            for contrib in data["contributors"][:10]:
                print(f"  - {contrib['username']}: {contrib['profile_url']}")
        
        if data["issues"]:
            print(f"\nRECENT ISSUES ({len(data['issues'])}):")
            print("-" * 80)
            for issue in data["issues"][:5]:
                print(f"  - {issue['title']}")
                print(f"    {issue['url']}")
        
        if data["pull_requests"]:
            print(f"\nRECENT PULL REQUESTS ({len(data['pull_requests'])}):")
            print("-" * 80)
            for pr in data["pull_requests"][:5]:
                print(f"  - {pr['title']}")
                print(f"    {pr['url']}")
        
        print("\n" + "=" * 80)
    
    def export_json(self, period="monthly", output_file="pulse_web_report.json"):
        """Export scraped data as JSON"""
        data = self.scrape_pulse(period)
        if not data:
            return False
        return export_to_json(data, output_file)


def main():
    parser = argparse.ArgumentParser(description="GitHub Pulse Web Scraper")
    parser.add_argument("--owner", default="Altinity", help="Repository owner")
    parser.add_argument("--repo", default="altinityknowledgebase", help="Repository name")
    parser.add_argument("--period", default="monthly", choices=["daily", "weekly", "monthly"], help="Time period")
    parser.add_argument("--export", help="Output JSON filename")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Run browser in non-headless mode")
    
    args = parser.parse_args()
    
    print("GitHub Pulse Web Scraper")
    print("=" * 80)
    print(f"Repository: {args.owner}/{args.repo}")
    print(f"Period: {args.period}")
    print()
    
    try:
        scraper = GitHubPulseWebScraper(args.owner, args.repo, headless=args.headless)
        
        # Generate report
        scraper.generate_report(period=args.period)
        
        # Optionally export to JSON
        if args.export:
            scraper.export_json(period=args.period, output_file=args.export)
        else:
            print("\n" + "=" * 80)
            do_export = input("Export data to JSON? (y/n): ").strip().lower()
            if do_export == 'y':
                output_file = input("Output filename (default: pulse_web_report.json): ").strip()
                if not output_file:
                    output_file = "pulse_web_report.json"
                scraper.export_json(period=args.period, output_file=output_file)
        
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
