import os

def delete_files(directory_path): 

    print("Delete attempt")

    try:

        if os.path.exists(directory_path):

            for root, dirs, files in os.walk(directory_path, topdown=False):

                for file in files:

                    file_path = os.path.join(root, file)

                    if os.path.isfile(file_path):

                        print("Removing file:", file_path)

                        os.remove(file_path)  

                for dir in dirs:

                    dir_path = os.path.join(root, dir)

                    if os.path.isdir(dir_path):

                        print("Removing directory:", dir_path)

                        os.rmdir(dir_path)  

            print("All files and directories have been deleted.")
        else:
            print(f"The directory {directory_path} does not exist.")

    except Exception as e:
        
        print(f"Error: {e}")
