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
        remaining_time = update_countdown(predicted_time_formatted) # update the predicted time remaining
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
        

def load_rates(json_file="rates.json"):
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
        return data["rates"]
    else:
        return []
    

'''
returns the average rate (rate = total bytes being processed / seconds it took the application to run) based on the last 10 runs
''' 
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
    os.remove(delete_path)
    

def delete_created_dir(delete_path):
    shutil.rmtree(delete_path)


'''
Creates an AI generated worksheet based off Gemini's response
'''
def write_AI_response(response, foldername):
    ai_response_folder = f"{root_path}\\AI Script\\" # creates a directory for the AI worksheet
    if not os.path.exists(ai_response_folder):
        os.makedirs(ai_response_folder) # if the directory doesn't exist, create one 
    
    ai_response_file = os.path.join(ai_response_folder, foldername + ".txt") # defines a variable for the AI generated workseet path
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
    for dirpath, dirnames, filenames in os.walk(directory): # iterates over the specified directory and its subdirectories.
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


def find_current_output_instance():
    files = os.listdir(output_folder)
    iteration = 1
    for file in files:
        if str(iteration) in file:
            iteration += 1

        else:
            break

    return iteration 

'''
Combines all the text files in a directory into one text file
'''
def combine_text_files(folder_path, output_file_name):
    output_file = os.path.join(folder_path, output_file_name + ".txt") # defines a varaible that contains the full path for the new text file
    if contains_text_files(folder_path): # checks if the directory contains text files 
        recorded = []
        with open(output_file, 'w') as outfile: # creates and opens the new text file to write in 
            number_of_files = 0
            for file in os.listdir(folder_path): # lists all the files in the directory 
                if file.endswith('.txt'): # checks if the file is a text file
                    number_of_files += 1

            file_iterations = -1
            while len(recorded) < number_of_files -1: # while the text files accounted for is less than the total
                file_iterations += 1
                if len(str(file_iterations)) < 1: # formats monograms to prepend a 0 to the front as a string 
                    file_iterations = "0" + file_iterations

                for filename in os.listdir(folder_path): # lists all the files from the folder path
                    if filename.endswith(".txt") and str(file_iterations) in filename: # file is a text file and is next in the iteration
                        recorded.append(filename) # adds the file to the array of recored files
                        file_path = os.path.join(folder_path, filename) # creates the entire file path so the os system can recognize it
                        with open(file_path, 'r') as infile: # reads the text file and writes it to the combine text file
                            outfile.write(f'Section: {filename}')
                            outfile.write("\n")
                            outfile.write("\n")
                            outfile.write(infile.read())
                            outfile.write("\n")  
                            outfile.write("\n")

        return output_file # returns the text file that contains all the text files
    
    else:
        return None # returns nothing if there are no text files in the directory


def write_text(text, folders, filename):
    filenames = filename.split('.')
    if filenames[0].isdigit():
        if int(filenames[0]) < 10:
            filename = f'0{filenames[0]}. {filenames[1]}'
        else:
            filename = f'{filenames[0]}. {filenames[1]}'

    textfile_path = text_path 
    for folder in folders:
        textfile_path = os.path.join(textfile_path, folder)

    os.makedirs(textfile_path, exist_ok=True)
    with open(os.path.join(textfile_path, filename + ".txt"), "w") as txt_file:
        txt_file.write(text)
    
    return textfile_path


'''
Converts an mp4 file to a wav file
'''
def convert_mp4_to_wav(file_path, folders):
    filename = os.path.splitext(os.path.basename(file_path))[0]
    video = mp.VideoFileClip(file_path) # loading a video to declare it as a variable 
    output_wav_path = audio_path
    for folder in folders:
        output_wav_path = os.path.join(output_wav_path, folder) 

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

    delete_created_files(output_wav_path) # deletes the wav file because it is no longer needed and wav files take up too much memory 
    return text

