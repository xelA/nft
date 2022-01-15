import asyncio
import json
import aiohttp
import hashlib

from quart import Quart, render_template, request


app = Quart(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

with open("config.json", "r") as f:
    config = json.load(f)


def string_to_sha256(text: str):
    salt = config.get("sha256_salt", "")

    result = hashlib.sha512(f"{salt}{text}".encode()).hexdigest()
    return result


@app.route("/")
async def index():
    ip_for_seed = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For") or request.remote_addr

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.alexflipnote.dev/nft?seed={ip_for_seed}") as response:
            data = await response.json()

    return await render_template("index.html", nft=data)


@app.route("/test_error")
async def test_error():
    return await render_template("error_handler.html")


@app.errorhandler(Exception)
async def handle_exception(e):
    return await render_template("error_handler.html")


if __name__ == "__main__":
    app.run(
        port=config.get("port", 8080),
        debug=config.get("debug", False)
    )
