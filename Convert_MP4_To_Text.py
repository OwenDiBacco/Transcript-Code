import os
import re
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
from itertools import groupby
from operator import itemgetter
from PIL import Image, ImageTk
from pydub import AudioSegment
from collections import defaultdict
from datetime import datetime, timedelta
from pydub.silence import split_on_silence
from concurrent.futures import ThreadPoolExecutor


class ProgressBarApp: # Progress bar needs to be in this file, to make changes to the root window
    def __init__(self, root):
        self.root = root
        self.root.title("Progress Bar")

        self.super_mario_frames = self.load_gif_frames('images\\super_mario_running.gif') # returns an array full of <PIL.ImageTk.PhotoImage object at 0x0000026545A67E50> objects 
        # idea: could create an array full of mario running png frames which have no background

        self.image = Image.open('images\\super_mario_background.png')   
        background_image_width, background_image_height = self.image.size # find the default size of the background image
        self.cropped_background_image = self.image.crop((0, background_image_height // 2, background_image_width, background_image_height))  # Crop the image by removing the top half
    
        self.cropped_background_image = self.cropped_background_image.resize((600, 200), Image.LANCZOS) # resize the image 
        self.background_photo = ImageTk.PhotoImage(self.cropped_background_image) # defines the images as it's cropped version 
        self.background_label = tk.Label(root, image=self.background_photo) # the label which will display the background image
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1) # places label in the top-left corner and makes it cover the entire screen

        self.super_mario_x = 0 # the starting values for mario
        self.super_mario_y = 92 # places mario on top of the dirt
        
        self.current_frame_index = 0 # starting mario gif frame
        self.mario_label = tk.Label(root) # creates label which will contain the mario image
        self.mario_label.place(x=self.super_mario_x, y=self.super_mario_y) # starting position
        
        self.estimated_time = tk.Label(root, bg="#5C94FC", fg="white", font=("Helvetica", 12, "bold")) # changes the colors and fonts of the countdown
        self.estimated_time.pack()

    '''
    Opens the gif and defines a frames array full of all the gif frames
    '''
    def load_gif_frames(self, gif_path):
        image = Image.open(gif_path) # Creates an image object from opening the filepath
        frames = []
        
        try:
            while True: # loop until it reaches the end of the file
                self.super_mario_width = 50 # defines the size of the mario image
                self.super_mario_height = 50
                resized_frame = image.copy().resize((self.super_mario_width, self.super_mario_height), Image.LANCZOS) # resizes the current frame
                frames.append(ImageTk.PhotoImage(resized_frame)) # appends the current frame
                image.seek(len(frames)) # moves to the next frame in the gif 

        except EOFError: # reached the end of file 
            pass  
        
        return frames

    '''
    Updates Mario image's x position
    '''
    def update_progress(self, current_step, total_steps, window_width):
        if total_steps == 0: # if there are no mp4s in the program 
            return False  
            
        true_window_width = window_width - self.super_mario_width # the window width that the image can entirely be displayed inside
        progress_value = (current_step / total_steps) * true_window_width # divides the current step by the total step and multplies it by the window width 
        
        if current_step == total_steps and true_window_width <= self.super_mario_x: # all the steps are completed and mario is at the very edge of the window
            self.update_position(progress_value) # update the x position of the mario image
            time.sleep(1) # pause for 1 second to show how the progress bar is complete
            return False 
        
        elif progress_value <= true_window_width:
            self.update_position(progress_value) # update the x position of the mario image
            return True
        
        elif self.super_mario_x < progress_value:
            self.update_position(progress_value) # update the x position of the mario image
            return True
        
        return False 
    
    '''
    Updates the x-postion of the Mario image on the window
    '''
    def update_position(self, x_value): 
        self.super_mario_x = x_value # updates Mario's x coordinate
        self.mario_label.place(x=self.super_mario_x, y=self.super_mario_y) # places the Mario image at the new location
        self.root.update_idletasks() # updates the window

    '''
    Displays the current frame in the GIF
    '''
    def display_mario(self):
        frame = self.super_mario_frames[self.current_frame_index] # selects the current frame from all the frames in the gif
        self.mario_label.configure(image=frame) # displays the current frame
        self.current_frame_index = (self.current_frame_index + 1) % len(self.super_mario_frames) # iterates the current frame index
        self.root.after(50, self.display_mario) # runs recursivley after 50 milliseconds

'''
Function starts the progress bar window
'''
def run_progress_bar():
    global current_step, total_steps
    root = tk.Tk() # create progress bar root
    window_width = 600 # define the window size 
    window_height = 200
    root.geometry(f"{window_width}x{window_height}") # create the window 
    app = ProgressBarApp(root) # create ProgressBarApp instance

    def progress_update(): # function updates the progress bar
        if False: # the process of finding rates doesn't work well with the finding pre-processed files functionality
            # Not accessed
            remaining_time = update_countdown(predicted_time_formatted) # update the predicted time remaining
        
        else:
            remaining_time = ''

        app.estimated_time.config(text=f'{remaining_time}') # display the predicted time remaining
        app.display_mario() # displays the updated frame in the gif animation, doesn't affect position at all
        progressing = app.update_progress(current_step, total_steps, window_width) # if the progress bar is still running
        if progressing:
            root.after(100, progress_update) # run function recursively, after 100 milliseconds
             
        else:
            root.destroy() # close the window 
 
    root.after(100, progress_update) # starts the recursive update function
    root.mainloop() # keeps window open


'''
Returns the the predicted time left in a formatted manner
'''
def update_countdown(predicted_time_duration): # takes predicted time left as a tuple (minute, seconds)
    global start_time # used the time the run started 
    current_time = datetime.now() # takes the current time for comparison
    minutes, seconds = predicted_time_duration
    predicted_time_duration_timedelta = timedelta(minutes=minutes, seconds=seconds) # timedelta object formats the minutes and seconds to represent the remaining duration of time
    elapsed_time = current_time - start_time # finds the time which has passed from the start of the run
    remaining_time = predicted_time_duration_timedelta - elapsed_time # the time which is left in the program
    if remaining_time.total_seconds() >= 0:
        remaining_minutes, remaining_seconds = divmod(int(remaining_time.total_seconds()), 60) # defines the individual minutes and seconds remaining
        remaining_time_str = f"{remaining_minutes:02}:{remaining_seconds:02}" # returns the minutes and seconds as strings

    else:
        overdue_time = abs(remaining_time) # returns the overdue time as a non-negative number 
        overdue_minutes, overdue_seconds = divmod(int(overdue_time.total_seconds()), 60) # defines the individual minutes and seconds remaining
        remaining_time_str = f"-{overdue_minutes:02}:{overdue_seconds:02}" # returns the minutes and seconds as strings

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
        

'''
returns the average rate (rate = total bytes being processed / seconds it took the application to run) based on the last 10 runs
''' 
def calculate_average_rate(json_file="rates.json"): 
    def load_rates(json_file="rates.json"):
        with open(json_file, 'r') as file:
            data = json.load(file)
        return data["rates"]
    
    rates = load_rates(json_file)
    if rates:
        total_rate = sum([entry["rate"] for entry in rates])
        return total_rate / len(rates)
    
    else:
        return None  


def find_total_seconds(start_time):
    return (datetime.now() - start_time).total_seconds()


def delete_file(delete_path):
    os.remove(delete_path)
    

def delete_created_dir(delete_path):
    shutil.rmtree(delete_path)


'''
Creates an AI generated worksheet based off Gemini's response
'''
def write_AI_response(response, file_name, directories):
    ai_response_folder = os.path.join(root_path, get_directories(directories), ai_script_name)
    if not os.path.exists(ai_response_folder):
        os.makedirs(ai_response_folder) # if the directory doesn't exist, create one 
    
    ai_response_file = os.path.join(ai_response_folder, file_name + ".txt") # defines a variable for the AI generated workseet path
    if not os.path.exists(ai_response_folder):
        os.makedirs(ai_response_folder) # if the directory doesn't exist, create one 

    f = open(ai_response_file, "w") # creates and opens new txt file
    f.write(response) # writes the AI response to the worksheet
    f.close()


'''
Finds the total memory of all the mp4s being processed
'''
def find_zip_memory(directory):
    total_size = 0
    for dirpath, _, filenames in os.walk(directory): # iterates over the specified directory and its subdirectories.
        for filename in filenames: # loops through all the files (mp4s) in the directory
            file_path = os.path.join(dirpath, filename) # gets the total path script, so os can recognize it
            file_size = os.path.getsize(file_path) # gets the size of the specific file
            total_size += file_size  # size in bytes
     
    return total_size


def contains_text_files(directory_path):
    files = os.listdir(directory_path)
    for file in files:
        if file.lower().endswith('.txt'):
            return True
        
    return False


'''
Just for identification of instance, doesn't really matter if they are all sequential
'''
def find_current_output_instance():
    files = os.listdir(output_folder)
    return len(files) + 1

'''
Combines all the text files in a directory into one text file
'''
def combine_text_files(text_folder_path, output_file_name):
    def write_content_to_text_file(file_iterations, recorded):
        for filename in os.listdir(text_folder_path): # lists all the files from the folder path
            if filename.endswith(".txt") and str(file_iterations) in filename: # file is a text file and is next in the iteration
                recorded.append(filename) # adds the file to the array of recored files
                file_path = os.path.join(text_folder_path, filename) # creates the entire file path so the os system can recognize it
                with open(file_path, 'r') as infile: # reads the text file and writes it to the combine text file
                    outfile.write(f'Section: {filename}')
                    outfile.write("\n")
                    outfile.write("\n")
                    outfile.write(infile.read())
                    outfile.write("\n")  
                    outfile.write("\n")
        
        return recorded

    if os.path.exists(text_folder_path):
        if contains_text_files(text_folder_path): # checks if the directory contains text files 
            recorded = []
            number_of_files = find_number_of_text_files(text_folder_path)
            output_text_file = os.path.join(text_folder_path, output_file_name + ".txt") 
            with open(output_text_file, 'w') as outfile: # creates and opens the new text file to write in 
                file_iterations = -1
                while len(recorded) < number_of_files -1: # while the text files accounted for is less than the total
                    file_iterations += 1
                    if len(str(file_iterations)) < 10: # formats monograms to prepend a 0 to the front as a string 
                        str_file_iterations = "0" + str(file_iterations)
                        recorded = write_content_to_text_file(str_file_iterations, recorded)

            return output_text_file # returns the text file that contains all the text files
    
    else:
        return None # returns nothing if there are no text files in the directory


def write_text(text, folders, file_name):
    file_names = file_name.split('.')
    if file_names[0].isdigit(): # if the files are numbered
        file_name = f'0{file_names[0]}. {file_names[1]}' if int(file_names[0]) < 10 else f'{file_names[0]}. {file_names[1]}'

    text_file_path = os.path.join(text_path, get_directories(folders))
    os.makedirs(text_file_path, exist_ok=True)
    with open(os.path.join(text_file_path, file_name + ".txt"), "w") as txt_file:
        txt_file.write(text)
    
    return text_file_path


'''
Converts an mp4 file to a wav file
'''
def convert_mp4_to_wav(file_path, folders):
    filename = os.path.splitext(os.path.basename(file_path))[0]
    video = mp.VideoFileClip(file_path) # loading a video to declare it as a variable 
    output_wav_path = os.path.join(audio_path, get_directories(folders)) 
    os.makedirs(output_wav_path, exist_ok=True) # creates output wav path
    output_wav_path = os.path.join(output_wav_path, filename + '.wav')
    video.audio.write_audiofile(output_wav_path) # stores the wav file at the defined location
    return filename, output_wav_path


'''
Converts a wav file to a text file
'''
def convert_wav_to_text(filename, output_wav_path):
    recognizer = sr.Recognizer() # initialize a speech recognition engine 
    text = ''
    try:
        with sr.AudioFile(output_wav_path) as source: # initializes an AudioFile instance for the specified audio file
            audio = recognizer.record(source) # gets the audio from the wav file
            text = recognizer.recognize_google(audio) # recognizes the text from the audio

    except sr.exceptions.RequestError as e: # if the wav file is too long to be processed; bad request
        text = split_and_convert_wav(output_wav_path, filename) # splits the wav file into chucks to recognize it  

    delete_file(output_wav_path) # deletes the wav file because it is no longer needed and wav files take up too much memory 
    return text

'''
splits the wav file into chucks in order to convert it to text
takes a lot longer to process, so shouldn't be used unless it can't be processed the conventional way
'''
def split_and_convert_wav(wav_path, filename):
    split_audio_folder = f"{root_path}\\Wav\\Split\\" # This is where the split files will be located 
    if not os.path.exists(split_audio_folder):
        os.makedirs(split_audio_folder) # creates the split directory if it doesn't yet exist

    chunk_text = []
    audio = AudioSegment.from_wav(wav_path) # defines the audio from the wav file
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40) # defines an array of segments of audio. The segments are split at silence points
    recognizer = sr.Recognizer()
    split_path = os.path.join(split_audio_folder, filename)
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
                except sr.UnknownValueError: # audio not recognizable
                    pass
                
    final_text = ''.join(chunk_text)
    return final_text


