from google import genai

client = genai.Client(api_key="AIzaSyDvJNnhlp4aY5ke__uJWv8oXPXD9SF7ETA")

for m in client.models.list():
    print(m.name)
