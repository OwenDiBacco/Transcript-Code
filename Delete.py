import os
import glob
folder = r".\d4571d2c-c71d-478c-8a24-03578b19aae9\Wav"
for file_path in glob.glob(os.path.join(folder, "*")):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Failed to delete {file_path}: {e}")
