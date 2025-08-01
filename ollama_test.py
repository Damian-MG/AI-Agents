import ollama

client = ollama.Client()

model = "mario:latest"
prompt = "What is the weather like in Madrid?"

response = client.generate(model=model, prompt=prompt)

print("Response from Ollama:")
print(response.response)