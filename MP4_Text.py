import moviepy.editor as mp
import speech_recognition as sr
import os
import zipfile
import soundfile as sf
from pydub import AudioSegment

import Text_GUI ## opens new GUI

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

def delete_files(directory_path, keep): # not currently used 

    print("delete attempt")

    try:
        
        if os.path.exists(directory_path):
            
            for filename in os.listdir(directory_path):
                
                if keep is not None:

                    keep = directory_path + "\\" + keep

                print("keep: ", keep)

                file_path = os.path.join(directory_path, filename)
                
                if file_path is not keep or keep is None:

                    if os.path.isfile(file_path):

                        os.remove(file_path)  # Delete the file

                    elif os.path.isdir(file_path):

                        print(f"Skipping directory: {file_path}")

            print("All files have been deleted.")

        else:

            print(f"The directory {directory_path} does not exist.")

    except Exception as e:

        print(f"{keep}: {e}")

# automatically creates Convert folder

root_path = Text_GUI.root_path

print("root: ", root_path)

zip_file = Text_GUI.zip_path

print("zip: ", zip_file)

txt_folder = Text_GUI.txt_path

if Text_GUI.clicked:

    txt_folder = f"{root_path}\\{txt_folder}"

zip_file_path = f"{zip_file}"

extract_to_path = f"{root_path}\\MP4-Text\\Converting\\MP4"

wav_path = f"{root_path}\\MP4-Text\\Converting\\Wav" # trying to delete

if txt_folder[-1] != "\\":

    txt_path = f"{txt_folder}\\"

else:

    txt_path = f"{txt_folder}"

print("txt folder: ", txt_path)

split_output_folder = f"{root_path}MP4-Text\\Converting\\Split" # trying to delete

def main():

    if not os.path.exists(extract_to_path):
        os.makedirs(extract_to_path)

    if not os.path.exists(wav_path):
        os.makedirs(wav_path)

    if not os.path.exists(txt_path):
        os.makedirs(txt_path)

    ## delete_files(extract_to_path, None)
    ## 
    ## delete_files(wav_path, None)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:

        zip_ref.extractall(extract_to_path)

    extracted_files = os.listdir(extract_to_path)

    recognizer = sr.Recognizer()

    # extract zip

    for content in extracted_files:

        # delete_files(wav_path, content)

        print("Extracting: ", content)

        file_path = os.path.join(extract_to_path, content)

        # convert single file to wav

        if content.endswith('.mp4'):

            filename = os.path.splitext(content)[0]

            video = mp.VideoFileClip(file_path)

            output_wav_path = os.path.join(wav_path, filename + ".wav")

            video.audio.write_audiofile(output_wav_path)

            print("Wav Created: ", output_wav_path)

            # os.remove(file_path) # remove mp4

            # converts same wav to text

            try:

                with sr.AudioFile(output_wav_path) as source:

                    audio = recognizer.record(source)

                    length = sf.SoundFile(output_wav_path)

                    seconds = length.frames / length.samplerate

                    split = False

                    if seconds > 350:

                        split = True

                        multi_wav = split_wav(output_wav_path, seconds, [], split_output_folder, filename)

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

                    # writes text

                    print(filename, " Text Created")

                    txt_file = open(txt_path + "\\" + filename + ".txt", "w")

                    txt_file.write(text)

                    txt_file.close()

            except:

                print("Error Converting ", output_wav_path, ": ", Exception)

if __name__ == '__main__':

    main()
