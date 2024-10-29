import os
import json
import time
import shutil
import zipfile
import threading
import Select_Zip_File_GUI
import Create_Notes_From_AI
import tkinter as tk
import moviepy.editor as mp
import speech_recognition as sr
from PIL import Image, ImageTk
from pydub import AudioSegment
from datetime import datetime, timedelta
from pydub.silence import split_on_silence
from concurrent.futures import ThreadPoolExecutor

class ProgressBarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Progress Bar")

        self.super_mario_frames = self.load_gif_frames('images\\super_mario_running.gif') # returns an array full of <PIL.ImageTk.PhotoImage object at 0x0000026545A67E50> objects 
        # idea: could create an array full of mario running png frames which have no background

        self.image = Image.open('images\\super_mario_background.png')   
        background_image_width, background_image_height = self.image.size
        self.cropped_background_image = self.image.crop((0, background_image_height // 2, background_image_width, background_image_height))  # Crop from halfway down to the bottom
    
        self.cropped_background_image = self.cropped_background_image.resize((600, 200), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.cropped_background_image)
        self.background_label = tk.Label(root, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.super_mario_x = 0
        self.super_mario_y = 92 # places mario on top of the dirt
        
        self.current_frame_index = 0 # starting mario gif frame
        self.mario_label = tk.Label(root)
        self.mario_label.place(x=self.super_mario_x, y=self.super_mario_y) # starting position
        
        self.estimated_time = tk.Label(root, bg="#5C94FC", fg="white", font=("Helvetica", 12, "bold"))
        self.estimated_time.pack()

    def load_gif_frames(self, gif_path):
        image = Image.open(gif_path)
        frames = []
        
        try:
            while True:
                self.super_mario_width = 50
                self.super_mario_height = 50
                resized_frame = image.copy().resize((self.super_mario_width, self.super_mario_height), Image.LANCZOS)
                frames.append(ImageTk.PhotoImage(resized_frame))
                image.seek(len(frames))

        except EOFError:
            pass  
        
        return frames

    def update_progress(self, current, total, window_width):
        if total == 0:
            return False  
        
        progress_value = (current / total) * (window_width - self.super_mario_width)
        if current >= total and progress_value >= window_width - self.super_mario_width and window_width <= self.super_mario_x + self.super_mario_width: 
            self.update_position(progress_value)
            time.sleep(1)
            return False 
        
        if progress_value <= window_width:
            self.update_position(progress_value)
            return True
        
        elif self.super_mario_x < progress_value:
            self.update_position(progress_value)
            return True
        
        return False 
    
    def update_position(self, progress_value):
        self.super_mario_x = progress_value
        self.mario_label.place(x=self.super_mario_x, y=self.super_mario_y)
        self.root.update_idletasks()
    
    def update_frame(self, ind):
        self.frame = tk.frames[ind]
        ind += 1
        if ind == tk.frame_count:
            ind = 0

        tk.label.configure(image=self.frame)
        self.root.after(50, tk.update_frame, ind)

    def display_mario(self):
        frame = self.super_mario_frames[self.current_frame_index]
        self.mario_label.configure(image=frame)
        self.current_frame_index = (self.current_frame_index + 1) % len(self.super_mario_frames)
        self.root.after(50, self.display_mario)

def run_progress_bar():
    global current_mp4, total_mp4s
    root = tk.Tk()
    window_width = 600
    window_height = 200
    root.geometry(f"{window_width}x{window_height}")
    app = ProgressBarApp(root)

    def progress_update():
        remaining_time = display_countdown(predicted_time_duration)
        app.estimated_time.config(text=f'{remaining_time}')
        app.display_mario() # displays the gif animation, doesn't affect position at all

        progressing = app.update_progress(current_mp4, total_mp4s, window_width)
        if progressing:
            root.after(100, progress_update)
             
        else:
            root.destroy()
 
    root.after(100, progress_update)
    root.mainloop()


def display_countdown(predicted_time_duration):
    global start_time
    current_time = datetime.now()
    minutes, seconds = predicted_time_duration
    predicted_time_duration_timedelta = timedelta(minutes=minutes, seconds=seconds)
    elapsed_time = current_time - start_time
    remaining_time = predicted_time_duration_timedelta - elapsed_time
    if remaining_time.total_seconds() >= 0:
        remaining_minutes, remaining_seconds = divmod(int(remaining_time.total_seconds()), 60)
        remaining_time_str = f"{remaining_minutes:02}:{remaining_seconds:02}"

    else:
        overdue_time = abs(remaining_time)
        overdue_minutes, overdue_seconds = divmod(int(overdue_time.total_seconds()), 60)
        remaining_time_str = f"-{overdue_minutes:02}:{overdue_seconds:02}"

    return remaining_time_str  


def store_rate(file_size, processing_time, json_file="rates.json"): 
    rate = processing_time / file_size
    rate_data = {
        "file_size_bytes": file_size,
        "processing_time_seconds": processing_time,
        "rate": rate
    }
    
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
    else:
        data = {"rates": []}

    data["rates"].append(rate_data)
    
    if len(data["rates"]) >= 10:
        data["rates"].pop(0)

    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)
        

def load_rates(json_file="rates.json"):
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
        return data["rates"]
    else:
        return []


def calculate_average_rate(json_file="rates.json"):
    rates = load_rates(json_file)
    if rates:
        total_rate = sum([entry["rate"] for entry in rates])
        return total_rate / len(rates)
    
    else:
        return None  


def find_total_seconds(start_time):
    return (datetime.now() - start_time).total_seconds()


def delete_created_files(delete_path):
    print(f'Creating {delete_path}.txt')
    os.remove(delete_path)
    

def delete_created_dir(delete_path):
    print(f'Creating {delete_path}.txt')
    shutil.rmtree(delete_path)


def write_AI_response(response, foldername):
    if not os.path.exists(ai_response_folder):
        os.makedirs(ai_response_folder)

    ai_response_file = os.path.join(ai_response_folder, foldername + ".txt")
    f = open(ai_response_file, "w")
    f.write(response)
    f.close()


def find_zip_memory(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):  # dirnames not used
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_size = os.path.getsize(file_path)
            total_size += file_size  # size in bytes
     
    return total_size


def contains_text_files(directory_path):
    files = os.listdir(directory_path)
    for file in files:
        if file.lower().endswith('.txt'):
            return True
        
    return False


def find_number_of_output_files():
    files = os.listdir(output_folder)
    number = 0
    for file in files:
        if output_dir_name in file:
            number += 1
    
    return number 


def combine_text_files(folder_path, output_file_name):
    print(f'Combining {folder_path} files')
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
                if len(str(file_iterations)) < 1:
                    file_iterations = "0" + file_iterations

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
    print(f'Creating {filename}.txt')
    filenames = filename.split('.')
    if filenames[0].isdigit():
        if int(filenames[0]) < 10:
            filename = f'0{filenames[0]}. {filenames[1]}'
        else:
            filename = f'{filenames[0]}. {filenames[1]}'

    file_path = os.path.join(text_path, folders)
    os.makedirs(file_path, exist_ok=True)
    with open(os.path.join(file_path, filename + ".txt"), "w") as txt_file:
        txt_file.write(text)
    
    return file_path


def convert_wav_to_text(filename, output_wav_path):
    print(f'Converting {filename} to text')
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
    print(f'Converting {file_path} to wav')
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
                except sr.UnknownValueError:
                    pass
                
    final_text = ''.join(chunk_text)
    return final_text


def loop_through_directory(extracted_files, extract_path, folders, original_path):
    for content in extracted_files:
        folder_path = extract_path
        file_path = os.path.join(extract_path, content)
        if os.path.isdir(file_path):
            extracted_files = os.listdir(file_path)
            extract_path = file_path
            folders = os.path.join(folders, content)
            loop_through_directory(extracted_files, extract_path, folders, original_path)
            extract_path = original_path
            folders = ""
    
    create_threads_for_mp4_folder(folder_path, folders)
    txt_directory = os.path.join(text_path, folders)
    combined_text_file = combine_text_files(txt_directory, "All")
    if combined_text_file != None and Select_Zip_File_GUI.checkbox_checked:
        content = ''
        with open(combined_text_file, 'r') as file:
            content = file.read() + " /n" 

        with open('prompt.txt', 'r') as file:
            content += file.read()

        response = Create_Notes_From_AI.prompt_genai(content)
        section_name = folders if folders else os.path.basename(zip_file_path)
        write_AI_response(response, section_name)


def process_file(mp4_file, folder_path, folders):
    global current_mp4
    file_path = os.path.join(folder_path, mp4_file)
    filename, wav = convert_mp4_to_wav(file_path, folders) 
    current_mp4 += 1 # mp4 converted to wav
    text = convert_wav_to_text(filename, wav)
    current_mp4 += 1 # wav converted to text
    write_text(text, folders, filename)
    current_mp4 += 1 # progress the progress bar, text written


def create_threads_for_mp4_folder(folder_path, folders): # creates a thread for each mp4 in a folder to be processed
    # thread pool: group of pre-instantiated, idle threads 
    mp4_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    def wrapper(mp4_file):
        return process_file(mp4_file, folder_path, folders)
    
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(wrapper, mp4_files))

    return results


def find_total_files(folder):
    mp4_count = 0
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isdir(item_path):
            mp4_count += find_total_files(item_path)

        elif item.endswith(".mp4"):
            mp4_count += 1

    return mp4_count


def convert_seconds(seconds):
    minutes = seconds // 60  
    remaining_seconds = seconds % 60 
    return minutes, remaining_seconds


average_rate = calculate_average_rate()
start_time = datetime.now()
output_dir_name = "Output Results"

zip_file_path = Select_Zip_File_GUI.zip_path
output_folder = f'.\\Output' 
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

root_path = f'{output_folder}\\{output_dir_name} - {find_number_of_output_files() + 1}.'
zip_file_path = f"{zip_file_path}"
video_path = f"{root_path}\\MP4"
if not os.path.exists(video_path):
    os.makedirs(video_path)

audio_path = f"{root_path}\\Wav" 
if not os.path.exists(audio_path):
    os.makedirs(audio_path)

text_path = f"{root_path}\\Txt" 
if not os.path.exists(text_path):
    os.makedirs(text_path)

split_audio_folder = f"{root_path}\\Wav\\Split\\" 
if not os.path.exists(split_audio_folder):
    os.makedirs(split_audio_folder)

ai_response_folder = f"{root_path}\\AI Script\\"
if not os.path.exists(ai_response_folder):
    os.makedirs(ai_response_folder)

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(video_path)

average_rate = calculate_average_rate() # rate of seconds per byte
file_size = find_zip_memory(video_path) # size in bytes
predicted_time = None
if average_rate:
    predicted_time = file_size * average_rate

current_mp4 = 0
predicted_time_duration = convert_seconds(predicted_time)
total_mp4s = (find_total_files(video_path) * 3) + 1 # number of steps, plus the final step 
extracted_files = os.listdir(video_path)
progress_thread = threading.Thread(target=run_progress_bar) 
converting_directory_thread = threading.Thread(target=loop_through_directory,  args=(extracted_files, video_path, "", video_path))
progress_thread.start()
converting_directory_thread.start()
converting_directory_thread.join()
delete_created_dir(audio_path) 
total_seconds = find_total_seconds(start_time) 
store_rate(file_size, total_seconds)
current_mp4 += 1
progress_thread.join()
# OSError: [WinError 6] The handle is invalid