# MP4 Transcriber

The objective of this program is to recieve a path to a zip file which should contain mp4 files (this will still work with folders).<br>
The program will produce a transcript of each mp4 file and a text file containing all the transcripts in the directory named 'All.txt.'<br>
Optionally, you can create an AI genereated worksheet based off of the represented material. <br>

## Table of Contents

- [Installation](#installation)
- [How_To_Run_The_Application](#How_To_Run_The_Application)
- [When_The_Application_Is_Finished](#When_The_Application_Is_Finished)

## Installation

1. Clone The Repository:
   
  a). Go to your indended directory in your Command Prompt (ex. cd Downloads/Transcript Code)<br>
  b). Paste this command: git clone https://github.com//OwenDiBacco/Transcript-Code.git

2. Make The Required Installations<br>

```bash
pip install -r requirements.txt
```

## How_To_Run_The_Application

1. Run the Convert_MP4_To_Transcript.py file<br>
2. Input the necessary zip-file path:<br>

   a). Select the 'Select Zip Path' button<br>
   b). Select the zip file which contains the mp4's you intend to convert<br>
   c). Optionally, you can select the checkbox that allows you to create an AI generated worksheet<br>
   

## When_The_Application_Is_Finished

All the file system integration will take place in the 'Output' folder. This is where your extracted mp4, text files and AI generated worksheets will be located.<br>

