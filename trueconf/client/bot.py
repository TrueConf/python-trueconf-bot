import aiofiles
import asyncio
import contextlib
import httpx
import json
import signal
import ssl
import tempfile
import websockets
from pathlib import Path
from aiohttp import ClientSession, ClientTimeout, TCPConnector, FormData
from async_property import async_cached_property
from typing import (
    Callable,
    Awaitable,
    Dict,
    List,
    Tuple,
    TypeVar,
    Self,
    TypedDict,
    Unpack
)

from trueconf import loggers
from trueconf.client.session import WebSocketSession
from trueconf.dispatcher.dispatcher import Dispatcher
from trueconf.enums.file_ready_state import FileReadyState
from trueconf.enums.parse_mode import ParseMode
from trueconf.enums.survey_type import SurveyType
from trueconf.enums.chat_participant_role import ChatParticipantRole
from trueconf.exceptions import ApiErrorException
from trueconf.methods.add_participant_to_chat import AddChatParticipant
from trueconf.methods.auth import AuthMethod
from trueconf.methods.base import TrueConfMethod
from trueconf.methods.change_participant_role import ChangeParticipantRole
from trueconf.methods.create_channel import CreateChannel
from trueconf.methods.create_favorites_chat import CreateFavoritesChat
from trueconf.methods.create_group_chat import CreateGroupChat
from trueconf.methods.create_p2p_chat import CreateP2PChat
from trueconf.methods.edit_message import EditMessage
from trueconf.methods.edit_survey import EditSurvey
from trueconf.methods.forward_message import ForwardMessage
from trueconf.methods.get_chat_by_id import GetChatByID
from trueconf.methods.get_chat_history import GetChatHistory
from trueconf.methods.get_chat_participants import GetChatParticipants
from trueconf.methods.get_chats import GetChats
from trueconf.methods.get_file_info import GetFileInfo
from trueconf.methods.get_message_by_id import GetMessageById
from trueconf.methods.get_user_display_name import GetUserDisplayName
from trueconf.methods.has_chat_participant import HasChatParticipant
from trueconf.methods.remove_chat import RemoveChat
from trueconf.methods.remove_message import RemoveMessage
from trueconf.methods.remove_participant_from_chat import RemoveChatParticipant
from trueconf.methods.send_file import SendFile
from trueconf.methods.send_message import SendMessage
from trueconf.methods.send_survey import SendSurvey
from trueconf.methods.subscribe_file_progress import SubscribeFileProgress
from trueconf.methods.unsubscribe_file_progress import UnsubscribeFileProgress
from trueconf.methods.upload_file import UploadFile
from trueconf.types.input_file import InputFile, URLInputFile
from trueconf.types.parser import parse_update
from trueconf.types.requests.uploading_progress import UploadingProgress
from trueconf.types.responses.add_chat_participant_response import AddChatParticipantResponse
from trueconf.types.responses.change_participant_role_response import ChangeParticipantRoleResponse
from trueconf.types.responses.create_channel_response import CreateChannelResponse
from trueconf.types.responses.create_favorites_chat_response import CreateFavoritesChatResponse
from trueconf.types.responses.create_group_chat_response import CreateGroupChatResponse
from trueconf.types.responses.create_p2p_chat_response import CreateP2PChatResponse
from trueconf.types.responses.edit_message_response import EditMessageResponse
from trueconf.types.responses.edit_survey_response import EditSurveyResponse
from trueconf.types.responses.forward_message_response import ForwardMessageResponse
from trueconf.types.responses.get_chat_by_id_response import GetChatByIdResponse
from trueconf.types.responses.get_chat_history_response import GetChatHistoryResponse
from trueconf.types.responses.get_chat_participants_response import GetChatParticipantsResponse
from trueconf.types.responses.get_chats_response import GetChatsResponse
from trueconf.types.responses.get_file_info_response import GetFileInfoResponse
from trueconf.types.responses.get_message_by_id_response import GetMessageByIdResponse
from trueconf.types.responses.get_user_display_name_response import GetUserDisplayNameResponse
from trueconf.types.responses.has_chat_participant_response import HasChatParticipantResponse
from trueconf.types.responses.remove_chat_participant_response import RemoveChatParticipantResponse
from trueconf.types.responses.remove_chat_response import RemoveChatResponse
from trueconf.types.responses.remove_message_response import RemoveMessageResponse
from trueconf.types.responses.send_file_response import SendFileResponse
from trueconf.types.responses.send_message_response import SendMessageResponse
from trueconf.types.responses.send_survey_response import SendSurveyResponse
from trueconf.types.responses.subscribe_file_progress_response import SubscribeFileProgressResponse
from trueconf.types.responses.unsubscribe_file_progress_response import UnsubscribeFileProgressResponse
from trueconf.utils import generate_secret_for_survey
from trueconf.utils import get_auth_token
from trueconf.utils import validate_token

T = TypeVar("T")

class TokenOpts(TypedDict, total=False):
    web_port: int
    https: bool


