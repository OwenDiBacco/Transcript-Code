# MP4 Zip-File Transcriber

The objective of this program is to recieve a path to a zip file which should contain mp4 files (this application supports sub-directories within the zip-file).<br>
The program will produce a transcripts for each mp4 file and a text file containing all the transcripts in the directory named 'All.txt.'<br>
Optionally, you can create an AI genereated worksheet based off of the represented material. <br>

## Table of Contents

- [Installation](#installation)
- [How-To-Run-The-Application](#How-To-Run-The-Application)
- [When-The-Application-Is-Finished](#When-The-Application-Is-Finished)
- [How-The-Application-Works](#How-The-Application-Works)

## Installation

1. Clone The Repository:
   
  a). Go to your indended directory in your Command Prompt (ex. cd Downloads/Transcript Code)<br>
  b). Paste this command: git clone https://github.com//OwenDiBacco/Transcript-Code.git

2. Make The Required Installations<br>

```bash
pip install -r requirements.txt
```

3. Get a Gemini API Key

   a). click on this link: https://aistudio.google.com/
   b). click on 'get api key' button, then the 'create api key' button
   c). select the Google Cloud Console project you would like this key associated with
   d). then 'create api key in existing project'
   e). copy this key becuase it is the only time you'll be able to access it
   d). create a file called '.env,' declare a function named 'API_KEY' and store your API key value in it. This creates an environemnt variable named 'API KEY'

## How-To-Run-The-Application

1. Run the Convert_MP4_To_Transcript.py file<br>
2. Input the necessary zip-file path:<br>

   a). Select the 'Select Zip Path' button which is the icon of a zip-file<br>
   b). Select the zip file which contains the mp4's you intend to convert<br>
   c). Optionally, you can select the checkbox that allows you to create an AI generated worksheet<br>
   

## When-The-Application-Is-Finished

All the file system integration will take place in the 'Output' folder. This is where your extracted mp4, text files and AI generated worksheets will be located.<br>

## How-The-Application-Works

1. The zip-file firstly, is extracted.
2. A function named process_extracted_content() walks through all the directories within the extracted zip file and processes each file within each. The function processes each directory sequentially so that the program can manage all the subdirectories.
3. The content within each directory gets passed into the function process_directory(). The first thing this function does is check if the other output instances have files that correspond with the current instance's files and have already been preprocessed. This is helpful for when a run fails or is ended prematurely; the user doesn't have to reprocess every file. The function creates an array of each file it needs to process. The text files are then immediatly copied into the current output directory's text file folder and each wav or mp4 file is passed into a function called create_threads_for_files_in_directory().
4. The create_threads_for_files_in_directory() function creates a thread for each file. The function only creates 5 threads at a time because of the possibility of an overprocessing error. Each file is passed into the process_file() function.
5. The process_file() function first checks the file's 'file_type' attribute. If the file is an mp4 file, the function converts it to a wav file. The wav file then is converted into text which is written to a text file.
6. When all the files are processed, a text file which contains all the text from each transcript is created. This text file is used for the AI prompt.
7. The document_AI_response() function creates a prompt by combining the combined text file with the prompt.txt file. This text file contains the prompt statement that will be prompted to the AI service. The function then records a response to the prompt by accessing the prompt_genai function from the Create_Notes_From_AI module.
8. The prompt_genai function prompts the Gemini AI engine with a Gemini API key as an evironment variable and returns the response.
9. This process is repeated until all the subdirectories have been fully processed. All the while, a progress bar runs in the background.
