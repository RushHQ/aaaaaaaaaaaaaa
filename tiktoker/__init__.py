import dis_snek as dis
from dotenv import get_key
import tiktoker.utils as utils


tiktoker = dis.Snake(
    intents=dis.Intents.MESSAGES | dis.Intents.DEFAULT,
    sync_interactions=True,
    delete_unused_application_cmds=False,  # this is a bit buggy on restarts
)


def run() -> None:

    for scale in utils.get_scales("./tiktoker/scales/"):
        tiktoker.grow_scale(scale)

    tiktoker.start(get_key(".env", "TOKEN"))
