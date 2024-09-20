import moviepy.editor as mp
import speech_recognition as sr
import os
import zipfile
import soundfile as sf
from pydub import AudioSegment
import requests
import msal

import Text_GUI ## opens new GUI
import Progress_Bar

def contains_text_files(directory_path):
    try:
        
        files = os.listdir(directory_path)
        
        
        for file in files:

            if file.lower().endswith('.txt'):

                return True
        
        return False
    
    except FileNotFoundError:

        return False
    
    except PermissionError:

        return False

def combine_text_files(folder_path, output_file_name):

    if contains_text_files(folder_path):

        output_file = os.path.join(folder_path, output_file_name + ".txt")
    
        recorded = []

        iterations = -1

        with open(output_file, 'w') as outfile:

            while len(recorded) < len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]) -1:

                iterations += 1

                # print(len(recorded), len(os.listdir(folder_path)))

                for filename in os.listdir(folder_path):

                    # print(len(str(iterations)))

                    string_iterations = ""

                    if len(str(iterations)) == 1:

                        string_iterations = "0" + str(iterations)

                    else:

                        string_iterations = str(iterations)

                    if filename.endswith(".txt") and ((string_iterations) + " - ") in filename and filename not in recorded: 

                        print("Combining: ", filename)

                        recorded.append(filename)

                        file_path = os.path.join(folder_path, filename)

                        with open(file_path, 'r') as infile:

                            outfile.write(infile.read())
                            outfile.write("\n")  

## combine_text_files("C:\\Users\\CMP_OwDiBacco\\Downloads\\MP4-Text\\Txt\\03 - Browsing History", "All")

def write_text(text, folders, filename):

    print(filename, " Text Created")

    file_path = os.path.join(txt_folder, folders)

    os.makedirs(file_path, exist_ok=True)

    with open(os.path.join(file_path, filename + ".txt"), "w") as txt_file:

        txt_file.write(text)
    
    print("Removing")

    ## os.remove(file_path) # i dont freaking know

    return file_path

def convert_wav_to_text(filename, output_wav_path):
    
    recognizer = sr.Recognizer()

    try:

        with sr.AudioFile(output_wav_path) as source:

            audio = recognizer.record(source)

            length = sf.SoundFile(output_wav_path)

            seconds = length.frames / length.samplerate

            split = False

            if seconds > 350:

                split = True

            text = ""

            if not split:

                text = recognizer.recognize_google(audio)

            else:

                for wav in os.listdir(split_output_folder):

                    output_wav_path = os.path.join(split_output_folder, wav)

                    with sr.AudioFile(output_wav_path) as source:

                        audio = recognizer.record(source)

                        t = recognizer.recognize_google(audio)

                        text += t + " "

    except:

        print("Error Converting ", output_wav_path, ": ", Exception)

    return text

def convert_mp4_to_wav(file_path, folders):

    filename = os.path.splitext(os.path.basename(file_path))[0]

    video = mp.VideoFileClip(file_path)
    
    output_wav_path = os.path.join(wav_path, folders)
    
    os.makedirs(output_wav_path, exist_ok=True)
    
    output_wav_path = os.path.join(output_wav_path, filename + '.wav')
    
    print("Output WAV Path: ", output_wav_path)
    
    video.audio.write_audiofile(output_wav_path)
    
    print("WAV Created: ", output_wav_path)
    
    return filename, output_wav_path

def split_wav(path, seconds, arr, output_folder, name):

    if not os.path.exists(output_folder):

        os.makedirs(output_folder)

    if seconds > 350:

        a = AudioSegment.from_wav(path)

        split_time = seconds / 2 * 1000

        segmentUno = a[:split_time]
        segmentDos = a[split_time:]

        arr.append(segmentUno)
        arr.append(segmentDos)

        split_wav(None, len(segmentUno) / 1000, arr, output_folder, name)
        split_wav(None, len(segmentDos) / 1000, arr, output_folder, name)

    else:

        for i, segment in enumerate(arr):

            segment_path = os.path.join(output_folder, f"{name} segment_{i+1}.wav")
            segment.export(segment_path, format="wav")

    return arr


def loop_through_directory(extracted_files, extract_path, folders, original_path):

    global reset_extract_path, current_mp4, total_mp4s

    print("reset path? ", reset_extract_path)

    print("original_path: ", original_path)

    print("extract path: ", extract_path)

    for content in extracted_files:

        print("content: ", content)

        file_path = os.path.join(extract_path, content)

        print("file_path: ", file_path)

        if '.mp4' in content[-4:]:

            current_mp4 += 1

            Progress_Bar.app.update_progress(current_mp4, total_mp4s)
            
            print("Starting: ", content)
            
            filename, wav = convert_mp4_to_wav(file_path, folders) # returns the filename and wav

            print("filename: ", filename)

            write_text(convert_wav_to_text(filename, wav), folders, filename)

        elif os.path.isdir(file_path):
            
            foldername = os.path.splitext(content)[0]

            print("Opening: ", foldername)

            extracted_files = os.listdir(file_path)

            print("Files in Folder ", foldername, ": ", extracted_files)

            extract_path = file_path

            folders = os.path.join(folders, content)

            print("Folders: ", folders)

            loop_through_directory(extracted_files, extract_path, folders, original_path)

            extract_path = original_path
            
            folders = ""

            print("extract_path: ", extract_path)

    print("Completed") # nice

    txt_directory = os.path.join(txt_folder, folders)

    combine_text_files(txt_directory, "All")

    ## extract_path = extract_to_path 

    reset_extract_path = True

    print("extract_path: ", extract_path)

