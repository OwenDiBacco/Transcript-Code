import moviepy.editor as mp
import speech_recognition as sr
import os
import zipfile
import soundfile as sf
from pydub import AudioSegment
import requests
import msal
import threading
import uuid
import asyncio

from queue import Queue
from pydub.silence import split_on_silence

import Text_GUI ## opens new GUI
import tkinter as tk
from tkinter import ttk
import threading
import time

class ProgressBarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Progress Bar Example")
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)

    def update_progress(self, current, end):
        if current <= end:
            # print(current, "/", end)
            self.progress["maximum"] = end
            self.progress["value"] = current
        else:
            self.close()

    def close(self):
        self.root.destroy()

def update_bar_in_main_thread(app, current, end):
    app.update_progress(current, end)

def thread_function(app, root, total_steps):
    while current_mp4 < total_steps: 
    # for i in range(total_steps + 1):
        root.after(0, update_bar_in_main_thread, app, current_mp4, total_steps) 
        
        # time.sleep(0.5)  
    

def start_thread(app, root, total_mp4s):
    
    threading.Thread(target=thread_function, args=(app, root, total_mp4s)).start()


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

            print("Opening: ", output_file)
            
            # len([f for f in  if  -1 # os.path.isfile(os.path.join(folder_path, f))])

            number_of_files = 0

            for file in os.listdir(folder_path):

                if file.endswith('.txt'):

                    number_of_files += 1

            while len(recorded) < number_of_files -1:
                
                print("Files #: ", number_of_files)
                print("Recorded: ", recorded, " Iterations ", iterations)

                iterations += 1

                # print(len(recorded), len(os.listdir(folder_path)))

                for filename in os.listdir(folder_path):

                    print("Working on: ", filename)

                    # print(len(str(iterations)))

                    string_iterations = ""

                    if iterations < 10:

                        string_iterations = "0" + str(iterations)

                    else:

                        string_iterations = str(iterations)

                    if filename.endswith(".txt") and ((string_iterations)) in filename and filename not in recorded: 

                        print("Combining: ", filename)

                        recorded.append(filename)

                        file_path = os.path.join(folder_path, filename)

                        with open(file_path, 'r') as infile:

                            outfile.write(infile.read())
                            outfile.write("\n")  

# combine_text_files("C:\\Users\\CMP_OwDiBacco\\Downloads\\MP4-Text\\Txt", "All")

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

    global split_output_folder, split_count
    
    recognizer = sr.Recognizer()
    
    text = ''
    
    try:

        with sr.AudioFile(output_wav_path) as source:

            print("Converting: ", source)

            audio = recognizer.record(source)

            length = sf.SoundFile(output_wav_path)

            seconds = length.frames / length.samplerate

            print("Second: ", seconds)

            text = recognizer.recognize_google(audio)

    except:
        
        if True:

            split_folder = os.path.join(split_output_folder, filename)
            
            text = split_and_convert_wav(output_wav_path, split_folder, filename)

        else:


            print("Error Converting ", output_wav_path, ": ", Exception)

            split_folder = os.path.join(split_output_folder, filename)

            os.makedirs(split_folder, exist_ok=True)

            split_count = 0

            max_iter = split_wav(output_wav_path, seconds, [], split_folder, filename)

            print("Max Iteration: ", max_iter)

            current = 0

            print("Current: ", current, " Max Iter Expoent: ", max_iter ** 2)

            while current < max_iter ** 2:

                for wav in os.listdir(split_folder):

                    output_wav_path = os.path.join(split_folder, wav)

                    if output_wav_path.lower().endswith('.wav') and wav[0] == str(max_iter) and wav[3] == str(current):

                        current += 1

                        print("Working on: ", output_wav_path)

                        with sr.AudioFile(output_wav_path) as source:

                            audio = recognizer.record(source)

                            t = recognizer.recognize_google(audio)

                            print(t)

                            text += t + " "

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


