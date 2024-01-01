import openai
import urllib

API_KEY = "api key"

client = openai.OpenAI(api_key = API_KEY)
response = client.images.generate(
  model="dall-e-3",
  prompt="A futuristic city at night",
  size="1024x1024",
  quality="standard",
  n=1)

image_url = response.data[0].url
urllib.request.urlretrieve(image_url, "test.jpg")