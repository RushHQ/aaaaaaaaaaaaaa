import dis_snek as dis
from dotenv import get_key
import tiktoker.utils as utils
from pyppeteer import launch
from tiktoker.db import init

tiktoker = dis.Snake(
    intents=dis.Intents.MESSAGES | dis.Intents.DEFAULT,
    sync_interactions=True,
    delete_unused_application_cmds=False,  # this is a bit buggy on restarts
)

BROWSER = None


async def run() -> None:
    global BROWSER
    BROWSER = await launch(headless=True)

    await init(
        host=get_key(".env", "HOST"),
        username=get_key(".env", "USERNAME"),
        password=get_key(".env", "PASSWORD"),
        port=int(get_key(".env", "PORT")),
    )
    for scale in utils.get_scales("./tiktoker/scales/"):
        tiktoker.grow_scale(scale)

    await tiktoker.login(get_key(".env", "TOKEN"))
    await tiktoker.start_gateway()
