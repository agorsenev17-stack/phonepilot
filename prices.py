import asyncio
import aiohttp


URL = "https://search.wb.ru/exactmatch/ru/common/v9/search"


async def search_phone(session, query):
    params = {
        "ab_testing": "false",
        "appType": "1",
        "curr": "rub",
        "dest": "-1257786",
        "query": query,
        "resultset": "catalog",
        "sort": "popular",
        "spp": "30",
        "suppressSpellcheck": "false",
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    try:
        async with session.get(
            URL,
            params=params,
            headers=headers,
            timeout=20
        ) as response:

            print("Запрос:", query)
            print("HTTP:", response.status)

            if response.status != 200:
                return

            data = await response.json()

            products = data.get("data", {}).get("products", [])

            for product in products[:5]:
                name = product.get("name", "Без названия")
                price_data = product.get("sizes", [])

                if price_data:
                    price = (
                        price_data[0]
                        .get("price", {})
                        .get("product", 0)
                    )
                    price = price / 100
                else:
                    price = 0

                print(name, "-", price, "₽")

    except Exception as error:
        print("Ошибка:", error)


async def main():
    async with aiohttp.ClientSession() as session:

        phones = [
            "Apple iPhone 16 128GB",
            "Samsung Galaxy S25 128GB",
            "Xiaomi 15 256GB",
            "POCO X7 Pro 256GB",
        ]

        for phone in phones:
            await search_phone(session, phone)
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
