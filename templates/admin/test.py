import os
import google.generativeai as genai

genai.configure(api_key='AIzaSyD9HEichmFttNL-g1uugxcTDulq1X-NcO4')

model = genai.GenerativeModel('gemini-pro')

prompt = "Write a story about a magic backpack."
response = model.generate_content(prompt)

print(response.text) 