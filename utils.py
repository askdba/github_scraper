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
