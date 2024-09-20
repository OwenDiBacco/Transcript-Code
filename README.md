# MP4 Transcripter

The objective of this program is to recieve a path to a zip file which should contain mp4 files (this will still work with folders).
The program will output a zip file full of text files, containing the transcripts for each original mp4. 
Each folder inside the output zip file will contain a text file named 'All.txt'. The content of this text file contains all the combined text files in the folder.

## Table of Contents

- [Installation](#installation)
- [How_To_Run_The_Application](#How_To_Run_The_Application)
- [When_The_Application_Is_Finished](#When_The_Application_Is_Finished)

## Installation

1. Clone The Repository:
   
  a). Go to your indended directory in your Command Prompt (ex. cd Downloads/Transcript Code)
  b). Paste this command: git clone https://github.com//OwenDiBacco/Transcript-Code.git

2. Make The Required Installations

The first thing to download is FFmpeg, so we can use some it's libraries

1. Click this link: https://ffmpeg.org/download.html
2. Click 'Download Source Code'

All the required pip installations are located below: 

pip install moviepy
pip install SpeechRecognition
pip install os-sys
pip install zipfile36
pip install soundfile
pip install pydub
pip install requests
pip install msal

## How To Run The Application

1. Run the MP4-Text.py file
2. Input the necessary file paths:

   a). In the 'File Selector' GUI, click 'Open Root Path'
   b). Select the folder where you would like to have all the backend converting operations take place (ex. C:\Users\[User Name]\Downloads\MP4-Text)
   c). Next select the 'Select Zip Path' button
   d). Select the zip file which contains the mp4's you intend to convert
   e). If you would like to choose where the text files are output, select the 'Select Txt Folder' button. To use the defualt txt output path, select the 'Use Default Txt Output Folder' radio button.
   f). When finished, select 'Run Application'

## When The Application Is Finished

1. When this is completed, the completed zip file will appear in your downloads folder
2. Feel free to delete any of the added content to your root path, because they are no longer needed


