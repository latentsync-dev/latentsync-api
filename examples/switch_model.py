"""The same client drives every hosted model listed in latentsync_api.MODELS."""
from latentsync_api import Client, MODELS

client = Client()
for slug, info in MODELS.items():
    print(slug, "->", info["category"], "required:", info["required"])
# pick one explicitly
output = client.run({"image_url": "https://example.com/input.png"}, model="heygen/avatar-4")
print(output)
