import asyncio
from trueconf import Bot, Dispatcher, Router, Message, F, ParseMode
from trueconf.exceptions import ApiErrorException

router = Router()
dp = Dispatcher()
dp.include_router(router)

@router.message(F.text)
async def echo(msg: Message):
    await msg.answer(f"You says: **{msg.text}**", parse_mode=ParseMode.MARKDOWN)

MAX_RETRIES = 5

async def main(attempt: int = 1):
    bot = Bot.from_credentials(
        server="video.example.com",
        username="john_doe",
        password="very_secret",
        web_port=443,
        verify_ssl=False
    )
    try:
        await bot.run()
    except ApiErrorException as e:
        if e.code == 203 and attempt < MAX_RETRIES:
            await bot.shutdown()
            print("🔁 Token expired. Retrying in 0.5 seconds...")
            await asyncio.sleep(0.5)
            await main(attempt + 1)


if __name__ == "__main__":
    asyncio.run(main())