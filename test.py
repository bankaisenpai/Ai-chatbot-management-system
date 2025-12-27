from google import genai

client = genai.Client(api_key="AIzaSyDvJNnhlp4aY5ke__uJWv8oXPXD9SF7ETA")

response = client.models.generate_content(
    model="models/gemini-2.5-flash",
    contents=["Hello Gemini! How are you?"]
)

print(response.text)