def find_total_files(folder):

    mp4_count = 0

    for item in os.listdir(folder):
        
        item_path = os.path.join(folder, item)
        
        if os.path.isdir(item_path):

            mp4_count += find_total_files(item_path)
        
        elif item.endswith(".mp4"):

            mp4_count += 1
    
    return mp4_count


def zip_output(text_folder, zip_file_name):
    
    ## downloads_folder = os.path.join(os.path.expanduser("~"), 'Downloads')

    zip_file_name = zip_file_name + "_Transcripts.zip"

    zip_file_path = os.path.join(txt_folder, zip_file_name)
    
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        print("Creating Zip in Downloads: ", zip_file_path)

        for foldername, subfolders, filenames in os.walk(text_folder):

            for filename in filenames:

                file_path = os.path.join(foldername, filename)

                arcname = os.path.relpath(file_path, text_folder)

                zipf.write(file_path, arcname)

    return zip_file_path

def get_access_token(client_id, authority, client_secret, scopes):

    app = msal.ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret
    )

    result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:

        return result["access_token"]
    
    else:

        raise Exception("Could not obtain access token. Check credentials.")

# Function to upload a file to OneDrive

def upload_file_to_onedrive(zip_file_path, access_token, file_name):
    print("Uploading: ", zip_file_path)

    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/your_folder/{file_name}:/content"

    try:

        with open(zip_file_path, 'rb') as file_data:

            headers = {

                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/zip',
            }

            response = requests.put(upload_url, headers=headers, data=file_data)

            if response.status_code == 201:

                print(f"File '{file_name}' uploaded successfully to OneDrive.")

            else:

                print(f"Failed to upload the file: {response.status_code}, {response.text}")

    except FileNotFoundError:

        print(f"File '{zip_file_path}' not found.")

    except requests.RequestException as e:

        print(f"An error occurred: {e}")

# automatically creates Convert folder for this program

# Declare paths v

reset_extract_path = False

root_path = Text_GUI.root_path

print("root: ", root_path)

zip_file = Text_GUI.zip_path

print("zip: ", zip_file)

txt_folder = Text_GUI.txt_path

if Text_GUI.clicked:

    txt_folder = f"{root_path}\\{txt_folder}"

zip_file_path = f"{zip_file}"

extract_to_path = f"{root_path}\\MP4"

wav_path = f"{root_path}\\Wav" # trying to delete

if txt_folder[-1] != "\\":

    txt_folder = f"{txt_folder}\\"

else:

    txt_folder = f"{txt_folder}"

print("txt folder: ", txt_folder)

txt_path = txt_folder.split("\\")

print(txt_path)

split_output_folder = f"{root_path}\\Wav\\Split" # trying to delete

# Declare paths ^

def main():

    global current_mp4, total_mp4s

    if not os.path.exists(extract_to_path):
        os.makedirs(extract_to_path)

    if not os.path.exists(wav_path):
        os.makedirs(wav_path)

    if not os.path.exists(txt_folder):
        os.makedirs(txt_folder)

    # Extract Zip File 
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:

        zip_ref.extractall(extract_to_path)

    current_mp4 = 0
    total_mp4s = find_total_files(extract_to_path)

    extracted_files = os.listdir(extract_to_path)

    loop_through_directory(extracted_files, extract_to_path, "", extract_to_path)

    zip_file_name = os.path.splitext(os.path.basename(zip_file))[0]

    output_zip_path = zip_output(txt_folder, zip_file_name)

    # Upload To Outlook

    '''

    client_id = "317264f1-552f-4612-a6ba-f1db8d74a872"
    tenant_id = "e34fd78b-f48d-4235-9787-fef76723be14"
    client_secret = "yTb8Q~XVAgzlQMXKA_~vXinFkhkPz.v1mNw2db9Y"

    # value: yTb8Q~XVAgzlQMXKA_~vXinFkhkPz.v1mNw2db9Y
    # ID: df681347-a3e4-41ca-bc58-fa8d1a3d62a7

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    scopes = ["https://graph.microsoft.com/.default"]

    '''

    # Path to your ZIP file
    zip_file_path = output_zip_path

    file_name = os.path.basename(zip_file_path)

    ## token = get_access_token(client_id, authority, client_secret, scopes)

    ## upload_file_to_onedrive(zip_file_path, token, file_name) ## i dont want to figure this out: BadRequest

if __name__ == '__main__':

    main()