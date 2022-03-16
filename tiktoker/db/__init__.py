from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from tiktoker.db.models import __beanie_models__
from tiktoker.db.models.usage_data import UsageData


CLIENT = None
TIKTOKERDB = None


async def init(host: str, username: str, password: str, port: int) -> None:
    ...
    global CLIENT, TIKTOKERDB
    CLIENT = AsyncIOMotorClient(
        host=host, port=port, username=username, password=password
    )
    TIKTOKERDB = CLIENT.tiktoker
    await init_beanie(database=TIKTOKERDB, document_models=__beanie_models__)