'''
splits the wav file into chucks in order to convert it to text
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
                except sr.UnknownValueError:
                    pass
                
    final_text = ''.join(chunk_text)
    return final_text



'''
Loops through a specific directory and process each mp4 file: convert to wav, convert to text, ect
'''
def loop_through_directory_original(extract_path, folders):
    files_to_progress = search_output_for_preprocessed_files(extract_path, output_folder) 
    folder_path = extract_path
    for content in files_to_progress['files']: # iterates through all the files which were extracted 
        folder_path = extract_path # renaming to folder_path for clarification
        # file_path = os.path.join(extract_path, content) # creates the full path so the os can recognize it
        file_path = content
        if os.path.isdir(file_path): # if file_path is a directory
            extracted_files = os.listdir(file_path) # list all the files in the newfound directory
            search_directory_path = file_path # renamed for clarification
            updated_folders = os.path.join(folders, content) # adds the found directory to the list of all folders
            loop_through_directory(search_directory_path, updated_folders) # searches all the files in the found directory recursivley
    
    create_threads_for_mp4_folder(folder_path, folders) # process all the files concurrently for efficency 
    txt_directory = os.path.join(text_path, folders) # creates specific text output directory for the specific directory
    combined_text_file = combine_text_files(txt_directory, "All") # combines all the text files in a directory into one file
    document_AI_response(combined_text_file)

def document_AI_response(combined_text_file):
    folders = None # FIX FOLDERS LATER!!!!!!!!!!!; don't really know if we need folders
    if combined_text_file != None and Select_Zip_File_GUI.checkbox_checked: # checks if the user checked the box for AI worksheet creation
        content = ''
        with open(combined_text_file, 'r') as file:
            content = file.read() + " /n" # reads the content from the combined text file

        with open('prompt.txt', 'r') as file:
            content += file.read() # reads in the prompt from prompt.txt to input into Gemini

        response = Create_Notes_From_AI.prompt_genai(content) # records the response from the Gemini prompt
        section_name = folders if folders else os.path.basename(zip_file_path) # records the section name for the worksheet title
        write_AI_response(response, section_name) # adds the complete worksheet to the AI output directory 


def loop_through_directory():
    files_to_procress_dict = search_output_for_preprocessed_files(video_path, output_folder) 
    folders = ''
    instance_to_copy_with_preprocessed_files = files_to_procress_dict['directory-name']
    instance_to_copy_with_preprocessed_files_txt_directory = os.path.join(output_folder, instance_to_copy_with_preprocessed_files, text_directory_name)
    copy_directory(instance_to_copy_with_preprocessed_files_txt_directory, text_path) # directory to copy, destination
    files_to_process = files_to_procress_dict['files']
    print('Files to process: ', files_to_process)
    create_threads_for_mp4_folder(files_to_process, video_path, folders) # ignoring folders for now


'''
Converts an mp4 file to a wav file, then converts the wav file to a text file
'''
def process_file(file, folder_path, folders): # ignoring folder_path for now 
    global current_step
    folders = file['directories']
    file = file['file_path']
    if mp4_directory_name in file: # the path is included if it comes from the preprocessed function 
        # is an mp4 from preprocessed function
        mp4_file_path = file 
        filename, wav_file_path = convert_mp4_to_wav(mp4_file_path, folders) 
        current_step += 1 # mp4 converted to wav 
        text = convert_wav_to_text(filename, wav_file_path) 
        current_step += 1 # wav converted to text
        write_text(text, folders, filename)
        current_step += 1 # progress the progress bar, text written 

    elif wav_directory_name in file:
        # is a wav from the preprocessed function
        wav_file_path = file 
        file_name = os.path.basename(wav_file_path)
        text = convert_wav_to_text(file_name, wav_file_path) 
        current_step += 1 # wav converted to text
        write_text(text, folders, filename)
        current_step += 1 # progress the progress bar, text written 

    else: # is not preprocessed
        file_path = os.path.join(folder_path, file) # defines the full path so the operating system can recognize it
        filename, wav_file_path = convert_mp4_to_wav(file_path, folders) 
        current_step += 1 # mp4 converted to wav 
        text = convert_wav_to_text(filename, wav_file_path) 
        current_step += 1 # wav converted to text
        write_text(text, folders, filename)
        current_step += 1 # progress the progress bar, text written 


'''Function creates a thread for each mp4 to be processed'''
def create_threads_for_mp4_folder_original(folder_path, folders): # creates a thread for each mp4 in a folder to be processed
    # ignore folders for now
    # thread pool: group of pre-instantiated, idle threads 
    mp4_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')] # gets all the mp4 files in a folder
    mp4_files = [mp4_files[i:i+5] for i in range(0, len(mp4_files), 5)] # make each array in the 2d array only contain 5 elements to avoid timeout

    for segment in mp4_files:
        def wrapper(mp4_file): # a wrapper is used to encapsulate other components
            return process_file(mp4_file, folder_path, folders) # returns the function with predetermined parameters

        with ThreadPoolExecutor() as executor: # ThreadPoolExecutor provides ways to manage multiple threads concurrently
            list(executor.map(wrapper, segment)) # creates a list of concurrent threads


def create_threads_for_mp4_folder(files_to_process, folder_path, folders): # creates a thread for each mp4 in a folder to be processed
    def wrapper(file): # a wrapper is used to encapsulate other components
        return process_file(file, folder_path, folders) # returns the function with predetermined parameters

    with ThreadPoolExecutor() as executor: # ThreadPoolExecutor provides ways to manage multiple threads concurrently
        list(executor.map(wrapper, files_to_process)) # creates a list of concurrent threads



'''
Returns the number of mp4 files are in a specific folder
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

'''
Converts seconds to Minute:Seconds format
'''
def format_seconds(seconds):
    minutes = seconds // 60  
    remaining_seconds = seconds % 60 
    return minutes, remaining_seconds


