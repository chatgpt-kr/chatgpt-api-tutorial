import openai
import urllib

API_KEY = "api key"

client = openai.OpenAI(api_key = API_KEY)
response = client.images.generate(
  model="dall-e-2",
  prompt="A futuristic city at night",
  size="512x512",
  quality="standard",
  n=1)

image_url = response.data[0].url
urllib.request.urlretrieve(image_url, "test.jpg")
