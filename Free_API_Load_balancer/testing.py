# import google.generativeai as genai

# # Example using the newest Flash model
# model = genai.GenerativeModel('gemini-2.0-flash')
# response = model.generate_content("Hello world!")

from google import genai

client = genai.Client(api_key="AIzaSyBpiVg19MLrLL2cVtnhV8693fDBpKLzbtk")
# kssj
response = client.models.generate_content(
    model="models/gemini-flash-latest", 
    contents="Hello, how are you?"
)

print(response.text)
