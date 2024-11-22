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
from PIL import Image, ImageTk
from pydub import AudioSegment
from datetime import datetime, timedelta
from pydub.silence import split_on_silence
from concurrent.futures import ThreadPoolExecutor


class ProgressBarApp:  # Progress bar needs to be in this file, to make changes to the root window
    def __init__(self, root):
        self.root = root
        self.root.title("Progress Bar")

        # returns an array full of <PIL.ImageTk.PhotoImage object at 0x0000026545A67E50> objects
        self.super_mario_frames = self.load_gif_frames(
            'images\\super_mario_running.gif')
        # idea: could create an array full of mario running png frames which have no background

        self.image = Image.open('images\\super_mario_background.png')
        # find the default size of the background image
        background_image_width, background_image_height = self.image.size
        self.cropped_background_image = self.image.crop(
            # Crop the image by removing the top half
            (0, background_image_height // 2, background_image_width, background_image_height))

        self.cropped_background_image = self.cropped_background_image.resize(
            (600, 200), Image.LANCZOS)  # resize the image
        # defines the images as it's cropped version
        self.background_photo = ImageTk.PhotoImage(
            self.cropped_background_image)
        # the label which will display the background image
        self.background_label = tk.Label(root, image=self.background_photo)
        # places label in the top-left corner and makes it cover the entire screen
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.super_mario_x = 0  # the starting values for mario
        self.super_mario_y = 92  # places mario on top of the dirt

        self.current_frame_index = 0  # starting mario gif frame
        # creates label which will contain the mario image
        self.mario_label = tk.Label(root)
        self.mario_label.place(x=self.super_mario_x,
                               y=self.super_mario_y)  # starting position

        self.estimated_time = tk.Label(root, bg="#5C94FC", fg="white", font=(
            "Helvetica", 12, "bold"))  # changes the colors and fonts of the countdown
        self.estimated_time.pack()

    '''
    Opens the gif and defines a frames array full of all the gif frames
    '''

    def load_gif_frames(self, gif_path):
        # Creates an image object from opening the filepath
        image = Image.open(gif_path)
        frames = []

        try:
            while True:  # loop until it reaches the end of the file
                self.super_mario_width = 50  # defines the size of the mario image
                self.super_mario_height = 50
                resized_frame = image.copy().resize((self.super_mario_width, self.super_mario_height),
                                                    Image.LANCZOS)  # resizes the current frame
                # appends the current frame
                frames.append(ImageTk.PhotoImage(resized_frame))
                image.seek(len(frames))  # moves to the next frame in the gif

        except EOFError:  # reached the end of file
            pass

        return frames

    '''
    Updates Mario image's x position
    '''

    def update_progress(self, current_step, total_steps, window_width):
        if total_steps == 0:  # if there are no mp4s in the program
            return False

        # the window width that the image can entirely be displayed inside
        true_window_width = window_width - self.super_mario_width
        # divides the current step by the total step and multplies it by the window width
        progress_value = (current_step / total_steps) * true_window_width

        # all the steps are completed and mario is at the very edge of the window
        if current_step == total_steps and true_window_width <= self.super_mario_x:
            # update the x position of the mario image
            self.update_position(progress_value)
            # pause for 1 second to show how the progress bar is complete
            time.sleep(1)
            return False

        elif progress_value <= true_window_width:
            # update the x position of the mario image
            self.update_position(progress_value)
            return True

        elif self.super_mario_x < progress_value:
            # update the x position of the mario image
            self.update_position(progress_value)
            return True

        return False

    '''
    Updates the x-postion of the Mario image on the window
    '''

    def update_position(self, x_value):
        self.super_mario_x = x_value  # updates Mario's x coordinate
        # places the Mario image at the new location
        self.mario_label.place(x=self.super_mario_x, y=self.super_mario_y)
        self.root.update_idletasks()  # updates the window

    '''
    Displays the current frame in the GIF
    '''

    def display_mario(self):
        # selects the current frame from all the frames in the gif
        frame = self.super_mario_frames[self.current_frame_index]
        self.mario_label.configure(image=frame)  # displays the current frame
        # iterates the current frame index
        self.current_frame_index = (
            self.current_frame_index + 1) % len(self.super_mario_frames)
        # runs recursivley after 50 milliseconds
        self.root.after(50, self.display_mario)


'''
Function starts the progress bar window
'''


def run_progress_bar():
    global current_step, total_steps
    root = tk.Tk()  # create progress bar root
    window_width = 600  # define the window size
    window_height = 200
    root.geometry(f"{window_width}x{window_height}")  # create the window
    app = ProgressBarApp(root)  # create ProgressBarApp instance

    def progress_update():  # function updates the progress bar
        # update the predicted time remaining
        remaining_time = update_countdown(predicted_time_formatted)
        # display the predicted time remaining
        app.estimated_time.config(text=f'{remaining_time}')
        # displays the updated frame in the gif animation, doesn't affect position at all
        app.display_mario()
        # if the progress bar is still running
        progressing = app.update_progress(
            current_step, total_steps, window_width)
        if progressing:
            # run function recursively, after 100 milliseconds
            root.after(100, progress_update)

        else:
            root.destroy()  # close the window

    root.after(100, progress_update)  # starts the recursive update function
    root.mainloop()  # keeps window open


'''
Returns the the predicted time left in a formatted manner
'''


# takes predicted time left as a tuple (minute, seconds)
def update_countdown(predicted_time_duration):
    global start_time  # used the time the run started
    current_time = datetime.now()  # takes the current time for comparison
    minutes, seconds = predicted_time_duration
    # timedelta object formats the minutes and seconds to represent the remaining duration of time
    predicted_time_duration_timedelta = timedelta(
        minutes=minutes, seconds=seconds)
    # finds the time which has passed from the start of the run
    elapsed_time = current_time - start_time
    remaining_time = predicted_time_duration_timedelta - \
        elapsed_time  # the time which is left in the program
    if remaining_time.total_seconds() >= 0:
        # defines the individual minutes and seconds remaining
        remaining_minutes, remaining_seconds = divmod(
            int(remaining_time.total_seconds()), 60)
        # returns the minutes and seconds as strings
        remaining_time_str = f"{remaining_minutes:02}:{remaining_seconds:02}"

    else:
        # returns the overdue time as a non-negative number
        overdue_time = abs(remaining_time)
        # defines the individual minutes and seconds remaining
        overdue_minutes, overdue_seconds = divmod(
            int(overdue_time.total_seconds()), 60)
        # returns the minutes and seconds as strings
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
    print(f'Creating {delete_path}.txt')
    os.remove(delete_path)


def delete_created_dir(delete_path):
    print(f'Creating {delete_path}.txt')
    shutil.rmtree(delete_path)


'''
Creates an AI generated worksheet based off Gemini's response
'''


def write_AI_response(response, foldername):
    print(response)
    print(foldername)
    # creates a directory for the AI worksheet
    ai_response_folder = f"{root_path}\\AI Script\\"
    if not os.path.exists(ai_response_folder):
        # if the directory doesn't exist, create one
        os.makedirs(ai_response_folder)

    print(ai_response_file)
    # defines a variable for the AI generated workseet path
    ai_response_file = os.path.join(ai_response_folder, foldername + ".txt")
    if not os.path.exists(ai_response_folder):
        # if the directory doesn't exist, create one
        os.makedirs(ai_response_folder)

    f = open(ai_response_file, "w")  # creates and opens new txt file
    f.write(response)  # writes the AI response to the worksheet
    f.close()


'''
Finds the total memory of all the mp4s being processed
'''


def find_zip_memory(directory):
    total_size = 0
    # iterates over the specified directory and its subdirectories.
    for dirpath, dirnames, filenames in os.walk(directory):
        # loops through all the files (mp4s) in the directory
        for filename in filenames:
            # gets the total path script, so os can recognize it
            file_path = os.path.join(dirpath, filename)
            # gets the size of the specific file
            file_size = os.path.getsize(file_path)
            total_size += file_size  # size in bytes

    return total_size


def contains_text_files(directory_path):
    files = os.listdir(directory_path)
    for file in files:
        if file.lower().endswith('.txt'):
            return True

    return False


'''
Returns the number of output directories have been created. Used for numbering the current run
'''


def find_number_of_output_files():
    files = os.listdir(output_folder)  # list all the files in the directory
    number = 0
    for file in files:
        if output_dir_name in file:  # if the file has the name that all output directories have in common
            number += 1

    return number


'''
Combines all the text files in a directory into one text file
'''


def combine_text_files(folder_path, output_file_name):
    print(f'Combining {folder_path} files')
    # defines a varaible that contains the full path for the new text file
    output_file = os.path.join(folder_path, output_file_name + ".txt")
    # checks if the directory contains text files
    if contains_text_files(folder_path):
        recorded = []
        with open(output_file, 'w') as outfile:  # creates and opens the new text file to write in
            number_of_files = 0
            # lists all the files in the directory
            for file in os.listdir(folder_path):
                if file.endswith('.txt'):  # checks if the file is a text file
                    number_of_files += 1

            file_iterations = -1
            # while the text files accounted for is less than the total
            while len(recorded) < number_of_files - 1:
                file_iterations += 1
                # formats monograms to prepend a 0 to the front as a string
                if len(str(file_iterations)) < 1:
                    file_iterations = "0" + file_iterations

                # lists all the files from the folder path
                for filename in os.listdir(folder_path):
                    # file is a text file and is next in the iteration
                    if filename.endswith(".txt") and str(file_iterations) in filename:
                        # adds the file to the array of recored files
                        recorded.append(filename)
                        # creates the entire file path so the os system can recognize it
                        file_path = os.path.join(folder_path, filename)
                        # reads the text file and writes it to the combine text file
                        with open(file_path, 'r') as infile:
                            outfile.write(f'Section: {filename}')
                            outfile.write("\n")
                            outfile.write("\n")
                            outfile.write(infile.read())
                            outfile.write("\n")
                            outfile.write("\n")

        return output_file  # returns the text file that contains all the text files

    else:
        return None  # returns nothing if there are no text files in the directory


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


'''
Converts an mp4 file to a wav file
'''


def convert_mp4_to_wav(file_path, folders):
    print(f'Converting {file_path} to wav')
    filename = os.path.splitext(os.path.basename(file_path))[0]
    # loading a video to declare it as a variable
    video = mp.VideoFileClip(file_path)
    output_wav_path = os.path.join(audio_path, folders)
    os.makedirs(output_wav_path, exist_ok=True)  # creates output wav path
    output_wav_path = os.path.join(output_wav_path, filename + '.wav')
    # stores the wav file at the defined location
    video.audio.write_audiofile(output_wav_path)
    return filename, output_wav_path


'''
Converts a wav file to a text file
'''


def convert_wav_to_text(filename, output_wav_path):
    print(f'Converting {filename} to text')
    recognizer = sr.Recognizer()  # initialize a speech recognition engine
    text = ''
    try:
        # initializes an AudioFile instance for the specified audio file
        with sr.AudioFile(output_wav_path) as source:
            # gets the audio from the wav file
            audio = recognizer.record(source)
            # recognizes the text from the audio
            text = recognizer.recognize_google(audio)

    except:  # if the wav file is too long to be processed
        # splits the wav file into chucks to recognize it
        text = split_and_convert_wav(output_wav_path, filename)

    # deletes the wav file because it is no longer needed and wav files take up too much memory
    delete_created_files(output_wav_path)
    return text


'''
splits the wav file into chucks in order to convert it to text
'''


def split_and_convert_wav(wav_path, filename):
    # This is where the split files will be located
    split_audio_folder = f"{root_path}\\Wav\\Split\\"
    if not os.path.exists(split_audio_folder):
        # creates the split directory if it doesn't yet exist
        os.makedirs(split_audio_folder)

    chunk_text = []
    # defines the audio from the wav file
    audio = AudioSegment.from_wav(wav_path)
    # defines an array of segments of audio. The segments are split at silence points
    chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)
    recognizer = sr.Recognizer()
    # JK: changed split_path to split_audio_folder
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

    # JK: changed ''.join on ' '.join so chunks aren't mashed together.
    final_text = ' '.join(chunk_text)
    return final_text


'''
Loops through a specific directory and process each mp4 file: convert to wav, convert to text, ect
'''


def loop_through_directory(extracted_files, extract_path, folders):
    for content in extracted_files:  # iterates through all the files which were extracted
        folder_path = extract_path  # renaming to folder_path for clarification
        # creates the full path so the os can recognize it
        file_path = os.path.join(extract_path, content)
        if os.path.isdir(file_path):  # if file_path is a directory
            # list all the files in the newfound directory
            extracted_files = os.listdir(file_path)
            search_directory_path = file_path  # renamed for clarification
            # adds the found directory to the list of all folders
            updated_folders = os.path.join(folders, content)
            # searches all the files in the found directory recursivley
            loop_through_directory(
                extracted_files, search_directory_path, updated_folders)

    # process all the files concurrently for efficency
    create_threads_for_mp4_folder(folder_path, folders)
    # creates specific text output directory for the specific directory
    txt_directory = os.path.join(text_path, folders)
    # combines all the text files in a directory into one file
    combined_text_file = combine_text_files(txt_directory, "All")
    # checks if the user checked the box for AI worksheet creation
    if combined_text_file != None and Select_Zip_File_GUI.checkbox_checked:
        content = ''
        with open(combined_text_file, 'r') as file:
            content = file.read() + " /n"  # reads the content from the combined text file

        with open('prompt.txt', 'r') as file:
            content += file.read()  # reads in the prompt from prompt.txt to input into Gemini

        # records the response from the Gemini prompt
        response = Create_Notes_From_AI.prompt_genai(content)
        section_name = folders if folders else os.path.basename(
            zip_file_path)  # records the section name for the worksheet title
        # adds the complete worksheet to the AI output directory
        write_AI_response(response, section_name)


'''
Converts an mp4 file to a wav file, then converts the wav file to a text file
'''


def process_file(mp4_file, folder_path, folders):
    global current_step
    # defines the full path so the operating system can recognize it
    file_path = os.path.join(folder_path, mp4_file)
    filename, wav = convert_mp4_to_wav(file_path, folders)
    current_step += 1  # mp4 converted to wav
    text = convert_wav_to_text(filename, wav)
    current_step += 1  # wav converted to text
    write_text(text, folders, filename)
    current_step += 1  # progress the progress bar, text written


'''Function creates a thread for each mp4 to be processed'''


# creates a thread for each mp4 in a folder to be processed
def create_threads_for_mp4_folder(folder_path, folders):
    # thread pool: group of pre-instantiated, idle threads
    mp4_files = [f for f in os.listdir(folder_path) if f.endswith(
        '.mp4')]  # gets all the mp4 files in a folder

    def wrapper(mp4_file):  # a wrapper is used to encapsulate other components
        # returns the function with predetermined parameters
        return process_file(mp4_file, folder_path, folders)

    # ThreadPoolExecutor provides ways to manage multiple threads concurrently
    with ThreadPoolExecutor() as executor:
        # creates a list of concurrent threads
        results = list(executor.map(wrapper, mp4_files))


'''
Returns the number of mp4 files are in a specific folder
'''


def find_total_files(folder):
    mp4_count = 0
    # lists all the items (directory or file) in the folder
    for item in os.listdir(folder):
        # creates the item's full path so the os can recognize it
        item_path = os.path.join(folder, item)
        if os.path.isdir(item_path):  # checks if the item is a directory
            # searches for mp4s recursively
            mp4_count += find_total_files(item_path)

        elif item.endswith(".mp4"):  # if the item is an mp4
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
    def get_filenames(directory):
        filenames = set()
        for root, dirs, files in os.walk(directory):
            for file in files:
                filenames.add(file)
        return filenames

    video_files = get_filenames(video_path)
    output_files = get_filenames(output_folder)

    missing_files = [file for file in video_files if file not in output_files]

    full_output_paths = [os.path.join(root, file) for root, _, files in os.walk(
        output_folder) for file in files if file in output_files]

    return not missing_files, missing_files, full_output_paths


# takes average rate (rate = total processed bytes / seconds the application took) of last 10 runs
average_rate = calculate_average_rate()
start_time = datetime.now()

# gets the path to the zip files from the starting GUI file
zip_file_path = Select_Zip_File_GUI.zip_path
# the Output directory all the output results will be located
output_folder = f'.\\Output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)  # creates the output folder

output_dir_name = "Output Results"  # the name of all output results
# root_path: where all the file system integration will take place
root_path = f'{output_folder}\\{
    output_dir_name} - {find_number_of_output_files() + 1}.'

