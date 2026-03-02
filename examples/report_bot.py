"""
Below is the initial scaffold for a bot that collects support reports.

- /report creates a router/state to capture and parse messages from a specific user.
- /cancel cancels the ticket and removes the user from this state.
- /send emails the collected messages — this is where you implement the logic to assemble the email (body + attachments) and send it.
You can use built-in modules, and third-party libraries if needed.
"""

import asyncio
import uuid
import trueconf
from trueconf import *
from trueconf.filters import Command

r1 = Router()
dp = Dispatcher()
dp.include_router(r1)

router_list_for_report = {}
list_message_for_report = {}

bot = trueconf.Bot.from_credentials(
    server="10.110.2.241",
    username="report_bot",
    password="123tr",
    dispatcher=dp,
    https=True,
    verify_ssl=False)

async def handle_report(msg: Message):
    if msg.from_user.id in router_list_for_report.keys():
        list_message_for_report[msg.from_user.id].append(msg)
        await msg.answer("The message has been added to the report.")


@r1.message(Command("report"))
async def on_report(msg: Message):
    number = uuid.uuid4() # генерация номера обращения с помощью uuid
    await msg.answer(f"Your ticket number is {number}. All subsequent messages will be added to this ticket.")
    r = Router(name=str(number))
    dp.include_router(r)
    r.message(F.from_user.id == msg.from_user.id)(handle_report)
    router_list_for_report.update({msg.from_user.id: r})
    list_message_for_report.update({msg.from_user.id: []})


@r1.message(Command("cancel"))
async def on_cancel(msg: Message):
    if msg.from_user.id in router_list_for_report.keys():
        for router in dp.routers:
            if router.name == router_list_for_report[msg.from_user.id].name:
                dp.routers.remove(router)
                router_list_for_report.pop(msg.from_user.id)
                list_message_for_report.pop(msg.from_user.id)
                await msg.answer("The report has been cancelled.")
                break
    else:
        await msg.answer("You don’t have an active report.")


def build_message_and_send_email(messages:list):
    """
    In Python, there are built-in libraries for working with email messages:
    https://docs.python.org/3/library/email.examples.html

    Here, you need to take the data from list_message_for_report[msg.from_user.id]
    and build an email-ready representation:

    for msg in message:
        match msg.content_type:
            case MessageType.TEXT:
                # You can put the text into the email body
            case MessageType.ATTACHMENT:
                # Download the files from TrueConf Server via:
                # msg.download(dest_path="path/to/file")

    Once the email is assembled correctly, send it using the smtplib module:
    https://docs.python.org/3/library/smtplib.html#smtp-example
    """

@r1.message(Command("send"))
async def send_report(msg: Message):
    if msg.from_user.id in router_list_for_report.keys():
        if build_message_and_send_email(list_message_for_report[msg.from_user.id]):
            await msg.answer("Your request has been successfully submitted to Technical Support.")
        else:
            await msg.answer("An error occurred. Please contact the bot developer.")
    else:
        await msg.answer("You don’t have an active report.")
        return

if __name__ == "__main__":
    asyncio.run(bot.run())
