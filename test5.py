import asyncio
import logging

from trueconf import Bot, Dispatcher
from trueconf.exceptions import ApiErrorException

dp = Dispatcher()

BOT_SERVER = "10.110.2.240"
BOT_PASSWORD = "123tr"


async def run_bot(index: int):
    username = "tony_budz"  # лучше разные аккаунты

    while True:
        # bot = Bot.from_credentials(
        #     server=BOT_SERVER,
        #     username=username,
        #     password=BOT_PASSWORD,
        #     dispatcher=dp,
        #     verify_ssl=False,
        # )
        #
        # print(bot.token)
        # break

        bot = Bot(
            server=BOT_SERVER,
            dispatcher=dp,
            verify_ssl=False,
            token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0b255X2J1ZHoiLCJqdGkiOiI3MTRGRTk2QTExMzIxRTQxNjIyQkUwN0ZGMDdEQThBRSIsImV4cCI6MTc4MTIxNTkwNH0.SNA9HacN3zdnKL8UpsJRe64B7S4vJ0KSwlwEAje7ySzB10A-VApBE2ezOTl0r3Rk3H2AQwoep3K-Ljaa-jeii-U24JVsH8x_IZ1gXi-C84bJv_xRkRZmiHYlT0LJ32Io7iuJkEuFx3PixUdmK6uzkVD39nC6f32IRkmW6WYHgko68GV8rbv41cL1diErgerAGPUg2BOYPnTcmcjVGdFaWLORdvaYY1zqMos0uSJMw6u8oP-84Fit3Mn5SnvZZqzuFZ1_kcFebdM98iRsZcrMgA6trbmXa-JEuQTQyPDiX4s82m8ZeoFrmnSqI35DQ3G_TgyxqFLoFyXBHT9v1MmroQ"
        )

        try:
            logging.info(f"🚀 Starting bot #{index}: {username}")
            await bot.run()

        except ApiErrorException as e:
            if e.code == 203:
                logging.info(f"🔁 Bot #{index}: token expired, restarting...")
                await bot.shutdown()
                await asyncio.sleep(1)
                break

            logging.exception(f"💥 Bot #{index}: critical API error")
            raise

        except asyncio.CancelledError:
            logging.info(f"🛑 Bot #{index}: cancelled")
            await bot.shutdown()
            raise

        except Exception:
            logging.exception(f"💥 Bot #{index}: unexpected error")
            await bot.shutdown()
            await asyncio.sleep(3)
            continue


async def main():
    async with asyncio.TaskGroup() as tg:
        for i in range(128):
            tg.create_task(run_bot(i))

        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())