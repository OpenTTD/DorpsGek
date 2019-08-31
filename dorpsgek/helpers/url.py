import aiohttp


async def shorten(url):
    data = aiohttp.FormData()
    data.add_field("url", url)

    async with aiohttp.ClientSession() as session:
        async with session.post("https://git.io", data=data) as resp:
            if resp.status == 201 and "Location" in resp.headers:
                return resp.headers["Location"]

    return url
