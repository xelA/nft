import asyncio
import json
import aiohttp

from quart import Quart, render_template, request


app = Quart(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

with open("config.json", "r") as f:
    config = json.load(f)


@app.route("/")
async def index():
    ip_for_seed = request.headers.get("X-Forwarded-For") or request.remote_addr

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.alexflipnote.dev/nft?seed={ip_for_seed}") as response:
            data = await response.json()

    return await render_template("index.html", nft=data)


if __name__ == "__main__":
    app.run(
        port=config.get("port", 8080),
        debug=config.get("debug", False)
    )
