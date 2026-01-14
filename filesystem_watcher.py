import time
import shutil
import sys
import os  # Added to find absolute paths
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION ---
# 1. Open your specific Obsidian Vault folder.
# 2. Copy the full path (e.g., C:\Users\Name\Documents\AI_Employee_Vault)
# 3. Paste it below, keeping the 'r' if you are on Windows.
VAULT_PATH = r"D:\abdullah\Digital_FTE_1\AI_Employee_Vault" 
DROP_FOLDER = "Input_Dropzone" 

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        # Convert to absolute path to prevent confusion
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        
        # Create the destination if missing
        if not self.needs_action.exists():
            print(f"⚠️  Creating new folder at: {self.needs_action}")
            self.needs_action.mkdir(parents=True, exist_ok=True)
        else:
            print(f"✅ Target Vault Found: {self.needs_action}")

    def on_created(self, event):
        if event.is_directory: return
        
        source = Path(event.src_path)
        # Wait slightly for the file to release its lock
        time.sleep(1)
        
        if not source.exists(): return

        dest = self.needs_action / f'FILE_{source.name}'
        
        try:
            # The 'Move' operation deletes from source and adds to dest
            shutil.move(str(source), str(dest))
            print(f"🚀 Moved file to: {dest}")
            self.create_metadata(source, dest)
        except Exception as e:
            print(f"❌ Error: {e}")

    def create_metadata(self, source: Path, dest: Path):
        meta_path = dest.with_suffix('.md')
        meta_path.write_text(f'''---
type: file_drop
original_name: {source.name}
timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}
status: pending
---
Please process this file.''', encoding='utf-8')

if __name__ == "__main__":
    # Print the exact paths so you can see where files will go
    print(f"--- DIAGNOSTICS ---")
    print(f"📂 Dropzone: {os.path.abspath(DROP_FOLDER)}")
    print(f"📂 Destination: {os.path.abspath(VAULT_PATH)}\\Needs_Action")
    print(f"-------------------")

    Path(DROP_FOLDER).mkdir(exist_ok=True)
    event_handler = DropFolderHandler(VAULT_PATH)
    observer = Observer()
    observer.schedule(event_handler, DROP_FOLDER, recursive=False)
    observer.start()
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()