# utils/nsfw_check.py

import aiohttp
from config import DEEPAI_API_KEY

async def is_nsfw(file_path: str) -> bool:
    url = "https://api.deepai.org/api/nsfw-detector"
    headers = {"api-key": DEEPAI_API_KEY}

    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as f:
            data = {'image': f}
            async with session.post(url, data=data, headers=headers) as resp:
                try:
                    result = await resp.json()
                    nsfw_score = result['output']['nsfw_score']
                    return nsfw_score >= 0.8  # You can adjust threshold here
                except Exception:
                    return False
