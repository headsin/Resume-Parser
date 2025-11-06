import base64, json

with open("credentials.json") as f:
    creds = f.read()

encoded = base64.b64encode(creds.encode()).decode()
print(encoded)
