import os
from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
generation_config = {
                    "temperature": 0.9,
                    "top_p": 1,
                    "top_k": 1,
                    "max_output_tokens": 2048}

model = genai.GenerativeModel("gemini-2.5-pro",
                              generation_config=generation_config)

response = model.generate_content(["Hello World!"])
print(response.text)
