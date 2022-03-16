import asyncio
import dis_snek as dis
from tiktoker.db import init
from dotenv import get_key
import tiktoker.utils as utils


tiktoker = dis.Snake(
    intents=dis.Intents.MESSAGES | dis.Intents.DEFAULT,
    sync_interactions=True,
    delete_unused_application_cmds=False,  # this is a bit buggy on restarts
)


def run() -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(
        init(
            host=get_key(".env", "HOST"),
            username=get_key(".env", "USERNAME"),
            password=get_key(".env", "PASSWORD"),
            port=int(get_key(".env", "PORT")),
        )
    )

    for scale in utils.get_scales("./tiktoker/scales/"):
        tiktoker.grow_scale(scale)

    tiktoker.start(get_key(".env", "TOKEN"))