def document_AI_response(combined_text_file, directories):
    if combined_text_file != None and Select_Zip_File_GUI.checkbox_checked: # checks if the user checked the box for AI worksheet creation and there is a combined text file
        content = read_file(combined_text_file)
        content += read_file('prompt.txt') # reads in the prompt from prompt.txt to input into Gemini
        response = Create_Notes_From_AI.prompt_genai(content) # records the response from the Gemini prompt
        ai_file_name = os.path.basename(os.path.normpath(directories)) if directories is not None else 'ai response file'
        section_name = ai_file_name + ' AI'
        write_AI_response(response, section_name, directories) # adds the complete worksheet to the AI output directory 


def read_file(file):
    with open(file, 'r') as file:
        return file.read()
        

'''
Processes all the files in the single directory
'''
def process_directory(directory_path, directories):
    def process_preprocessed_text_files(files_to_procress_dicts):
        text_file_dicts, files_to_procress_dicts = get_text_files(files_to_procress_dicts)
        text_files_paths = get_file_paths(text_file_dicts)        
        output_txt_directory = os.path.join(root_path, text_directory_name, get_directories(directories))
        copy_files_to_directory(text_files_paths, output_txt_directory)
        return files_to_procress_dicts

    files_to_procress_dict = search_output_for_preprocessed_files(directory_path, output_folder)['files'] # gets the files from the files_to_be_processed dictionary
    files_to_procress_dict = process_preprocessed_text_files(files_to_procress_dict)
    combined_text_file = create_threads_for_files_in_directory(files_to_procress_dict, directories) 
    document_AI_response(combined_text_file, directories)


