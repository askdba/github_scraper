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
    """Prints a perfectly aligned, scorecard-style report using basic ASCII."""
    
    WIDTH = 78

    def truncate(text, max_len):
        """Truncates text with an ellipsis if it's too long."""
        if not text:
            return ""
        if len(text) > max_len:
            return text[:max_len - 2] + ".."
        return text

    def print_row(items, widths, dividers=True):
        """Prints a row with specified content and widths."""
        row_str = "|" if dividers else " "
        for i, item in enumerate(items):
            # Pad content to the full width of the column
            padded_item = f" {item} ".ljust(widths[i] + 2)
            row_str += padded_item
            if dividers and i < len(items) - 1:
                row_str += "|"
        row_str += "|" if dividers else " "
        print(row_str)

    def print_divider(widths, is_header=False):
        """Prints a +---+---+ style divider."""
        divider = "+"
        for i, width in enumerate(widths):
            char = "=" if is_header else "-"
            divider += char * (width + 2)
            divider += "+"
        print(divider)

    # --- Header ---
    repo_name_full = repo_info.get('full_name', 'N/A')
    repo_name = truncate(repo_name_full, 35)
    header_title = f"GitHub Pulse Scorecard: {repo_name}"
    period_text = f"Period: Last {period_days} days"

    print("\n" + "=" * (WIDTH + 2))
    print(f" {header_title.ljust(WIDTH)}")
    print(f" {period_text.ljust(WIDTH)}")
    print("=" * (WIDTH + 2))

    # --- Key Metrics ---
    total_commits = len(commits)
    total_issues = len(issues_opened) + len(issues_closed)
    total_prs = len(prs_opened) + len(prs_merged) + len(prs_closed_unmerged)
    
    c_text = f"Total Commits: {total_commits}"
    i_text = f"Total Issues: {total_issues}"
    p_text = f"Total PRs: {total_prs}"
    
    print("\nSUMMARY OVERVIEW")
    print_divider([25, 25, 26])
    print_row([c_text, i_text, p_text], [25, 25, 26])
    print_divider([25, 25, 26])

    # --- Commits & Contributors ---
    print("\nCOMMITS & CONTRIBUTORS")
    c_widths = [4, 33, 10, 25]
    print_divider(c_widths)
    summary_items = [
        "", 
        f"Total Commits: {total_commits}", 
        "", 
        f"Active Contributors: {len(contributors)}"
    ]
    print_row(summary_items, c_widths)
    
    if contributors:
        print_divider(c_widths, is_header=True)
        print_row(["#", "Top Contributor", "Commits", "Activity"], c_widths)
        print_divider(c_widths, is_header=True)
        
        max_commits = max(contributors.values()) if contributors else 0
        for i, (author, count) in enumerate(list(contributors.items())[:5], 1):
            author_display = truncate(author, c_widths[1] - 1)
            bar_len = c_widths[3] - 1
            bar = "█" * int((count / max_commits) * bar_len) if max_commits > 0 else ""
            print_row([str(i), author_display, str(count), bar], c_widths)
    print_divider(c_widths)

    # --- Issues ---
    print("\nISSUES")
    i_widths = [8, 55, 11]
    print_divider(i_widths)
    summary_text = f"Opened: {len(issues_opened)} | Closed: {len(issues_closed)}"
    print_row(["", summary_text, ""], i_widths)

    if issues_opened:
        print_divider(i_widths, is_header=True)
        print_row(["ID", "Title", "Author"], i_widths)
        print_divider(i_widths, is_header=True)
        for issue in issues_opened[:3]:
            issue_id = f"#{issue['number']}"
            title = truncate(issue['title'], i_widths[1] - 1)
            author = truncate(issue['user']['login'], i_widths[2] - 1)
            print_row([issue_id, title, author], i_widths)
    print_divider(i_widths)

    # --- Pull Requests ---
    print("\nPULL REQUESTS")
    p_widths = [8, 43, 12, 9]
    print_divider(p_widths)
    pr_summary_text = f"Opened: {len(prs_opened)} | Merged: {len(prs_merged)} | Not Merged: {len(prs_closed_unmerged)}"
    print_row(["", pr_summary_text, "", ""], p_widths)
    
    if prs_opened:
        print_divider(p_widths, is_header=True)
        print_row(["ID", "Title", "Author", "Status"], p_widths)
        print_divider(p_widths, is_header=True)
        for pr in prs_opened[:3]:
            pr_id = f"#{pr['number']}"
            title = truncate(pr['title'], p_widths[1] - 1)
            author = truncate(pr['user']['login'], p_widths[2] - 1)
            status = truncate("Merged" if pr.get("merged_at") else ("Closed" if pr["state"] == "closed" else "Open"), p_widths[3])
            print_row([pr_id, title, author, status], p_widths)
    print_divider(p_widths)
    
    # --- Footer ---
    print(f"\nReport generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * (WIDTH + 2))