class Bot:
    def __init__(
            self,
            server: str,
            token: str,
            web_port: int = 443,
            https: bool = True,
            debug: bool = False,
            verify_ssl: bool = True,
            dispatcher: Dispatcher | None = None,
            receive_unread_messages: bool = False,
    ):
        """
        Initializes a TrueConf chatbot instance with WebSocket connection and configuration options.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/connect-and-auth/#auth

        Args:
            server (str): Address of the TrueConf server.
            token (str): Bot authorization token.
            web_port (int, optional): WebSocket connection port. Defaults to 443.
            https (bool, optional): Whether to use HTTPS protocol. Defaults to True.
            debug (bool, optional): Enables debug mode. Defaults to False.
            verify_ssl (bool, optional): Whether to verify the server's SSL certificate. Defaults to True.
            dispatcher (Dispatcher | None, optional): Dispatcher instance for registering handlers.
            receive_unread_messages (bool, optional): Whether to receive unread messages on connection. Defaults to False.

        Note:
            Alternatively, you can authorize using a username and password via the `from_credentials()` class method.
        """

        validate_token(token)

        self.server = server
        self.__token = token
        self.web_port = web_port
        self.https = https
        self.debug = debug
        self.connected_event = asyncio.Event()
        self.authorized_event = asyncio.Event()
        self._session: WebSocketSession | None = None
        self._connect_task: asyncio.Task | None = None
        self.stopped_event = asyncio.Event()
        self.dp = dispatcher or Dispatcher()
        self._protocol = "https" if self.https else "http"
        self.port = 443 if self.https else self.web_port
        self.receive_unread_messages = receive_unread_messages
        self._url_for_upload_files = (
            f"{self._protocol}://{self.server}:{self.port}/bridge/api/client/v1/files"
        )
        self.verify_ssl = verify_ssl
        self._progress_queues: Dict[str, asyncio.Queue] = {}

        self._futures: Dict[int, asyncio.Future] = {}
        self._handlers: List[Tuple[dict, Callable[[dict], Awaitable]]] = []

        self._stop = False
        self._ws = None

    async def __call__(self, method: TrueConfMethod[T]) -> T:
        return await method(self)

    async def __get_domain_name(self):
        url = f"{self._protocol}://{self.server}:{self.port}/api/v4/server"

        try:
            async with httpx.AsyncClient(verify=False, timeout=5) as client:
                response = await client.get(url)
                return response.json().get("product").get("display_name")
        except Exception as e:
            loggers.chatbot.error(f"Failed to get server domain_name: {e}")
            return None

    @property
    def token(self) -> str:
        """
        Returns the bot's authorization token.

        Returns:
            str: The access token used for authentication.
        """

        return self.__token

    @async_cached_property
    async def server_name(self) -> str:
        """
        Returns the domain name of the TrueConf server.

        Returns:
            str: Domain name of the connected server.
        """

        return await self.__get_domain_name()

    @async_cached_property
    async def me(self) -> str:
        """
        Returns the identifier of the bot's personal (Favorites) chat.

        If the chat does not exist yet, it will be created automatically.
        The result is cached to prevent redundant API calls.

        Returns:
            str: Chat ID of the bot's personal Favorites chat.
        """

        r = await self.create_favorites_chat()
        return r.chat_id

    @classmethod
    def from_credentials(
            cls,
            server: str,
            username: str,
            password: str,
            dispatcher: Dispatcher | None = None,
            receive_unread_messages: bool = False,
            verify_ssl: bool = True,
            **token_opts: Unpack[TokenOpts],
    ) -> Self:
        """
        Creates a bot instance using username and password authentication.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/connect-and-auth/#connect-and-auth

        Args:
            server (str): Address of the TrueConf server.
            username (str): Username for authentication.
            password (str): Password for authentication.
            dispatcher (Dispatcher | None, optional): Dispatcher instance for registering handlers.
            receive_unread_messages (bool, optional): Whether to receive unread messages on connection. Defaults to False.
            verify_ssl (bool, optional): Whether to verify the server's SSL certificate. Defaults to True.
            **token_opts: Additional options passed to the token request, such as `web_port` and `https`.

        Returns:
            Bot: An authorized bot instance.

        Raises:
            RuntimeError: If the token could not be obtained.
        """

        token = get_auth_token(server, username, password, verify=verify_ssl)
        if not token:
            raise RuntimeError("Failed to obtain token")
        return cls(
            server,
            token,
            web_port=token_opts.get("web_port", 443),
            https=token_opts.get("https", True),
            dispatcher=dispatcher,
            receive_unread_messages=receive_unread_messages,
            verify_ssl=verify_ssl,
        )

    async def __wait_upload_complete(
            self,
            file_id: str,
            expected_size: int,
            timeout: float | None = None,
    ) -> bool:
        q = self._progress_queues.get(file_id)
        if q is None:
            q = asyncio.Queue()
            self._progress_queues[file_id] = q

        await self.subscribe_file_progress(file_id)
        try:
            while True:
                if timeout is None:
                    update = await q.get()
                else:
                    update = await asyncio.wait_for(q.get(), timeout=timeout)

                if update.progress >= expected_size:
                    return True
        except asyncio.TimeoutError:
            return False
        finally:
            await self.unsubscribe_file_progress(file_id)
            if self._progress_queues.get(file_id) is q:
                self._progress_queues.pop(file_id, None)

    async def __download_file_from_server(
            self,
            url: str,
            file_name: str,
            dest_path: str | Path | None = None,
            verify: bool | None = None,
            timeout: int = 60,
            chunk_size: int = 64 * 1024,
    ) -> Path | None:

        """
        Asynchronously download file by URL and save it to disk.

        If `dest_path` isn't provided, a temporary file will be created (similar to aiogram.File.download()).

        Args:
            url: Direct download URL.
            dest_path: Destination path; if None, a NamedTemporaryFile will be created and returned.
            verify: SSL verification flag; defaults to self.verify_ssl.
            timeout: Request timeout (seconds).
            chunk_size: Stream chunk size in bytes.


        Returns:
            Path | None: Path to saved file, or None on error.
        """

        v = self.verify_ssl if verify is None else verify

        if dest_path is None:
            tmp = tempfile.NamedTemporaryFile(prefix="tc_dl_", suffix=file_name, delete=False)
            dest = Path(tmp.name)
            tmp.close()
        else:
            dest = Path(dest_path) / file_name
            dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with httpx.AsyncClient(verify=v, timeout=httpx.Timeout(timeout)) as client:
                async with client.stream("GET", url) as resp:
                    resp.raise_for_status()
                    async with aiofiles.open(dest, "wb") as f:
                        async for chunk in resp.aiter_bytes(chunk_size):
                            if chunk:
                                await f.write(chunk)
            return dest
        except Exception as e:
            loggers.chatbot.error(f"Failed to download file from {url}: {e}")
            with contextlib.suppress(Exception):
                if dest.exists():
                    dest.unlink()
            return None

    async def __upload_file_to_server(
            self,
            file: InputFile,
            preview: InputFile | None = None,
            is_sticker: bool = False,
            verify: bool = True,
            timeout: int = 60,
    ) -> str | None:
        """
           Uploads a file to the server and returns a temporary file identifier (temporalFileId).

           This method is used for uploading attachments to a TrueConf chat: images, documents,
           stickers, and other file types. The `file` argument must be an instance of a class
           that inherits from `InputFile`, such as:

               - `BufferedInputFile(InputFile)` — from in-memory byte buffer
               - `FSInputFile(InputFile)` — from a local file
               - `URLInputFile(InputFile)` — from a remote URL

           Optionally, a preview file can be attached (for example, for videos or documents).
           If `is_sticker=True`, the MIME type of the file will be set to `sticker/webp`.

           Source:
                https://trueconf.com/docs/chatbot-connector/en/files/#upload-file-to-server-storage

           Args:
               file (InputFile): The primary file to upload.
               preview (InputFile | None, optional): Optional preview file (default is None).
               is_sticker (bool, optional): Whether the uploaded file is a sticker (affects MIME type). Defaults to False.
               verify (bool, optional): Whether to verify the SSL certificate. Defaults to True.
               timeout (int, optional): Upload timeout in seconds. Defaults to 60.

           Returns:
               str | None: A temporary file ID (`temporalFileId`) on success, or None if the upload failed.
           """

        if isinstance(file, URLInputFile):
            await file.prepare()
            if preview:
                await preview.prepare()

        res = await self(UploadFile(file_size=file.file_size))
        upload_task_id = res.upload_task_id

        headers = {
            "Upload-Task-Id": upload_task_id,

        }

        timeout = ClientTimeout(total=timeout)

        if not verify:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = TCPConnector(ssl=ssl_context)
        else:
            connector = TCPConnector()

        try:
            async with ClientSession(connector=connector, timeout=timeout) as session:
                data = FormData()
                data.add_field(
                    name="file",
                    value= await file.read(),
                    filename=file.filename,
                    content_type="sticker/webp" if is_sticker else file.mimetype,
                )

                if preview:
                    data.add_field(
                        name="preview",
                        value = await preview.read(),
                        filename=preview.filename,
                        content_type=preview.mimetype
                    )

                async with session.post(self._url_for_upload_files, headers=headers, data=data) as response:
                     result = await response.json()
            return result.get("temporalFileId")
        except Exception as e:
            loggers.chatbot.error(f"Failed to upload file to server: {e}")
        return None

    async def _send_ws_payload(self, message: dict) -> bool:
        if not self._session:
            loggers.chatbot.warning("Session is None — not connected")
            return False
        try:
            await self._session.send_json(message)
            return True
        except Exception as e:
            loggers.chatbot.error(f"❌ Send failed or connection closed: {e}")
            return False

    async def __connect_and_listen(self):
        ssl_context = ssl._create_unverified_context() if self.https else None
        uri = f"wss://{self.server}:{self.web_port}/websocket/chat_bot" if self.https else f"ws://{self.server}:{self.web_port}/websocket/chat_bot"

        while not self._stop:
            try:
                loggers.chatbot.info("⏳ Attempting WebSocket connection...")
                async with websockets.connect(uri, ssl=ssl_context, ping_interval=30, ping_timeout=10) as ws:
                    self._ws = ws
                    loggers.chatbot.info("✅ WebSocket connected")

                    if self._session is None:
                        self._session = WebSocketSession(on_message=self.__on_raw_message)
                    self._session.attach(ws)

                    self.connected_event.set()
                    self.authorized_event.clear()

                    try:
                        await self.__authorize()
                    except ApiErrorException as e:
                        loggers.chatbot.error(f"❌ Authorization failed: {e}")
                        raise

                    self.authorized_event.set()
                    await ws.wait_closed()

            except asyncio.CancelledError:
                loggers.chatbot.info("🛑 Connect loop cancelled, performing cleanup.")
                raise

            except websockets.exceptions.ConnectionClosed as e:
                loggers.chatbot.warning(
                    f"🔌 Connection closed: {getattr(e, 'code', '?')} – {getattr(e, 'reason', '?')}. Retrying...")
                self.connected_event.clear()
                self.authorized_event.clear()
                await asyncio.sleep(0.5)
                continue

            finally:
                self.connected_event.clear()
                self.authorized_event.clear()
                if self._session:
                    with contextlib.suppress(Exception):
                        await self._session.detach()
                self._ws = None

    def _register_future(self, id_: int, future):
        loggers.chatbot.debug(f"📬 Registered future for id={id_}")
        self._futures[id_] = future

    def __resolve_future(self, message: dict):
        if message.get("type") == 2 and "id" in message:
            future = self._futures.pop(message["id"], None)
            if future and not future.done():
                future.set_result(message)

    async def __authorize(self):
        loggers.chatbot.info("🚀 Starting authorization")

        call = AuthMethod(
            token=self.__token, receive_unread_messages=self.receive_unread_messages
        )
        loggers.chatbot.info(f"🛠 Created AuthMethod with id={call.id}")
        result = await self(call)
        loggers.chatbot.info(f"🔐 Authenticated as {result.user_id}")

    async def __process_message(self, data: dict):
        data = parse_update(data)
        if data is None:
            return

        if isinstance(data, UploadingProgress):
            q = self._progress_queues.get(data.file_id)
            if q:
                q.put_nowait(data)
                return

        if hasattr(data, "bind"):
            data.bind(self)

        payload = getattr(data, "payload", None)
        if hasattr(payload, "bind"):
            payload.bind(self)

        await self.dp._feed_update(data)

    async def __on_raw_message(self, raw: str):
        try:
            data = json.loads(raw)
        except Exception as e:
            loggers.chatbot.error(f"Failed to parse incoming message: {e}; raw={raw!r}")
            return
        # --- auto‑acknowledge every server request (type == 1) ---
        if isinstance(data, dict) and data.get("type") == 1 and "id" in data:
            # reply with {"type": 2, "id": <same id>}
            asyncio.create_task(self._send_ws_payload({"type": 2, "id": data["id"]}))
        self.__resolve_future(data)
        asyncio.create_task(self.__process_message(data))

    async def add_participant_to_chat(
            self,
            chat_id: str,
            user_id: str,
            display_history: bool = False
    ) -> AddChatParticipantResponse:
        """
        Adds a participant to the specified chat.

        Optionally allows showing chat history to the newly added participant.
        The `display_history` parameter is supported **only in TrueConf Server version 5.5.2 and above**.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#addChatParticipant

        Args:
            chat_id (str): Identifier of the chat to add the participant to.
            user_id (str): Identifier of the user to be added. If no domain is specified, the server domain will be used.
            display_history (bool, optional): Whether to show previous chat history to the participant.
                **Requires TrueConf Server 5.5.2+**. Defaults to **False**.

        Returns:
            AddChatParticipantResponse: Object containing the result of the participant addition.

        Example:
            ```python
            await bot.add_participant_to_chat(
                chat_id="chat123",
                user_id="user456",
                display_history=True
            )
            ```
        """

        if "@" not in user_id:
            user_id = f"{user_id}@{await self.server_name}"

        call = AddChatParticipant(chat_id=chat_id, user_id=user_id, display_history=display_history)
        return await self(call)

    async def change_participant_role(
            self,
            chat_id:str,
            user_id: str,
            role:str | ChatParticipantRole
    ) -> ChangeParticipantRoleResponse:
        """
        **Requires TrueConf Server 5.5.2+**.

        Changes the role of a participant in the specified group chat.

        This method requires that the bot has **moderator (admin)** or **owner** rights in the chat.

        Supported roles in group chat:
            - "owner" — group chat owner
            - "admin" — appointed moderator of the group chat
            - "user" — regular participant of a group chat

        It is recommended to use the enumeration class for safer role assignment:
            ```python
            from trueconf.enums import ChatParticipantRole
            ```

        For a full list of roles in conference, channel, or Favorites chats, see the documentation:

        Role descriptions:
            https://trueconf.com/docs/chatbot-connector/en/roles-and-users-rules/#which-roles-has-apis

        Role permissions matrix:
            https://trueconf.com/docs/chatbot-connector/en/roles-and-users-rules/#roles-rules-group-chats

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#changeParticipantRole

        Args:
            chat_id (str): Identifier of the chat where the role should be changed.
            user_id (str): Identifier of the participant whose role is being updated.
            role (str | ChatParticipantRole): New role to assign. Must be one of the supported roles listed above.

        Returns:
            ChangeParticipantRoleResponse: Object containing the result of the role change operation.

        Example:
            ```python
            from trueconf.enums import ChatParticipantRole as role

            await bot.change_participant_role(
                chat_id="chat123",
                user_id="user456",
                role=role.ADMIN
            )
            ```
        """

        if "@" not in user_id:
            user_id = f"{user_id}@{await self.server_name}"

        call = ChangeParticipantRole(chat_id=chat_id, user_id=user_id, role=role)
        return await self(call)

    async def create_channel(self, title: str) -> CreateChannelResponse:
        """
        Creates a new channel with the specified title.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#createChannel

        Args:
            title (str): Title of the new channel.

        Returns:
            CreateChannelResponse: Object containing the result of the channel creation.
        """

        loggers.chatbot.info(f"✉️ Create channel with name {title}")
        call = CreateChannel(title=title)
        return await self(call)

    async def create_favorites_chat(self) -> CreateFavoritesChatResponse:
        """
        **Requires TrueConf Server 5.5.2+**

        Creates a "Favorites" chat for the current user.

        This type of chat is a personal space accessible only to its owner.
        It can be used to store notes, upload files, or test bot features in a private context.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#createFavoritesChat

        Returns:
            CreateFavoritesChatResponse: An object containing information about the newly created chat.
        """

        loggers.chatbot.info(f"✉️ Create favorite chat")
        call = CreateFavoritesChat()
        return await self(call)

    async def create_group_chat(self, title: str) -> CreateGroupChatResponse:
        """
        Creates a new group chat with the specified title.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#createGroupChat

        Args:
            title (str): Title of the new group chat.

        Returns:
            CreateGroupChatResponse: Object containing the result of the group chat creation.
        """

        loggers.chatbot.info(f"✉️ Create group chat with name {title}")
        call = CreateGroupChat(title=title)
        return await self(call)

    async def create_personal_chat(self, user_id: str) -> CreateP2PChatResponse:
        """
        Creates a personal (P2P) chat with a user by their identifier.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#createP2PChat

        Args:
            user_id (str): Identifier of the user. Can be with or without a domain.

        Returns:
            CreateP2PChatResponse: Object containing the result of the personal chat creation.

        Note:
            Creating a personal chat (peer-to-peer) with a server user.
            If the bot has never messaged this user before, a new chat will be created.
            If the bot has previously sent messages to this user, the existing chat will be returned.
        """

        loggers.chatbot.info(f"✉️ Create personal chat with name {user_id}")

        if "@" not in user_id:
            user_id = f"{user_id}@{await self.server_name}"

        call = CreateP2PChat(user_id=user_id)
        return await self(call)

    async def delete_chat(self, chat_id: str) -> RemoveChatResponse:
        """
        Deletes a chat by its identifier.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#removeChat

        Args:
            chat_id: Identifier of the chat to be deleted.

        Returns:
            RemoveChatResponse: Object containing the result of the chat deletion.
        """

        call = RemoveChat(chat_id=chat_id)
        return await self(call)

    async def download_file_by_id(self, file_id, dest_path: str = None) -> Path | None:
        """
        Downloads a file by its ID, waiting for the upload to complete if necessary.

        If the file is already in the READY state, it will be downloaded immediately.
        If the file is in the NOT_AVAILABLE state, the method will exit without downloading.
        In other cases, the bot will wait for the upload to finish and then attempt to download the file.

        Args:
            file_id (str): Unique identifier of the file on the server.
            dest_path (str, optional): Path where the file should be saved.
                If not specified, a temporary file will be created using `NamedTemporaryFile`
                (with prefix `tc_dl_`, suffix set to the original file name, and `delete=False` to keep the file on disk).

        Returns:
            Path | None: Path to the downloaded file, or None if the download failed.
        """

        info = await self.get_file_info(file_id)

        if info.ready_state == FileReadyState.READY:
            return await self.__download_file_from_server(
                url=info.download_url,
                file_name=info.name,
                dest_path=dest_path,
                verify=self.verify_ssl
            )

        if info.ready_state == FileReadyState.NOT_AVAILABLE:
            loggers.chatbot.warning(f"File {file_id} is NOT_AVAILABLE")
            return None

        ok = await self.__wait_upload_complete(file_id, expected_size=info.size, timeout=None)
        if not ok:
            loggers.chatbot.error(f"Wait upload complete failed for {file_id}")
            return None

        for _ in range(20):
            info = await self.get_file_info(file_id)
            if info.ready_state == FileReadyState.READY:
                break
            await asyncio.sleep(1)
        else:
            loggers.chatbot.warning(f"File {file_id} didn’t reach READY in time")
            return None

        return await self.__download_file_from_server(
            url=info.download_url,
            file_name=info.name,
            dest_path=dest_path,
            verify=self.verify_ssl
        )

    async def edit_message(
            self, message_id: str, text: str, parse_mode: ParseMode | str = ParseMode.TEXT
    ) -> EditMessageResponse:
        """
        Edits a previously sent message.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#editMessage

        Args:
            message_id (str): Identifier of the message to be edited.
            text (str): New text content for the message.
            parse_mode (ParseMode | str, optional): Text formatting mode.
                Defaults to plain text.

        Returns:
            EditMessageResponse: Object containing the result of the message update.
        """

        call = EditMessage(message_id=message_id, text=text, parse_mode=parse_mode)
        return await self(call)

    async def edit_survey(
            self,
            message_id: str,
            title: str,
            survey_campaign_id: str,
            survey_type: SurveyType = SurveyType.NON_ANONYMOUS,
    ) -> EditSurveyResponse:
        """
        Edits a previously sent survey.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/surveys/#editSurvey

        Args:
            message_id (str): Identifier of the message containing the survey to edit.
            title (str): New title of the survey.
            survey_campaign_id (str): Identifier of the survey campaign.
            survey_type (SurveyType, optional): Type of the survey (anonymous or non-anonymous). Defaults to non-anonymous.

        Returns:
            EditSurveyResponse: Object containing the result of the survey update.
        """

        call = EditSurvey(
            message_id=message_id,
            server=self.server,
            path=survey_campaign_id,
            title=title,
            description=survey_type,
        )
        return await self(call)

    async def forward_message(
            self, chat_id: str, message_id: str
    ) -> ForwardMessageResponse:
        """
        Forwards a message to the specified chat.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#forwardMessage

        Args:
            chat_id (str): Identifier of the chat to forward the message to.
            message_id (str): Identifier of the message to be forwarded.

        Returns:
            ForwardMessageResponse: Object containing the result of the message forwarding.
        """

        call = ForwardMessage(chat_id=chat_id, message_id=message_id)
        return await self(call)

    async def get_chats(
            self, count: int = 10, page: int = 1
    ) -> GetChatsResponse:
        """
        Retrieves a paginated list of chats available to the bot.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#getChats

        Args:
            count (int, optional): Number of chats per page. Defaults to 10.
            page (int, optional): Page number. Must be greater than 0. Defaults to 1.

        Returns:
            GetChatsResponse: Object containing the result of the chat list request.

        Raises:
            ValueError: If the page number is less than 1.
        """

        if page < 1:
            raise ValueError("Argument <page> must be greater than 0")
        loggers.chatbot.info(f"✉️ Get info all chats by ")
        call = GetChats(count=count, page=page)
        return await self(call)

    async def get_chat_by_id(self, chat_id: str) -> GetChatByIdResponse:
        """
        Retrieves information about a chat by its identifier.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#getChatById

        Args:
            chat_id (str): Identifier of the chat.

        Returns:
            GetChatByIDResponse: Object containing information about the chat.
        """

        loggers.chatbot.info(f"✉️ Get info chat by {chat_id}")
        call = GetChatByID(chat_id=chat_id)
        return await self(call)

    async def get_chat_participants(
            self,
            chat_id: str,
            page_size: int,
            page_number: int
    ) -> GetChatParticipantsResponse:
        """
        Retrieves a paginated list of chat participants.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#getChatParticipants

        Args:
            chat_id (str): Identifier of the chat.
            page_size (int): Number of participants per page.
            page_number (int): Page number.

        Returns:
            GetChatParticipantsResponse: Object containing the result of the participant list request.
        """

        call = GetChatParticipants(
            chat_id=chat_id, page_size=page_size, page_number=page_number
        )
        return await self(call)

    async def get_chat_history(
            self,
            chat_id: str,
            count: int,
            from_message_id: str | None = None,
    ) -> GetChatHistoryResponse:
        """
        Retrieves the message history of the specified chat.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#getChatHistory

        Args:
            chat_id (str): Identifier of the chat.
            count (int): Number of messages to retrieve.
            from_message_id (str | None, optional): Identifier of the message to start retrieving history from.
                If not specified, the history will be loaded from the most recent message.

        Returns:
            GetChatHistoryResponse: Object containing the result of the chat history request.

        Raises:
            ValueError: If the count number is less than 1.
        """

        if count < 1:
            raise ValueError("Argument <count> must be greater than 0")

        call = GetChatHistory(
            chat_id=chat_id, count=count, from_message_id=from_message_id
        )
        return await self(call)

    async def get_file_info(self, file_id: str) -> GetFileInfoResponse:
        """
        Retrieves information about a file by its identifier.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#getFileInfo

        Args:
            file_id (str): Identifier of the file.

        Returns:
            GetFileInfoResponse: Object containing information about the file.
        """

        call = GetFileInfo(file_id=file_id)
        return await self(call)

    async def get_message_by_id(
            self, message_id: str
    ) -> GetMessageByIdResponse:
        """
        Retrieves a message by its identifier.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#getMessageById

        Args:
            message_id (str): Identifier of the message to retrieve.

        Returns:
            GetMessageByIdResponse: Object containing the retrieved message data.
        """

        call = GetMessageById(message_id=message_id)
        return await self(call)

    async def get_user_display_name(
            self, user_id: str
    ) -> GetUserDisplayNameResponse:
        """
        Retrieves the display name of a user by their TrueConf ID.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/contacts/#getUserDisplayName

        Args:
            user_id (str): User's TrueConf ID. Can be specified with or without a domain.

        Returns:
            GetUserDisplayNameResponse: Object containing the user's display name.
        """

        if "@" not in user_id:
            user_id = f"{user_id}@{await self.server_name}"

        call = GetUserDisplayName(user_id=user_id)
        return await self(call)

    async def has_chat_participant(
            self,
            chat_id: str,
            user_id: str
    ) -> HasChatParticipantResponse:
        """
        Checks whether the specified user is a participant in the chat.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#hasChatParticipant

        Args:
            chat_id (str): Identifier of the chat.
            user_id (str): Identifier of the user. Can be with or without a domain.

        Returns:
            HasChatParticipantResponse: Object containing the result of the check.
        """

        if "@" not in user_id:
            user_id = f"{user_id}@{await self.server_name}"

        call = HasChatParticipant(chat_id=chat_id, user_id=user_id)
        return await self(call)

    async def remove_message(
            self, message_id: str, for_all: bool = False
    ) -> RemoveMessageResponse:
        """
        Removes a message by its identifier.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#removeMessage

        Args:
            message_id (str): Identifier of the message to be removed.
            for_all (bool, optional): If True, the message will be removed for all participants.
                Default to False (the message is removed only for the bot).

        Returns:
            RemoveMessageResponse: Object containing the result of the message deletion.
        """

        call = RemoveMessage(message_id=message_id, for_all=for_all)
        return await self(call)

    async def remove_participant_from_chat(
            self, chat_id: str, user_id: str
    ) -> RemoveChatParticipantResponse:
        """
        Removes a participant from the specified chat.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#removeChatParticipant

        Args:
            chat_id (str): Identifier of the chat to remove the participant from.
            user_id (str): Identifier of the user to be removed.

        Returns:
            RemoveChatParticipantResponse: Object containing the result of the participant removal.
        """

        if "@" not in user_id:
            user_id = f"{user_id}@{await self.server_name}"

        call = RemoveChatParticipant(chat_id=chat_id, user_id=user_id)
        return await self(call)

    async def reply_message(
            self,
            chat_id: str,
            message_id: str,
            text: str,
            parse_mode: ParseMode | str = ParseMode.TEXT,
    ) -> SendMessageResponse:
        """
        Sends a reply to an existing message in the chat.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#replyMessage

        Args:
            chat_id (str): Identifier of the chat where the reply will be sent.
            message_id (str): Identifier of the message to reply to.
            text (str): Text content of the reply.
            parse_mode (ParseMode | str, optional): Text formatting mode.
                Defaults to plain text.

        Returns:
            SendMessageResponse: Object containing the result of the message delivery.
        """

        call = SendMessage(
            chat_id=chat_id,
            reply_message_id=message_id,
            text=text,
            parse_mode=parse_mode,
        )
        return await self(call)

    async def run(self, handle_signals: bool = True) -> None:
        """
        Runs the bot and waits until it stops. Supports handling termination signals (SIGINT, SIGTERM).

        Args:
            handle_signals (bool, optional): Whether to handle termination signals. Defaults to True.

        Returns:
            None
        """

        if handle_signals:
            loop = asyncio.get_running_loop()
            try:
                loop.add_signal_handler(
                    signal.SIGINT, lambda: asyncio.create_task(self.shutdown())
                )
                loop.add_signal_handler(
                    signal.SIGTERM, lambda: asyncio.create_task(self.shutdown())
                )
            except NotImplementedError:
                pass

        await self.start()
        await self.connected_event.wait()
        await self.authorized_event.wait()
        await self.stopped_event.wait()

    async def send_document(
            self,
            chat_id: str,
            file: InputFile,
            caption: str | None = None,
            parse_mode: ParseMode | str = ParseMode.TEXT,
    ) -> SendFileResponse:
        """
        Sends a document or any arbitrary file to the specified chat.

        This method supports all file types, including images.
        However, images sent via this method will be transferred **in original, uncompressed form**.
        If you want to send a compressed image with preview support, use `send_photo()` instead.

        The file must be provided as an instance of one of the `InputFile` subclasses:
        `FSInputFile`, `BufferedInputFile`, or `URLInputFile`.

        Args:
            chat_id (str): The identifier of the chat to which the document will be sent.
            file (InputFile): The file to be uploaded. Must be a subclass of `InputFile`.
            caption (str | None): Optional caption text to be sent with the file.
            parse_mode (ParseMode | str): Text formatting mode (e.g., Markdown, HTML, or plain text).

        Returns:
            SendFileResponse: An object containing the result of the file upload.

        Example:
            ```python
            await bot.send_document(
                chat_id="a1s2d3f4f5g6",
                file=FSInputFile("report.pdf"),
                caption="📄 Annual report **for 2025**",
                parse_mode=ParseMode.MARKDOWN
            )
            ```
        """

        loggers.chatbot.info(f"✉️ Sending file to {chat_id}")

        temporal_file_id = await self.__upload_file_to_server(
            file=file,
            verify=self.verify_ssl,
        )

        call = SendFile(chat_id=chat_id, temporal_file_id=temporal_file_id, text=caption, parse_mode=parse_mode)
        return await self(call)

    async def send_message(
            self,
            chat_id: str,
            text: str,
            parse_mode: ParseMode | str = ParseMode.TEXT
    ) -> SendMessageResponse:
        """
        Sends a message to the specified chat.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#sendMessage

        Args:
            chat_id (str): Identifier of the chat to send the message to.
            text (str): Text content of the message.
            parse_mode (ParseMode | str, optional): Text formatting mode.
                Defaults to plain text.

        Returns:
            SendMessageResponse: Object containing the result of the message delivery.
        """

        loggers.chatbot.info(f"✉️ Sending message to {chat_id}")
        call = SendMessage(chat_id=chat_id, text=text, parse_mode=parse_mode)
        return await self(call)

    async def send_photo(
            self,
            chat_id: str,
            file: InputFile,
            preview: InputFile | None,
            caption: str | None = None,
            parse_mode: ParseMode | str = ParseMode.TEXT
    ) -> SendFileResponse:
        """
        Sends a photo to the specified chat, with optional caption and preview support.

        This method is recommended when sending **compressed images with preview** support.
        If you want to send uncompressed images or arbitrary files, use `send_document()` instead.

        The file must be provided as an instance of one of the `InputFile` subclasses:
        `FSInputFile`, `BufferedInputFile`, or `URLInputFile`.

        Supported image formats include:
        `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.gif`, `.tiff`

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#file-transfer

        Args:
            chat_id (str): Identifier of the chat to which the photo will be sent.
            file (InputFile): The photo file to upload. Must be a subclass of `InputFile`.
            preview (InputFile | None): Optional preview image. Must also be an `InputFile` if provided.
            caption (str | None): Optional caption to be sent along with the image.
            parse_mode (ParseMode | str): Formatting mode for the caption (e.g., Markdown, HTML, plain text).

        Returns:
            SendFileResponse: An object containing the result of the file upload.

        Example:
            ```python
            await bot.send_photo(
                chat_id="a1s2d3f4f5g6",
                file=FSInputFile("image.jpg"),
                preview=FSInputFile("image_preview.webp"),
                caption="Here's our **team** photo 📸",
                parse_mode=ParseMode.MARKDOWN
            )
            ```
        """

        loggers.chatbot.info(f"✉️ Sending photo to {chat_id}")

        temporal_file_id = await self.__upload_file_to_server(
            file=file,
            preview=preview,
            verify=self.verify_ssl,
        )

        call = SendFile(chat_id=chat_id, temporal_file_id=temporal_file_id, text=caption, parse_mode=parse_mode)
        return await self(call)

    async def send_sticker(self, chat_id: str, file: InputFile) -> SendFileResponse:
        """
        Sends a sticker in WebP format to the specified chat.

        The file must have a MIME type of `'image/webp'`, otherwise a `TypeError`
        will be raised. The file must be an instance of one of the `InputFile` subclasses:
        `FSInputFile`, `BufferedInputFile`, or `URLInputFile`.

        A preview is automatically generated from the source file, as required
        for sticker uploads in TrueConf.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#file-transfer

        Args:
            chat_id (str): Identifier of the chat to which the sticker will be sent.
            file (InputFile): The sticker file in WebP format. Must be a subclass of `InputFile`.

        Returns:
            SendFileResponse: An object containing the result of the file upload.

        Raises:
            TypeError: If the file's MIME type is not `'image/webp'`.

        Example:
            ```python
            await bot.send_sticker(chat_id="user123", file=FSInputFile("sticker.webp"))
            ```
        """

        if file.mimetype != "image/webp":
            raise TypeError("File type not supported. File type must be 'image/webp'")

        loggers.chatbot.info(f"✉️ Sending file to {chat_id}")

        temporal_file_id = await self.__upload_file_to_server(
            file=file,
            preview=file.clone(),
            is_sticker=True,
            verify=self.verify_ssl
        )

        call = SendFile(chat_id=chat_id, temporal_file_id=temporal_file_id)
        return await self(call)

    async def send_survey(
            self,
            chat_id: str,
            title: str,
            survey_campaign_id: str,
            reply_message_id: str = None,
            survey_type: SurveyType = SurveyType.NON_ANONYMOUS,
    ) -> SendSurveyResponse:
        """
        Sends a survey to the specified chat.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/surveys/#sendSurvey

        Args:
            chat_id (str): Identifier of the chat to send the survey to.
            title (str): Title of the survey displayed in the chat.
            survey_campaign_id (str): Identifier of the survey campaign.
            reply_message_id (str, optional): Identifier of the message being replied to.
            survey_type (SurveyType, optional): Type of the survey (anonymous or non-anonymous). Defaults to non-anonymous.

        Returns:
            SendSurveyResponse: Object containing the result of the survey submission.
        """

        secret = await generate_secret_for_survey(title=title)

        call = SendSurvey(
            chat_id=chat_id,
            server=self.server,
            reply_message_id=reply_message_id,
            path=survey_campaign_id,
            title=title,
            description=survey_type,
            secret=secret,
        )
        return await self(call)

    async def start(self) -> None:
        """
        Starts the bot by connecting to the server and listening for incoming events.

        Note:
            This method is safe to call multiple times — subsequent calls are ignored
            if the connection is already active.

        Returns:
            None
        """
        if self._connect_task and not self._connect_task.done():
            return
        self._stop = False
        self._connect_task = asyncio.create_task(self.__connect_and_listen())

    async def shutdown(self) -> None:
        """
        Gracefully shuts down the bot, cancels the connection task, and closes active sessions.

        This method:

        - Cancels the connection task if it is still active;
        - Closes the WebSocket session or `self.session` if they are open;
        - Clears the connection and authorization events;
        - Sets the `stopped_event` flag.

        Returns:
            None
        """

        self._stop = True
        if self._connect_task and not self._connect_task.done():
            self._connect_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._connect_task
        self._connect_task = None

        try:
            if self._session:
                with contextlib.suppress(Exception):
                    await self._session.close()
            elif self._ws:
                with contextlib.suppress(Exception):
                    await self._ws.close()
        finally:
            self._ws = None
            self.connected_event.clear()
            self.authorized_event.clear()
            loggers.chatbot.info("🛑 ChatBot stopped")
            self.stopped_event.set()
            # sys.exit()

    async def subscribe_file_progress(
            self, file_id: str
    ) -> SubscribeFileProgressResponse:
        """
        Subscribes to file transfer progress updates.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#subscribeFileProgress

        Args:
            file_id (str): Identifier of the file.

        Returns:
            SubscribeFileProgressResponse: Object containing the result of the subscription.

        Note:
            If the file is in the UPLOADING status, you can subscribe to the upload process
            to be notified when the file becomes available.
        """

        call = SubscribeFileProgress(file_id=file_id)
        return await self(call)

    async def unsubscribe_file_progress(
            self, file_id: str
    ) -> UnsubscribeFileProgressResponse:
        """
        Unsubscribes from receiving file upload progress events.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#unsubscribeFileProgress

        Args:
            file_id (str): Identifier of the file.

        Returns:
            UnsubscribeFileProgressResponse: Object containing the result of the unsubscription.

        Note:
            If necessary, you can unsubscribe from file upload events that were previously subscribed to
            using the `subscribe_file_progress()` method.
        """

        call = UnsubscribeFileProgress(file_id=file_id)
        return await self(call)