def get_file_paths(file_dicts):
    return [d['file_path'] for d in file_dicts] if file_dicts else []


def get_directories(directories):
    if directories is not None:
        return directories

    return ''


def get_text_files(files):
    txt_files = []
    files_to_process = []
    for file in files:
        if file['file_type'] == 'txt':
            txt_files.append(file)
        else:
            files_to_process.append(file)

    return txt_files, files_to_process


'''
Searches each sub directory in each directory
'''
def process_extracted_content(directory_path, directories): 
    process_directory(directory_path, directories)
    for root, dirs, _ in os.walk(directory_path):
        for dir in dirs:
            sub_directory_path = os.path.join(root, dir)
            sub_directories = os.path.join(get_directories(directories), dir)
            process_extracted_content(sub_directory_path, sub_directories)


'''
Converts an mp4 file to a wav file, then converts the wav file to a text file
'''
def process_file(file, directories): # only mp4s and wavs are in this function    
    
    if file['file_type'] == 'mp4': # the path is included if it comes from the preprocessed function 
        mp4_file_path = file['file_path']
        file_name, wav_file_path = convert_mp4_to_wav(mp4_file_path, directories) 

    else: # is a wav file
        wav_file_path = file['file_path']
        
    file_name = os.path.basename(wav_file_path)
    text = convert_wav_to_text(file_name, wav_file_path) 
    write_text(text, directories, file_name)
    progress_step(1) # the file is completly processed