def split_and_convert_wav(wav_path, split_path, filename):

    chunk_text = []

    audio = AudioSegment.from_wav(wav_path)

    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)

    print("Chunks: ", chunks)

    recognizer = sr.Recognizer()

    split_path = os.path.join(split_path)

    split_path = os.path.join(split_path, filename)

    os.makedirs(split_path, exist_ok=True)

    for i, chunk in enumerate(chunks):

        full_wav_path = os.path.join(split_path, f"chunk{i+1}.wav")

        chunk.export(full_wav_path, format="wav")

        ## print("Working on wav: ", f"chunk{i+1}.wav", " Length: ", len(chunk) / 1000)

        if len(chunk) > 0: # not empty
    
            with sr.AudioFile(full_wav_path) as source:

                audio_chunk = recognizer.record(source)

                try:

                    text = recognizer.recognize_google(audio_chunk)

                    chunk_text.append(text)

                    ## print("Completed")

                except: # sr.UnknownValueError: # no sound 
                    
                    pass

    final_text = ''.join(chunk_text)
    return final_text

def split_wav(wav_path, seconds, arr, output_folder, name, split_iterations=0):

    global split_count

    if seconds < 350:

        arr.append([wav_path])
        return 0

    a = AudioSegment.from_wav(wav_path)

    print("ID: ", name, " Created")

    split_time = seconds / 2 * 1000
    
    segmentUno = a[:split_time]
    segmentDos = a[split_time:]
    
    wav_uno_path = os.path.join(output_folder, f"{split_iterations}_{split_count}. {uuid.uuid4()}_segment_1_uno.wav")
    wav_dos_path = os.path.join(output_folder, f"{split_iterations}_{split_count +1}. {uuid.uuid4()}_segment_1_dos.wav")
    
    segmentUno.export(wav_uno_path, format="wav")
    segmentDos.export(wav_dos_path, format="wav")
    
    max_iter = split_wav(wav_uno_path, len(segmentUno) / 1000, arr, output_folder, name, split_iterations + 1)
    split_wav(wav_dos_path, len(segmentDos) / 1000, arr, output_folder, name, split_iterations + 1)

    split_count += 2

    print(f"Split iteration {split_iterations} done for: {wav_path}")

    return max(max_iter, split_iterations)
 

def check_queue():
    try:
        
        run_async(current_mp4, total_mp4s)

    except Exception:

        pass 

    root.after(100, check_queue)

def loop_through_directory(queue ,extracted_files, extract_path, folders, original_path):

    global reset_extract_path, current_mp4, total_mp4s

    queue.put("In Queue")

    print("reset path? ", reset_extract_path)

    print("original_path: ", original_path)

    print("extract path: ", extract_path)

    for content in extracted_files:

        print("content: ", content)

        file_path = os.path.join(extract_path, content)

        print("file_path: ", file_path)

        if '.mp4' in content[-4:]:

            ## check_queue()

            current_mp4 += 1

            ## asyncio.run(updated_bar(current_mp4, total_mp4s))

            # root.after(0, run_async(current_mp4, total_mp4s))

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

            loop_through_directory(queue, extracted_files, extract_path, folders, original_path)

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

split_output_folder = f"{root_path}\\Wav\\Split\\" # trying to delete

# Declare paths ^

if not os.path.exists(extract_to_path):
    os.makedirs(extract_to_path)

if not os.path.exists(wav_path):
    os.makedirs(wav_path)

if not os.path.exists(split_output_folder):
    os.makedirs(split_output_folder)

if not os.path.exists(txt_folder):
    os.makedirs(txt_folder)

# Extract Zip File 

with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(extract_to_path)

root = tk.Tk()

app = ProgressBarApp(root)

current_mp4 = 0

total_mp4s = find_total_files(extract_to_path)

extracted_files = os.listdir(extract_to_path)

queue = Queue()

# thread = threading.Thread(target=loop_through_directory, args=(queue, extracted_files, extract_to_path, "", extract_to_path))
# thread.start()

split_count = 0

## bar_thread = threading.Thread(target=updated_bar, args=(current_mp4, total_mp4s))
convert_thread = threading.Thread(target=loop_through_directory, args=(queue, extracted_files, extract_to_path, "", extract_to_path))

## bar_thread.start()
convert_thread.start()
start_thread(app, root, total_mp4s)
root.mainloop()

# check_queue()

zip_file_name = os.path.splitext(os.path.basename(zip_file))[0]

output_zip_path = zip_output(txt_folder, zip_file_name)

zip_file_path = output_zip_path

file_name = os.path.basename(zip_file_path)

## bar_thread.join()
## convert_thread.join()

## token = get_access_token(client_id, authority, client_secret, scopes)
## upload_file_to_onedrive(zip_file_path, token, file_name) ## i dont want to figure this out: BadRequest