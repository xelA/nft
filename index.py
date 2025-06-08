import asyncio
import json
import sass
import aiohttp
import random
import hashlib

from dotenvplus import DotEnv
from io import BytesIO
from quart import Quart, render_template, request, send_file

app = Quart(__name__)
config = DotEnv(".env")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

with open("./data/testimonials.json", encoding="utf8") as f:
    testimonials = json.load(f)


def string_to_sha512(text: str) -> str:
    """
    Convert a string to a SHA512 hash.

    Parameters
    ----------
    text:
        The string to hash.

    Returns
    -------
        The SHA512 hash of the string.
    """
    salt = config["CRYPTO_SALT"]
    return hashlib.sha512(f"{salt}{text}".encode()).hexdigest()


@app.route("/")
async def _index():
    ip_for_seed: str = (
        request.headers.get("CF-Connecting-IP") or
        request.headers.get("X-Forwarded-For") or
        request.remote_addr or
        "127.0.0.1"
    )

    encrypted_ip = string_to_sha512(ip_for_seed)

    async with aiohttp.ClientSession() as session, session.get(f"https://api.alexflipnote.dev/nft?seed={encrypted_ip}") as response:
        data = await response.json()

    random.shuffle(testimonials)

    return await render_template(
        "index.html", nft=data,
        testimonials=testimonials,
        enumerate=enumerate
    )


async def fetch_and_read(filename: str, text_hex: str, text_colour: str):
    """ Fetch a file from the API and return it. """
    async with aiohttp.ClientSession() as session, session.get(f"https://api.alexflipnote.dev/nft/{text_hex}/{text_colour}") as response:
        data = await response.read()

    return await send_file(
        BytesIO(data), mimetype="image/png",
        attachment_filename=filename,
        as_attachment=True
    )


@app.route("/download/<text_hex>/<text_colour>")
async def _index_download(text_hex, text_colour):
    return await fetch_and_read("xela_nft.png", text_hex, text_colour)


@app.route("/steal/<text_hex>/<text_colour>")
async def _index_stolen_download(text_hex, text_colour):
    return await fetch_and_read("stolen_xela_nft.png", text_hex, text_colour)


@app.errorhandler(Exception)
async def _handle_exception(e):
    return await render_template(
        "error_handler.html",
        error_code=e.code,
        error_message=e.description
    )


sass.compile(
    dirname=["./static/sass", "./static/css"],
    output_style="compressed"
)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run(
    port=config["HTTP_PORT"],
    debug=config["HTTP_DEBUG"]
)
