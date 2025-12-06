import asyncio

import httpx
from pprint import pprint
client = httpx.AsyncClient(base_url="http://0.0.0.0:8000")


async def req():
    response = await client.post("/api/transfer/", json={
        "from_wallet_id": 2,
        "to_wallet_id": 3,
        "amount": 2000,
    })
    pprint(response.json())


async def main():
    tasks = [req() for _ in range(70)]
    await asyncio.gather(*tasks)


asyncio.run(main())