'''
Creates a thread for each file to process it
'''
def create_threads_for_files_in_directory(files_to_process, directories): # creates a thread for each mp4 in a folder to be processed
    def wrapper(file_to_process): # a wrapper is used to encapsulate other components
        return process_file(file_to_process, directories) # returns the function with predetermined parameters

    with ThreadPoolExecutor() as executor: # ThreadPoolExecutor provides ways to manage multiple threads concurrently
        list(executor.map(wrapper, files_to_process)) # creates a list of concurrent threads
    
    output_text_path = os.path.join(root_path, get_directories(directories), text_directory_name)
    combined_text_file_name = 'all' # the name of the file with the combined transcripts
    combined_file_path = combine_text_files(output_text_path, combined_text_file_name)
    return combined_file_path



'''
Returns the number of mp4 files are in a specific folder
Needs to remain as is because the files in each sub directory are not known until they are processed
'''
def find_total_files(folder):
    mp4_count = 0
    for item in os.listdir(folder): # lists all the items (directory or file) in the folder
        item_path = os.path.join(folder, item) # creates the item's full path so the os can recognize it
        if os.path.isdir(item_path): # checks if the item is a directory 
            mp4_count += find_total_files(item_path) # searches for mp4s recursively 

        elif item.endswith(".mp4"): # if the item is an mp4
            mp4_count += 1

    return mp4_count


