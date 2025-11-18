import shutil
import os
from datetime import datetime

def create_backup():
    # Generate timestamp for backup folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir_name = f"backup_{timestamp}"
    source_dir = os.getcwd()
    destination_dir = os.path.join(source_dir, backup_dir_name)

    # Define patterns/directories to ignore
    ignore_patterns = shutil.ignore_patterns(
        "__pycache__", 
        "*.pyc", 
        ".git", 
        ".pytest_cache", 
        ".venv", 
        "node_modules", 
        "backup_*",  # Avoid recursive backups of backups
        "artifacts",
        "*.log"      # Optional: skip logs to save space
    )

    try:
        print(f"Creating backup at: {destination_dir}")
        shutil.copytree(source_dir, destination_dir, ignore=ignore_patterns)
        print(f"✅ Backup created successfully: {backup_dir_name}")
    except Exception as e:
        print(f"❌ Error creating backup: {e}")

if __name__ == "__main__":
    create_backup()
