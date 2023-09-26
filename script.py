import requests, zipfile, io

r = requests.get(
    'https://transparenciachc.blob.core.windows.net/lic-da/2023-1.zip')
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(".")

print(r.status_code)
