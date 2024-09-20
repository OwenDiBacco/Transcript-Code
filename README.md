# MP4 Transcripter

The objective of this program is to recieve a path to a zip file which should contain mp4 files (this will still work with folders).<br>
The program will output a zip file full of text files, containing the transcripts for each original mp4. <br>
Each folder inside the output zip file will contain a text file named 'All.txt'. The content of this text file contains all the combined text files in the folder.<br>

## Table of Contents

- [Installation](#installation)
- [How_To_Run_The_Application](#How_To_Run_The_Application)
- [When_The_Application_Is_Finished](#When_The_Application_Is_Finished)

## Installation

1. Clone The Repository:
   
  a). Go to your indended directory in your Command Prompt (ex. cd Downloads/Transcript Code)<br>
  b). Paste this command: git clone https://github.com//OwenDiBacco/Transcript-Code.git

2. Make The Required Installations<br>

The first thing to download is FFmpeg, so we can use some it's libraries<br>

1. Click this link: https://ffmpeg.org/download.html<br>
2. Click 'Download Source Code'<br>

All the required pip installations are located below: <br>

pip install moviepy<br>
pip install SpeechRecognition<br>
pip install os-sys<br>
pip install zipfile36<br>
pip install soundfile<br>
pip install pydub<br>
pip install requests<br>
pip install msal<br>

## How To Run The Application

1. Run the MP4-Text.py file<br>
2. Input the necessary file paths:<br>

   a). In the 'File Selector' GUI, click 'Open Root Path'<br>
   b). Select the folder where you would like to have all the backend converting operations take place (ex. C:\Users\[User Name]\Downloads\MP4-Text)<br>
   c). Next select the 'Select Zip Path' button<br>
   d). Select the zip file which contains the mp4's you intend to convert<br>
   e). If you would like to choose where the text files are output, select the 'Select Txt Folder' button. To use the defualt txt output path, select the 'Use Default Txt Output Folder' radio button.<br>
   f). When finished, select 'Run Application'<br>

## When The Application Is Finished

1. When this is completed, the completed zip file will appear in your downloads folder<br>
2. Feel free to delete any of the added content to your root path, because they are no longer needed


