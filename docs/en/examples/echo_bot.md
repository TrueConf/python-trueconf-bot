# Echo bot

```python
import asyncio
from trueconf import Bot, Dispatcher, Router, Message, F, ParseMode
from os import getenv

router = Router()
dp = Dispatcher()
dp.include_router(router)

TOKEN = getenv("TOKEN")

bot = Bot(server="video.example.com", token=TOKEN, dispatcher=dp)


@router.message(F.text)
async def echo(msg: Message):
    await msg.answer(f"You says: **{msg.text}**", parse_mode=ParseMode.MARKDOWN)


async def main():
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
```
