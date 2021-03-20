# OldSandboxPosts Bot

A chatbot designed to search for week-old posts in the [Sandbox for Proposed Challenges](https://codegolf.meta.stackexchange.com/questions/2140/sandbox-for-proposed-challenges) on [Code Golf Stack Exchange](https://codegolf.stackexchange.com/) and post them into [The Nineteenth Byte](https://chat.stackexchange.com/rooms/240/the-nineteenth-byte)

To be run, the bot needs the following:

- Python 3.6 or later and it's standard modules
- The nonstandard modules [`stackapi`](https://pypi.org/project/StackAPI/), [`pycryptodomex`](https://pypi.org/project/pycryptodomex/) and [`websocket-client`](https://pypi.org/project/websocket-client/)
- An account on Code Golf Stack Exchange to operate from

To run it, simply run `main.py` and leave it going in the background. The first time it tries to log on, it will ask for the credentials to log in.

---

The bot runs once per day at 1am UTC time. It visits `https://codegolf.meta.stackexchange.com/search?q=inquestion%3A2140+lastactive%3A{}+score%3A0..+`, replacing `{}` with the date 7 days ago and takes the lists posts. It then filters out stubs and posts the rest to the chat room.
