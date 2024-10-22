import os
import uuid
import shutil
import zipfile
import threading
import Select_Zip_File_GUI
import Create_Notes_From_AI
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
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)
        self.current_task = tk.Label(root, text='Starting...')
        self.current_task.pack()

    def update_progress(self, current, total):
        if total == 0:
            return False  
        
        progress_value = (current / total) * 100
        self.progress['value'] = progress_value
        self.root.update_idletasks()
        if current >= total:
            return False 
        
        return True

def run_progress_bar():
    global current_mp4, total_mp4s, current_task
    root = tk.Tk()
    app = ProgressBarApp(root)
    app.current_task.config(text=current_task)

    def progress_update():
        progressing = app.update_progress(current_mp4, total_mp4s)
        if progressing:
            root.after(100, progress_update)  
        else:
            root.destroy()

    root.after(100, progress_update)
    root.mainloop()


def delete_created_files(delete_path):
    global current_task
    current_task = f'Creating {delete_path}.txt'
    os.remove(delete_path)
    

def delete_created_dir(delete_path):
    global current_task
    current_task = f'Creating {delete_path}.txt'
    shutil.rmtree(delete_path)


def write_AI_response(response, foldername):
    if not os.path.exists(ai_response_folder):
        os.makedirs(ai_response_folder)

    ai_response_file = os.path.join(ai_response_folder, foldername + ".txt")
    f = open(ai_response_file, "w")
    f.write(response)
    f.close()


def contains_text_files(directory_path):
    files = os.listdir(directory_path)
    for file in files:
        if file.lower().endswith('.txt'):
            return True
        
    return False
  

def combine_text_files(folder_path, output_file_name):
    global current_task
    current_task = f'Combining {folder_path} files'
    output_file = os.path.join(folder_path, output_file_name + ".txt")
    if contains_text_files(folder_path):    
        recorded = []
        with open(output_file, 'w') as outfile:
            number_of_files = 0
            for file in os.listdir(folder_path):
                if file.endswith('.txt'):
                    number_of_files += 1

            file_iterations = -1
            while len(recorded) < number_of_files -1:
                file_iterations += 1 
                for filename in os.listdir(folder_path):
                    if filename.endswith(".txt") and str(file_iterations) in filename:
                        recorded.append(filename)
                        file_path = os.path.join(folder_path, filename)
                        with open(file_path, 'r') as infile:
                            outfile.write(f'Section: {filename}')
                            outfile.write("\n")
                            outfile.write("\n")
                            outfile.write(infile.read())
                            outfile.write("\n")  
                            outfile.write("\n")

        return output_file
    else:
        return None

def write_text(text, folders, filename):
    global current_mp4, current_task
    current_task = f'Creating {filename}.txt'
    filenames = filename.split('.')
    if filenames[0].isdigit():
        if int(filenames[0]) < 10:
            filename = f'0{filenames[0]}. {filenames[1]}'
        else:
            filename = f'{filenames[0]}. {filenames[1]}'

    current_mp4 += 1 # progress the progress bar
    file_path = os.path.join(text_path, folders)
    os.makedirs(file_path, exist_ok=True)
    with open(os.path.join(file_path, filename + ".txt"), "w") as txt_file:
        txt_file.write(text)
    
    return file_path


def convert_wav_to_text(filename, output_wav_path):
    global current_mp4, split_audio_folder, current_task
    current_mp4 += 1 # progress the progress bar
    current_task = f'Converting {filename} to text'
    recognizer = sr.Recognizer()
    text = ''
    try:
        with sr.AudioFile(output_wav_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)

    except: # add the exception
        split_folder = os.path.join(split_audio_folder, filename)
        text = split_and_convert_wav(output_wav_path, split_folder, filename)

    delete_created_files(output_wav_path) 
    return text


def convert_mp4_to_wav(file_path, folders):
    global current_mp4, current_task
    current_mp4 += 1 # progress the progress bar
    current_task = f'Converting {file_path} to wav'
    filename = os.path.splitext(os.path.basename(file_path))[0]
    video = mp.VideoFileClip(file_path)
    output_wav_path = os.path.join(audio_path, folders)
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
                text = recognizer.recognize_google(audio_chunk)
                chunk_text.append(text)
                
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

    txt_directory = os.path.join(text_path, folders)
    combined_text_file = combine_text_files(txt_directory, "All")
    foldername = os.path.basename(os.path.dirname(txt_directory))
    if combined_text_file != None:
        content = ''
        with open(combined_text_file, 'r') as file:
            content = file.read()
            content += " /n" 

        with open('prompt.txt', 'r') as file:
            content += file.read()

        response = Create_Notes_From_AI.prompt_genai(content)
        print(response)
        write_AI_response(response, foldername)

def find_total_files(folder):
    mp4_count = 0
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isdir(item_path):
            mp4_count += find_total_files(item_path)
        elif item.endswith(".mp4"):
            mp4_count += 1

    return mp4_count

zip_file_path = Select_Zip_File_GUI.zip_path
root_id = "Output " + str(uuid.uuid4())
root_path = f'.\\{root_id}'
zip_file_path = f"{zip_file_path}"
video_path = f"{root_path}\\MP4"
audio_path = f"{root_path}\\Wav" 
text_path = f"{root_path}\\Txt" 
split_audio_folder = f"{root_path}\\Wav\\Split\\" 
ai_response_folder = f"{root_path}\\AI Script\\"

if not os.path.exists(video_path):
    os.makedirs(video_path)

if not os.path.exists(audio_path):
    os.makedirs(audio_path)

if not os.path.exists(split_audio_folder):
    os.makedirs(split_audio_folder)

if not os.path.exists(text_path):
    os.makedirs(text_path)

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(video_path)


current_mp4 = 0
current_task = ''
total_mp4s = find_total_files(video_path) * 4 # times the steps
extracted_files = os.listdir(video_path)
progress_thread = threading.Thread(target=run_progress_bar)
converting_directory_thread = threading.Thread(target=loop_through_directory,  args=(extracted_files, video_path, "", video_path))
progress_thread.start()
converting_directory_thread.start()
progress_thread.join()
converting_directory_thread.join()
delete_created_dir(audio_path) 
# OSError: [WinError 6] The handle is invalid