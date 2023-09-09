import os
import shutil
import datetime
import time

# Declare the path of both folders
source_path = input("Source folder path: ")
replica_path = input("Replica folder path: ")
log_file_path = input("Log File path: ")

# Track the last modification in each file
file_modification_times = {}

# Task description: "File creation/copying/removal operations should be logged to a file and to the console output"
def log_event(event):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{current_time} - {event}"
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{log_message}\n")
    print(log_message)

# The main function where the sync is coded 
def synchronize_function(source_folder, replica_folder):
    try:
        source_items = set(os.listdir(source_folder))
        replica_items = set(os.listdir(replica_folder))

        # Verifying if any modified, new, or deleted files exist in the source folder
        modified_files = []
        new_files = list(source_items - replica_items)
        deleted_files = list(replica_items - source_items)

        # Check for modified files
        for item in source_items:
            source_item_path = os.path.join(source_folder, item)
            replica_item_path = os.path.join(replica_folder, item)

            if os.path.isfile(source_item_path) and os.path.isfile(replica_item_path):
                source_mod_time = os.path.getmtime(source_item_path)
                replica_mod_time = file_modification_times.get(replica_item_path, 0)

                if source_mod_time > replica_mod_time:
                    modified_files.append(item)
                    file_modification_times[replica_item_path] = source_mod_time

        # Log and print the differences between the two folders
        if new_files:
            message = "New files:\n"
            for item in new_files:
                message += f" - Added {item}\n"
            log_event(message)

        if deleted_files:
            message = "Deleted files:\n"
            for item in deleted_files:
                message += f" - Deleted {item}\n"
            log_event(message)

        if modified_files:
            message = "Modified files:\n"
            for item in modified_files:
                message += f" - Modified {item}\n"
            log_event(message)

        # If any difference exists, sync automatically
        if new_files or deleted_files or modified_files:
            # The sync process
            for item in new_files + modified_files:
                source_item_path = os.path.join(source_folder, item)
                replica_item_path = os.path.join(replica_folder, item)

                # copytree if the item we want to copy is a folder
                # copy2 is for files
                # Check https://docs.python.org/3/library/shutil.html
                if os.path.isdir(source_item_path):
                    log_event(f"Started copying folder {item}")
                    shutil.copytree(source_item_path, replica_item_path)
                    log_event(f"Finished copying folder {item}")
                else:
                    log_event(f"Started copying file {item}")
                    shutil.copy2(source_item_path, replica_item_path)
                    log_event(f"Finished copying file {item}")

            for item in deleted_files:
                replica_item_path = os.path.join(replica_folder, item)

                if os.path.isdir(replica_item_path):
                    log_event(f"Started deleting folder {item}")
                    shutil.rmtree(replica_item_path)
                    log_event(f"Finished deleting folder {item}")
                else:
                    log_event(f"Started deleting file {item}")
                    os.remove(replica_item_path)
                    log_event(f"Finished deleting file {item}")

            # Recursively synchronize subdirectories
            for item in source_items & replica_items:
                source_item_path = os.path.join(source_folder, item)
                replica_item_path = os.path.join(replica_folder, item)

                if os.path.isdir(source_item_path) and os.path.isdir(replica_item_path):
                    synchronize_function(source_item_path, replica_item_path)

            log_event("Sync Completed.")

    except FileNotFoundError as e:
        log_event(f"Error: {e}")

# Set up automatic synchronization
auto_sync = False

while True:
    if auto_sync:
        # Synchronize the folders without asking for confirmation
        synchronize_function(source_path, replica_path)
    else:
        # Ask the user to enable automatic synchronization
        auto_sync_decision = input("Do you want to enable automatic synchronization? (y/n): ").strip().lower()
        if auto_sync_decision == "y":
            auto_sync = True
            auto_sync_interval = int(input("Enter the interval (in seconds) for automatic synchronization: "))

    # Sleep for the specified interval before the next synchronization
    if auto_sync:
        time.sleep(auto_sync_interval)
