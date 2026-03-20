import os
import shutil

source_dir = os.path.join("data", "projects", "practice_06")
target_dir = "backup_folder"

os.makedirs(target_dir, exist_ok=True)

file_to_copy = "notes.txt"
source_path = os.path.join(source_dir, file_to_copy)
dest_path = os.path.join(target_dir, file_to_copy)

if os.path.exists(source_path):
    shutil.copy2(source_path, dest_path)
    print(f"Copied {file_to_copy} to {target_dir}")
    
    move_dest = os.path.join(target_dir, "moved_notes.txt")
    shutil.move(dest_path, move_dest)
    print(f"Moved and renamed to: {move_dest}")
else:
    print(f"Source file {file_to_copy} not found. Run create_list_dirs.py first.")