def search_output_for_preprocessed_files(video_path, output_folder):
    def compare_arrays(video_files_array, output_files_array):
        video_files_array_copy = video_files_array[:]
        output_files_array_copy = output_files_array[:]

        partially_processed_files = [] # for files that are partially processsed
        
        print('out: ', output_files_array_copy)

        output_files_array[:].sort(key=itemgetter('file_name'))
        output_directory_versions = [list(group) for _, group in groupby(output_files_array_copy, key=itemgetter('file_name'))]
        
        print('output_directory_versions: ', output_directory_versions)

        for extracted_zip_element in video_files_array[:]: 
            for output_file_versions in output_directory_versions:
                if output_file_versions[0]['file_name'] == extracted_zip_element['file_name']:
                    print('videos array copy: ', video_files_array_copy)
                    video_files_array_copy.remove(extracted_zip_element) # having trouble removing 

                    [partially_processed_files.append(item) for item in output_file_versions if text_directory_name in item["file_path"]] # check for txt
                    [partially_processed_files.append(item) for item in output_file_versions if wav_directory_name in item["file_path"]] # check for wav
                    [partially_processed_files.append(item) for item in output_file_versions if mp4_directory_name in item["file_path"]] # check for mp4

        '''
        # categories = [text_directory_name, wav_directory_name, mp4_directory_name]
        if True:
        # for category in categories:
            for extracted_zip_element in video_files_array[:]:  
                if 'file_name' in extracted_zip_element:
                    for output_element in output_files_array_copy:
                        # if the file is in both 
                        if ('file_name' in output_element and extracted_zip_element['file_name'] == output_element['file_name']):
                            if True:
                            # if (category in output_element['file_path']):
                                partially_processed_files.append(output_element)
                                video_files_array_copy.remove(extracted_zip_element)
                                # [item for item in video_files_array_copy if item["file_name"] != output_element['file_name']] # removes all versions of a file with the name

                            
                            if mp4_directory_name in output_element['file_path'] or wav_directory_name in output_element['file_path']:
                                partially_processed_files.append(output_element)
                                break
                            
                            
        '''                    
        return partially_processed_files + video_files_array_copy
    
    video_files = walk_through_directory(video_path, []) # the files we are searching for in the outputs
    
    progress_cache = {
        'directory-name': None,
        'length': float('inf'),
        'files': []
    }

    output_folder_instances = os.listdir(output_folder)
    for instance in output_folder_instances:
        file_name = instance
        path = os.path.join(output_folder, instance)
        files_in_instance_directory = walk_through_directory(path, []) # gets all the files for each output folder
        files_left_to_process = compare_arrays(video_files, files_in_instance_directory) # limits the files to process to only the ones that need totally processed or are partially processed
        print('files left: ', files_left_to_process)
        length = len(files_left_to_process) # number of files to process
        if length < progress_cache.get('length'):
            progress_cache['directory-name'] = file_name
            progress_cache['files'] = files_left_to_process
            progress_cache['length'] = length


    return progress_cache


def walk_through_directory(directory, directories): # directories
    # print('directory: ', directory, ' directories: ', directories)
    file_names = []
    process_files = True 
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            directory_path = os.path.join(root, dir)
            d = directories
            d.append(dir)
            directory_file_names = walk_through_directory(directory_path, d)
            file_names.extend(directory_file_names)
            process_files = False # to make sure that the same data doesn't get processed twice
        

        if process_files:
            for file in files:
                filename_segments = file.split('.')
                file_name = " ".join(map(str, filename_segments[:-1])) # everything in the name except the extension
                file_path = os.path.join(directory, file) # 

                if file_name != '':
                    file_elements = {
                        'file_name': file_name, 
                        'file_path': file_path,
                        'directories': []
                    }
                    file_names.append(file_elements) 

    print('filenames: ', file_names)
    return file_names


def copy_directory(output_instance, current_output_instance): # or directory to copy, destination
    shutil.copytree(output_instance, current_output_instance, dirs_exist_ok=True)


average_rate = calculate_average_rate() # takes average rate (rate = total processed bytes / seconds the application took) of last 10 runs
start_time = datetime.now() 

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

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref: # extracts the zip-file
    zip_ref.extractall(video_path)

average_rate = calculate_average_rate() # rate of seconds per byte
file_size = find_zip_memory(video_path) # get the size of the toal files being processsed (size in bytes)

predicted_time = file_size * average_rate if average_rate else None # the estimated time the program will take

current_step = 0 # !!!!!!!!!!!
predicted_time_formatted = format_seconds(predicted_time) # formats the predicted time from seconds to Minute:Seconds
total_steps = (find_total_files(video_path) * 3) + 1 # find the number of mp4 files, times the number of steps (3 steps per mp4), plus the final step (recording the time duration)
progress_bar_thread = threading.Thread(target=run_progress_bar) # thread which runs the progress bar
convert_thread = threading.Thread(target=loop_through_directory) # this thread converts mp4s
progress_bar_thread.start()
convert_thread.start()
convert_thread.join() # ends the convert thread
delete_created_dir(audio_path) # deletes the Wav directory once it is no longer needed
total_seconds = find_total_seconds(start_time) # get the total number of seconds the entire application run took 
store_rate(file_size, total_seconds) # stores the total seconds of the run in the rates.json file
current_step += 1 #  the final step of the application
progress_bar_thread.join() # ends the progress bar thread