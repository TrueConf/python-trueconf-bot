import logging

dispatcher = logging.getLogger("trueconf.dispatcher")
dispatcher.setLevel(logging.INFO)

chatbot = logging.getLogger("trueconf.client.chatbot")
chatbot.setLevel(logging.INFO)

if not chatbot.handlers:
    chatbot.addHandler(logging.StreamHandler())
    chatbot.handlers[0].setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )

if not dispatcher.handlers:
    dispatcher.addHandler(logging.StreamHandler())
    dispatcher.handlers[0].setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
