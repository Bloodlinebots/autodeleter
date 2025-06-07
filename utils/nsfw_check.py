# utils/nsfw_check.py

import aiohttp
from config import SIGHTENGINE_USER, SIGHTENGINE_SECRET

API_URL = "https://api.sightengine.com/1.0/check.json"

async def is_nsfw(image_path):
    data = {
        "models": "nudity",
        "api_user": SIGHTENGINE_USER,
        "api_secret": SIGHTENGINE_SECRET
    }

    async with aiohttp.ClientSession() as session:
        with open(image_path, "rb") as f:
            form_data = aiohttp.FormData()
            form_data.add_field("media", f, filename="image.jpg", content_type="image/jpeg")
            for key, value in data.items():
                form_data.add_field(key, value)

            async with session.post(API_URL, data=form_data) as response:
                result = await response.json()

                # 👇 Check for NSFW probability
                if result.get("nudity", {}).get("raw", 0) > 0.7:
                    return True
                return False
