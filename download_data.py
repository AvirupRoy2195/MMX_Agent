import kagglehub
import os
import shutil

# Download latest version
path = kagglehub.dataset_download("datatattle/dt-mart-market-mix-modeling")

print("Path to dataset files:", path)

# Copy files to current directory for easier access
target_dir = "data"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

for file in os.listdir(path):
    full_file_name = os.path.join(path, file)
    if os.path.isfile(full_file_name):
        shutil.copy(full_file_name, target_dir)
        print(f"Copied {file} to {target_dir}")
