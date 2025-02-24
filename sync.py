import os
import shutil
import time
import hashlib
import argparse
from datetime import datetime

def calculate_md5(file_path):
    """Calculate the MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def log_action(log_file, message):
    """Logs an action and prints it to the console."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(log_file, 'a') as log:
        log.write(log_entry + '\n')

def sync_folders(source, replica, log_file):
    """Synchronizes the source folder with the replica."""
    if not os.path.exists(replica):
        os.makedirs(replica)
        log_action(log_file, f"Created directory: {replica}")
    
    source_files = {}
    replica_files = {}
    
    # Maps the files in the source folder
    for root, _, files in os.walk(source):
        for file in files:
            source_path = os.path.join(root, file)
            rel_path = os.path.relpath(source_path, source)
            source_files[rel_path] = source_path
    
    # Maps the files in the replica folder
    for root, _, files in os.walk(replica):
        for file in files:
            replica_path = os.path.join(root, file)
            rel_path = os.path.relpath(replica_path, replica)
            replica_files[rel_path] = replica_path
    
    # Copy/Updates files from the source to the replica
    for rel_path, source_path in source_files.items():
        replica_path = os.path.join(replica, rel_path)
        if rel_path not in replica_files or calculate_md5(source_path) != calculate_md5(replica_path):
            os.makedirs(os.path.dirname(replica_path), exist_ok=True)
            shutil.copy2(source_path, replica_path)
            log_action(log_file, f"File copied/updated: {replica_path}")
    
    # Remove files from the replica that are not in the source
    for rel_path, replica_path in replica_files.items():
        if rel_path not in source_files:
            os.remove(replica_path)
            log_action(log_file, f"File removed: {replica_path}")
    
    # Remove empty directories from the replica
    for root, dirs, _ in os.walk(replica, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                log_action(log_file, f"Directory removed: {dir_path}")

def main():
    parser = argparse.ArgumentParser(description="Periodically synchronizes two folders.")
    parser.add_argument("source", nargs="?", default="./source", help="Path to the source folder")
    parser.add_argument("replica", nargs="?", default="./replica", help="Path to the replica folder")
    parser.add_argument("interval", nargs="?", type=int, default=60, help="Sync interval in seconds")
    parser.add_argument("log_file", nargs="?", default="./logs/sync.log", help="Path to the log file")
    
    args = parser.parse_args()

    print(f"Synchronization starded from {args.source} to {args.replica} every {args.interval} seconds.")
    
    while True:

        print("Executing synchronization...")
        sync_folders(args.source, args.replica, args.log_file)
        print(f"Synchronization completed. Next in {args.interval} seconds.")
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
