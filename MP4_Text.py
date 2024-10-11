import os
import zipfile
import Text_GUI
import threading
import tkinter as tk
import moviepy.editor as mp
import speech_recognition as sr
from tkinter import ttk
from pydub import AudioSegment
from pydub.silence import split_on_silence

class ProgressBarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Progress Bar")

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

def contains_text_files(directory_path):
    files = os.listdir(directory_path)
    for file in files:
        if file.lower().endswith('.txt'):
            return True
        
    return False
    

def combine_text_files(folder_path, output_file_name):
    if contains_text_files(folder_path):
        output_file = os.path.join(folder_path, output_file_name + ".txt")
        recorded = []
        iterations = -1
        with open(output_file, 'w') as outfile:
            number_of_files = 0
            for file in os.listdir(folder_path):
                if file.endswith('.txt'):
                    number_of_files += 1

            while len(recorded) < number_of_files -1:
                iterations += 1
                for filename in os.listdir(folder_path):
                    string_iterations = ""
                    if iterations < 10:
                        string_iterations = "0" + str(iterations)

                    else:
                        string_iterations = str(iterations)

                    if filename.endswith(".txt") and ((string_iterations)) in filename and filename not in recorded:
                        recorded.append(filename)
                        file_path = os.path.join(folder_path, filename)
                        with open(file_path, 'r') as infile:
                            outfile.write(infile.read())
                            outfile.write("\n")  


def write_text(text, folders, filename):
    global current_mp4
    current_mp4 += 1 # progress the progress bar
    file_path = os.path.join(txt_folder, folders)
    os.makedirs(file_path, exist_ok=True)
    with open(os.path.join(file_path, filename + ".txt"), "w") as txt_file:
        txt_file.write(text)
    
    return file_path


def convert_wav_to_text(filename, output_wav_path):
    global current_mp4, split_output_folder, split_count
    current_mp4 += 1 # progress the progress bar
    recognizer = sr.Recognizer()
    text = ''
    try:
        with sr.AudioFile(output_wav_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)

    except: # add the exception
        split_folder = os.path.join(split_output_folder, filename)
        text = split_and_convert_wav(output_wav_path, split_folder, filename)

    return text


def convert_mp4_to_wav(file_path, folders):
    global current_mp4
    current_mp4 += 1 # progress the progress bar
    filename = os.path.splitext(os.path.basename(file_path))[0]
    video = mp.VideoFileClip(file_path)
    output_wav_path = os.path.join(wav_path, folders)
    os.makedirs(output_wav_path, exist_ok=True)
    output_wav_path = os.path.join(output_wav_path, filename + '.wav')
    video.audio.write_audiofile(output_wav_path)
    return filename, output_wav_path


def split_and_convert_wav(wav_path, split_path, filename):
    chunk_text = []
    audio = AudioSegment.from_wav(wav_path)
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)
    recognizer = sr.Recognizer()
    split_path = os.path.join(split_path, filename)
    os.makedirs(split_path, exist_ok=True)
    for i, chunk in enumerate(chunks):
        full_wav_path = os.path.join(split_path, f"chunk{i+1}.wav")
        chunk.export(full_wav_path, format="wav")
        if len(chunk) > 0:
            with sr.AudioFile(full_wav_path) as source:
                audio_chunk = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_chunk)
                    chunk_text.append(text)

                except: # don't know why this is here
                    print("An error occured in the splitting function")
                
    final_text = ''.join(chunk_text)
    return final_text


def loop_through_directory(extracted_files, extract_path, folders, original_path):
    global current_mp4, total_mp4s #?
    for content in extracted_files:
        file_path = os.path.join(extract_path, content)
        if '.mp4' in content[-4:]:
            current_mp4 += 1 # progress the progress bar
            filename, wav = convert_mp4_to_wav(file_path, folders) 
            write_text(convert_wav_to_text(filename, wav), folders, filename)

        elif os.path.isdir(file_path):
            extracted_files = os.listdir(file_path)
            extract_path = file_path
            folders = os.path.join(folders, content)
            loop_through_directory(extracted_files, extract_path, folders, original_path)
            extract_path = original_path
            folders = ""

    txt_directory = os.path.join(txt_folder, folders)
    combine_text_files(txt_directory, "All")


def find_total_files(folder):
    mp4_count = 0
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isdir(item_path):
            mp4_count += find_total_files(item_path)
        elif item.endswith(".mp4"):
            mp4_count += 1

    return mp4_count

root_path = Text_GUI.root_path
zip_file = Text_GUI.zip_path
txt_folder = Text_GUI.txt_path

if Text_GUI.clicked:
    txt_folder = f"{root_path}\\{txt_folder}"

zip_file_path = f"{zip_file}"
extract_to_path = f"{root_path}\\MP4"
wav_path = f"{root_path}\\Wav" 

if txt_folder[-1] != "\\":
    txt_folder = f"{txt_folder}\\"
else:
    txt_folder = f"{txt_folder}"

split_output_folder = f"{root_path}\\Wav\\Split\\" 

if not os.path.exists(extract_to_path):
    os.makedirs(extract_to_path)

if not os.path.exists(wav_path):
    os.makedirs(wav_path)

if not os.path.exists(split_output_folder):
    os.makedirs(split_output_folder)

if not os.path.exists(txt_folder):
    os.makedirs(txt_folder)

with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(extract_to_path)

root = tk.Tk()
app = ProgressBarApp(root)
current_mp4 = 0
total_mp4s = find_total_files(extract_to_path) * 4 # times the steps
extracted_files = os.listdir(extract_to_path)
split_count = 0
loop_through_directory(extracted_files, extract_to_path, "", extract_to_path)