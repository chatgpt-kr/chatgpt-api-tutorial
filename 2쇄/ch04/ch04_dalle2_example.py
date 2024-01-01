import openai
import urllib

API_KEY = "api key"

client = openai.OpenAI(api_key = API_KEY)
response = client.images.generate(
    prompt="A futuristic city at night",
    n=1,
    size="512x512"
    )

image_url = response.data[0].url
urllib.request.urlretrieve(image_url, "test.jpg")