import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("github_scraper")

def export_to_json(data, output_file):
    """Common logic for exporting data to JSON"""
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Data exported to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error exporting data to JSON: {e}")
        return False

def format_timestamp(ts):
    """Format timestamp for reporting"""
    if not ts:
        return "N/A"
    try:
        if isinstance(ts, str):
            # Handle ISO format strings
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(ts)

def print_scorecard_report(
    repo_info,
    commits,
    contributors,
    issues_opened,
    issues_closed,
    prs_opened,
    prs_merged,
    prs_closed_unmerged,
    period_days
):
    """Prints a formatted, scorecard-style report to the console."""
    
    # --- Helper for dynamic bar charts ---
    def get_bar_chart(value, max_value, bar_length=20):
        if max_value == 0:
            return " " * bar_length
        bar = "█" * int((value / max_value) * bar_length)
        return f"{bar:<{bar_length}}"

    # --- Header ---
    print("\n" + "╔" + "═" * 78 + "╗")
    print(f"║ {'GitHub Pulse Scorecard:':<48} {repo_info['full_name']:>28} ║")
    dynamic_content = f"{'Period:':<8} Last {period_days} days"
    padding = max(0, 76 - len(dynamic_content))
    print(f"║ {dynamic_content}{' ' * padding} ║")
    print("╚" + "═" * 78 + "╝")

    # --- Key Metrics ---
    total_commits = len(commits)
    total_issues = len(issues_opened) + len(issues_closed)
    total_prs = len(prs_opened) + len(prs_merged) + len(prs_closed_unmerged)
    
    print("\n" + "┌─ SUMMARY OVERVIEW " + "─" * 61 + "┐")
    print(f"│ Total Commits: {total_commits:<5} | Total Issues: {total_issues:<5} | Total PRs: {total_prs:<5} │")
    print("└" + "─" * 78 + "┘")

    # --- Commits & Contributors ---
    print("\n" + "┌─ COMMITS & CONTRIBUTORS " + "─" * 55 + "┐")
    print(f"│ Total Commits: {total_commits:<5} │ Active Contributors: {len(contributors):<4} │")
    
    if contributors:
        print("│" + "─" * 28 + "┬" + "─" * 49 + "│")
        print(f"│ {'Top Contributors':<27} │ {'Commits':<10} {'Activity':<22} │")
        print("│" + "─" * 28 + "┼" + "─" * 49 + "│")
        
        max_commits = max(contributors.values()) if contributors else 0
        for i, (author, count) in enumerate(list(contributors.items())[:5], 1):
            bar = get_bar_chart(count, max_commits)
            print(f"│ {i}. {author:<24} │ {count:<10} {bar} │")
    print("└" + "─" * 78 + "┘")
    
    # --- Issues ---
    print("\n" + "┌─ ISSUES " + "─" * 70 + "┐")
    print(f"│ Opened: {len(issues_opened):<5} │ Closed: {len(issues_closed):<5} │")
    if issues_opened:
        print("│" + "─" * 15 + "┬" + "─" * 62 + "│")
        print(f"│ {'Recent Issues':<14} │ {'Title':<50} {'Author':<10} │")
        print("│" + "─" * 15 + "┼" + "─" * 62 + "│")
        for issue in issues_opened[:3]:
            title = issue['title'][:48] + ".." if len(issue['title']) > 50 else issue['title']
            author = issue['user']['login'][:10]
            print(f"│ #{issue['number']:<14} │ {title:<50} {author:<10} │")
    print("└" + "─" * 78 + "┘")
    
    # --- Pull Requests ---
    print("\n" + "┌─ PULL REQUESTS " + "─" * 64 + "┐")
    print(f"│ Opened: {len(prs_opened):<5} │ Merged: {len(prs_merged):<5} │ Not Merged: {len(prs_closed_unmerged):<5} │")
    if prs_opened:
        print("│" + "─" * 15 + "┬" + "─" * 62 + "│")
        print(f"│ {'Recent PRs':<14} │ {'Title':<40} {'Author':<10} {'Status':>9} │")
        print("│" + "─" * 15 + "┼" + "─" * 62 + "│")
        for pr in prs_opened[:3]:
            title = pr['title'][:38] + ".." if len(pr['title']) > 40 else pr['title']
            author = pr['user']['login'][:10]
            status = "Merged" if pr.get("merged_at") else ("Closed" if pr["state"] == "closed" else "Open")
            print(f"│ #{pr['number']:<14} │ {title:<40} {author:<10} {status:>9} │")
    print("└" + "─" * 78 + "┘")
    
    # --- Footer ---
    print("\n" + "Report generated at: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 80)