def find_number_of_text_files(folder_path):
    number_of_files = 0
    for file in os.listdir(folder_path): # lists all the files in the directory 
        if file.endswith('.txt'): # checks if the file is a text file
            number_of_files += 1
    
    return number_of_files

def progress_step(increment):
    global current_step
    current_step += increment


'''
Converts seconds to Minute:Seconds format
'''
def format_seconds(seconds):
    minutes = seconds // 60  
    remaining_seconds = seconds % 60 
    return minutes, remaining_seconds


def search_output_for_preprocessed_files(video_path, output_folder):
    def compare_files(video_files_array, output_files_array):
        files_to_process = []  # List to store files to process
    
        for video_file in video_files_array:
            match_found = next((output_file for output_file in output_files_array 
                                if output_file['file_name'] == video_file['file_name']), None)
            
            files_to_process.append(match_found or video_file)

        return files_to_process


    def find_most_processed_version(files):
        def group_files_together(array_of_files):
            array_of_files.sort(key=itemgetter('file_name'))
            file_versions = [list(group) for _, group in groupby(array_of_files, key=itemgetter('file_name'))]
            return file_versions

        def get_most_processed_version(file):
            file_types = ['txt', 'wav', 'mp4']
            for file_type in file_types:
                for version in file:
                    if version['file_type'] == file_type:
                        return version
            return
                    
        grouped_file_versions = group_files_together(files)
        most_processed_versions_of_files = []

        for file_versions in grouped_file_versions:
            most_processed_versions_of_files.append(get_most_processed_version(file_versions))
                        
        return most_processed_versions_of_files


    files_to_be_processed = {
        'length': float('inf'),
        'files': []
    }

    video_files = find_all_files_in_directory(video_path) # find all the files in a single directory
    all_output_files = find_all_files(output_folder) # finds all the files from every directory
    most_processed_output_file_versions = find_most_processed_version(all_output_files)
    files_associated_to_extracted_files = compare_files(video_files, most_processed_output_file_versions) # limits the files to process to only the ones that need totally processed or are partially processed
    
    length = len(files_associated_to_extracted_files) # number of files to process
    if length < files_to_be_processed.get('length'):
        files_to_be_processed['files'] = files_associated_to_extracted_files
        files_to_be_processed['length'] = length


    return files_to_be_processed


def find_all_files_in_directory(directory_path):
    all_items = os.listdir(directory_path)
    file_dicts = []
    for item in all_items:
        if os.path.isfile(os.path.join(directory_path, item)):
            file_dict = create_file_dict(item, directory_path)
            file_dicts.append(file_dict)
    
    return file_dicts


