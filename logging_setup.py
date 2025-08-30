import logging
from colorama import Fore, Style, init
import csv
from datetime import datetime, timezone
import os

# Resets the color of the log after each print/log
init(autoreset=True)

# Directories paths for logs
main_source = "c:/Users/OLUWAPELUMI/.vscode/python/aws resource cleaner & auditor"
log_path = os.path.join(main_source, "csv_log")
os.makedirs(log_path, exist_ok=True)   # Create csv_log/ if not exists

log_file = os.path.join(log_path, "report.log")
csv_file = os.path.join(log_path, "report.csv")


# Custom Formatter for Console Colors
class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN, 
        logging.WARNING: Fore.YELLOW, 
        logging.ERROR: Fore.RED, 
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"


# Logging Setup
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

console = logging.StreamHandler()
console.setFormatter(ColorFormatter("%(levelname)s - %(message)s"))

logging.basicConfig(level=logging.INFO, handlers=[console, file_handler])


# CSV Setup
def init_csv():
    #Create a CSV file with headers if it does not exist.
    if not os.path.exists(csv_file):
        with open(csv_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Service", "Resource", "Action", "Status", "Timestamp"])


def log_csv(service, resource, action, status):
    #Append an entry to the CSV report
    with open(csv_file, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            service,
            resource,
            action,
            status,
            datetime.now(timezone.utc).isoformat()
        ])
