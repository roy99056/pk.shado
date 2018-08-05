import requests
import io


def get_image_data(url):
    data = requests.get(url)
    content = io.BytesIO(data.content)
    filename = url.rsplit("/", 1)[-1]
    return {"content": content, "filename": filename}