def find_all_files(directory): 
    def get_all_files(directory):
        file_dicts = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_dict = create_file_dict(file, root)
                file_dicts.append(file_dict)

        return file_dicts
    
    file_dicts = get_all_files(directory)
    return file_dicts
    

def create_file_dict(file, directory):
    filename_segments = file.split('.')
    file_name = " ".join(map(str, filename_segments[:-1])) # everything in the name except the extension
    file_path = os.path.join(directory, file) 
    
    file_type = ''

    if mp4_directory_name in file_path:
        file_type = 'mp4'
    elif wav_directory_name in file_path:
        file_type = 'wav'
    elif text_directory_name in file_path:
        file_type = 'txt'
     
    file_elements = {
        'file_name': file_name, 
        'file_path': file_path,
        'file_type': file_type
    }

    return file_elements

'''
Takes the file to copy and the directory to copy to and copies all the files into the right directory
'''
def copy_files_to_directory(txt_files, current_output_instance_txt_directory): 
    # shutil.copytree(output_instance, current_output_instance, dirs_exist_ok=True) 
    # copies the entire directory 
    for file in txt_files:
        shutil.copy(file, current_output_instance_txt_directory)
        progress_step(1) # the file is completly processed


def find_predicted_run_time(file_size, average_rate):
    return file_size * average_rate if average_rate else None


# defines the file paths for the current run's output directory as global variables

# removed time predicted functionality because it is too complicated to calculate with the threading, and the addition of preprocessed files
start_time = datetime.now() # get the time the program started to compare against the time it ended

zip_file_path = Select_Zip_File_GUI.zip_path # gets the path to the zip files from the starting GUI file 
output_folder = f'.\\Output' # the Output directory all the output results will be located
if not os.path.exists(output_folder):
    os.makedirs(output_folder) # creates the output folder

output_dir_name = "Output Results" # the name of all output results
current_output_directory_name = find_current_output_instance()
root_path = f'{output_folder}\\{output_dir_name} - {current_output_directory_name}.' # root_path: where all the file system integration will take place

mp4_directory_name = 'MP4'
video_path = f"{root_path}\\{mp4_directory_name}" # where the mp4s from the zip-file will be extracted to 
if not os.path.exists(video_path):
    os.makedirs(video_path) # created the path the zip-file will extract to

wav_directory_name = 'Wav'
audio_path = f"{root_path}\\{wav_directory_name}" # the directory where the mp4s that convert to wav will be located
if not os.path.exists(audio_path):
    os.makedirs(audio_path) # creates the wav directory

text_directory_name = 'Txt'
text_path = f"{root_path}\\{text_directory_name}" # the directory where the transcripts will be located
if not os.path.exists(text_path):
    os.makedirs(text_path) # creates the transcript directory

ai_script_name = 'AI Script'

# extract the zip-file
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref: 
    zip_ref.extractall(video_path)

# used to calculate the predicted time, no longer used; too complicated
average_rate = calculate_average_rate() # takes average rate (rate = total processed bytes / seconds the application took) of last 10 runs
file_size = find_zip_memory(video_path) # get the size of the toal files being processsed (size in bytes)
predicted_time = find_predicted_run_time(file_size, average_rate) # the estimated time the program will take
predicted_time_formatted = format_seconds(predicted_time) if predicted_time is not None else None

# defines the step the program is on; used for the progress bar
current_step = 0
total_steps = (find_total_files(video_path) + 1) # find the number of mp4 files, plus the final step (recording the time duration)
progress_bar_thread = threading.Thread(target=run_progress_bar) # thread which runs the progress bar
convert_thread = threading.Thread(target=process_extracted_content, args=(video_path, None)) # this thread converts mp4s, start the process with the extracted zip
progress_bar_thread.start()
convert_thread.start()
convert_thread.join() # ends the convert thread
delete_created_dir(audio_path) # deletes the Wav directory once it is no longer needed
progress_step(1) # the final step of the program
progress_bar_thread.join() # ends the progress bar thread
total_seconds = find_total_seconds(start_time) # get the total number of seconds the entire application run took 
store_rate(file_size, total_seconds) # stores the total seconds of the run in the rates.json file