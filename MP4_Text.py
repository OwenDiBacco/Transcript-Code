import os
import uuid
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
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)

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
    global current_mp4, total_mp4s
    root = tk.Tk()
    app = ProgressBarApp(root)

    def progress_update():
        progressing = app.update_progress(current_mp4, total_mp4s)
        if progressing:
            root.after(100, progress_update)  
        else:
            root.destroy()

    root.after(100, progress_update)
    root.mainloop()


def delete_created_files(workspace, output_path):
    delete_script_path = os.path.join(workspace, 'Delete.py')
    with open(delete_script_path, "w") as wrfile:
        wrfile.write('import os\n')
        wrfile.write('import glob\n')
        wrfile.write('import shutil\n')
        wrfile.write(f'folder = r"{output_path}"\n')
        wrfile.write('files = glob.glob(os.path.join(folder, "*"))\n')
        wrfile.write('for f in files:\n')
        wrfile.write('    try:\n')
        wrfile.write('        if os.path.isfile(f):\n')
        wrfile.write('            os.remove(f)\n')
        wrfile.write('            print(f"Deleted file: {f}")\n')
        wrfile.write('        elif os.path.isdir(f):\n')
        wrfile.write('            shutil.rmtree(f)\n')
        wrfile.write('            print(f"Deleted directory: {f}")\n')
        wrfile.write('    except Exception as e:\n')
        wrfile.write('        print(f"Failed to delete {f}: {e}")\n')
        wrfile.write(f'os.remove(r"{delete_script_path}")\n')

    os.system(f'python3 "{delete_script_path}"')


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
    file_path = os.path.join(text_path, folders)
    os.makedirs(file_path, exist_ok=True)
    with open(os.path.join(file_path, filename + ".txt"), "w") as txt_file:
        txt_file.write(text)
    
    return file_path


def convert_wav_to_text(filename, output_wav_path):
    global current_mp4, split_audio_folder
    current_mp4 += 1 # progress the progress bar
    recognizer = sr.Recognizer()
    text = ''
    try:
        with sr.AudioFile(output_wav_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)

    except: # add the exception
        split_folder = os.path.join(split_audio_folder, filename)
        text = split_and_convert_wav(output_wav_path, split_folder, filename)

    return text


def convert_mp4_to_wav(file_path, folders):
    global current_mp4
    current_mp4 += 1 # progress the progress bar
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
                try:
                    text = recognizer.recognize_google(audio_chunk)
                    chunk_text.append(text)

                except: # don't know why this is here
                    print("An Error Occured in the Splitting Function")
                
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

zip_file_path = Text_GUI.zip_path
root_id = str(uuid.uuid4())
root_path = f'.\\{root_id}'
zip_file_path = f"{zip_file_path}"
video_path = f"{root_path}\\MP4"
audio_path = f"{root_path}\\Wav" 
text_path = f"{root_path}\\Txt" 
split_audio_folder = f"{root_path}\\Wav\\Split\\" 

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
total_mp4s = find_total_files(video_path) * 4 # times the steps
extracted_files = os.listdir(video_path)
progress_thread = threading.Thread(target=run_progress_bar)
converting_directory_thread = threading.Thread(target=loop_through_directory,  args=(extracted_files, video_path, "", video_path))
progress_thread.start()
converting_directory_thread.start()
progress_thread.join()
converting_directory_thread.join()
current_directory =  os.getcwd()
delete_created_files(current_directory, root_path)