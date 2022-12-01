import asyncio
import json
import sass
import aiohttp
import random
import hashlib

from io import BytesIO
from quart import Quart, render_template, request, send_file

app = Quart(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


def load_json(filename: str) -> dict:
    with open(filename, "r", encoding="utf8") as f:
        data = json.load(f)
    return data


def string_to_sha256(text: str):
    salt = config.get("sha256_salt", "")

    result = hashlib.sha512(f"{salt}{text}".encode()).hexdigest()
    return result


config = load_json("./config.json")
testimonials = load_json("./data/testimonials.json")


@app.route("/")
async def index():
    ip_for_seed = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For") or request.remote_addr
    encrypted_ip = string_to_sha256(ip_for_seed)

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.alexflipnote.dev/nft?seed={encrypted_ip}") as response:
            data = await response.json()

    random.shuffle(testimonials)
    return await render_template(
        "index.html", nft=data,
        testimonials=testimonials,
        enumerate=enumerate
    )


async def fetch_and_read(filename: str, text_hex: str, text_colour: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.alexflipnote.dev/nft/{text_hex}/{text_colour}") as response:
            data = await response.read()

    return await send_file(
        BytesIO(data), mimetype="image/png",
        attachment_filename=filename,
        as_attachment=True
    )


@app.route("/download/<text_hex>/<text_colour>")
async def index_download(text_hex, text_colour):
    return await fetch_and_read("xela_nft.png", text_hex, text_colour)


@app.route("/steal/<text_hex>/<text_colour>")
async def index_stolen_download(text_hex, text_colour):
    return await fetch_and_read("stolen_xela_nft.png", text_hex, text_colour)


@app.errorhandler(Exception)
async def handle_exception(e):
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
    port=config.get("port", 8080),
    debug=config.get("debug", False)
)