# where the mp4s from the zip-file will be extracted to
video_path = f"{root_path}\\MP4"
if not os.path.exists(video_path):
    os.makedirs(video_path)  # created the path the zip-file will extract to

# the directory where the mp4s that convert to wav will be located
audio_path = f"{root_path}\\Wav"
if not os.path.exists(audio_path):
    os.makedirs(audio_path)  # creates the wav directory

# the directory where the transcripts will be located
text_path = f"{root_path}\\Txt"
if not os.path.exists(text_path):
    os.makedirs(text_path)  # creates the transcript directory

with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:  # extracts the zip-file
    zip_ref.extractall(video_path)

average_rate = calculate_average_rate()  # rate of seconds per byte
# get the size of the toal files being processsed (size in bytes)
file_size = find_zip_memory(video_path)

# the estimated time the program will take
predicted_time = file_size * average_rate if average_rate else None

current_step = 0  # !!!!!!!!!!!
# formats the predicted time from seconds to Minute:Seconds
predicted_time_formatted = format_seconds(predicted_time)
# find the number of mp4 files, times the number of steps (3 steps per mp4), plus the final step (recording the time duration)
total_steps = (find_total_files(video_path) * 3) + 1
# lists all the files which were extracted
extracted_files = os.listdir(video_path)
print(search_output_for_preprocessed_files(video_path, output_folder))
# thread which runs the progress bar
progress_bar_thread = threading.Thread(target=run_progress_bar)
convert_thread = threading.Thread(target=loop_through_directory,  args=(
    extracted_files, video_path, ""))  # this thread converts mp4s
progress_bar_thread.start()
convert_thread.start()
convert_thread.join()  # ends the convert thread
# deletes the Wav directory once it is no longer needed
delete_created_dir(audio_path)
# get the total number of seconds the entire application run took
total_seconds = find_total_seconds(start_time)
# stores the total seconds of the run in the rates.json file
store_rate(file_size, total_seconds)
current_step += 1  # the final step of the application
progress_bar_thread.join()  # ends the progress bar thread
