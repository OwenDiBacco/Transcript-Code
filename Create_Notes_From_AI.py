# OpenAI requires monthly billing
# Gemmini "free tier" is offered through the API service with lower rate limits for testing purposes
# Project ID: "gemini-prompter-439417"
# Gemini API Key: 'AIzaSyC7w6TBQQIE4xLDcsrOgnviJ4hHE-eLTdw'

# PS C:\Users\CMP_OwDiBacco> setx OPENAI_API_KEY "API-Key" 

# openai.api_key = "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" 
# Owen's Key ^ 
# Can only see key after you create it

import os
import google.generativeai as genai
from dotenv import load_dotenv

def prompt_genai(prompt):
    text = ''
    load_dotenv() # Load variables from .env
    api_key = os.getenv("API_KEY")  # Access the API key
    genai.configure(api_key=api_key) # Replace with your own Gemini API Key
    model = genai.GenerativeModel("gemini-1.5-flash")
    responses = model.generate_content([prompt])
    for response in responses:
        text += ' ' + response.text
    
    return text