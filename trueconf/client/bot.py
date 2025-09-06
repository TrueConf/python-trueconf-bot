import aiofiles
import asyncio
import contextlib
import httpx
import json
import mimetypes
import signal
import ssl
import tempfile
import websockets
from pathlib import Path
from contextlib import AsyncExitStack
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
from trueconf.exceptions import ApiError
from trueconf.methods.add_participant_to_chat import AddChatParticipant
from trueconf.methods.auth import AuthMethod
from trueconf.methods.base import TrueConfMethod
from trueconf.methods.create_channel import CreateChannel
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
from trueconf.types.parser import parse_update
from trueconf.types.requests.uploading_progress import UploadingProgress
from trueconf.types.responses.add_chat_participant_response import AddChatParticipantResponse
from trueconf.types.responses.api_error import ApiError
from trueconf.types.responses.create_channel_response import CreateChannelResponse
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
            https://trueconf.com/docs/chatbot-connector/en/connect-and-auth/#websocket-connection-authorization

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

        self._domain = None

        self._futures: Dict[int, asyncio.Future] = {}
        self._handlers: List[Tuple[dict, Callable[[dict], Awaitable]]] = []

        self._stop = False
        self._ws = None

    async def __call__(self, method: TrueConfMethod[T]) -> T:
        return await method(self)

    def __get_domain_name(self):
        url = f"{self._protocol}://{self.server}:{self.port}/api/v4/server"

        try:
            with httpx.Client(verify=False, timeout=5) as client:
                response = client.get(url)
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

    @property
    def server_name(self) -> str:
        """
        Returns the domain name of the TrueConf server.

        Returns:
            str: Domain name of the connected server.
        """

        if self._domain is None:
            self._domain = self.__get_domain_name()
        return self._domain

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
            https://trueconf.com/docs/chatbot-connector/en/getting-started/#authorization

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
            file_path: str,
            preview_path: str | None = None,
            preview_mimetype: str | None = None,
            verify: bool = True,
            timeout: int = 60,
    ) -> str | None:
        """
        Uploads a file to the server and returns its temporary identifier (temporalFileId).

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#uploading-a-file-to-the-file-storage

        Args:
            file_path (str): Path to the file to be uploaded.
            preview_path (bytes | None, optional): Preview data in WebP format (if applicable).
            preview_mimetype (str, optional): MIME type of the preview, e.g., "image/webp".
            verify (bool, optional): Whether to verify the SSL certificate. Defaults to True.
            timeout (int, optional): Upload timeout in seconds. Defaults to 60.

        Returns:
            str | None: Temporary file identifier (temporalFileId), or None if the upload failed.
        """

        file = Path(file_path)
        file_size = file.stat().st_size
        file_name = file.name
        file_mimetype = mimetypes.guess_type(file_path)[0]

        res = await self(UploadFile(file_size=file_size))
        upload_task_id = res.upload_task_id

        headers = {
            "Upload-Task-Id": upload_task_id,
        }

        try:

            async with AsyncExitStack() as stack:
                client = await stack.enter_async_context(
                    httpx.AsyncClient(verify=verify, timeout=httpx.Timeout(timeout)))

                f = stack.enter_context(open(file_path, "rb"))
                files = {"file": (file_name, f, file_mimetype)}

                if preview_path is not None:
                    p = stack.enter_context(open(preview_path, "rb"))
                    files["preview"] = (file_name, p, mimetypes.guess_type(preview_path)[0])

                elif preview_mimetype == "sticker/webp":
                    files["preview"] = (file_name, f, preview_mimetype)

                response = await client.post(self._url_for_upload_files, headers=headers, files=files)
            return response.json().get("temporalFileId")
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
        uri = f"wss://{self.server}:{self.web_port}/websocket/chat_bot"

        try:
            async for ws in websockets.connect(
                    uri, ssl=ssl_context, ping_interval=30, ping_timeout=10
            ):
                if self._stop:
                    break

                self._ws = ws
                loggers.chatbot.info("✅ WebSocket connected")

                if self._session is None:
                    self._session = WebSocketSession(on_message=self.__on_raw_message)
                self._session.attach(ws)

                self.connected_event.set()
                self.authorized_event.clear()

                try:
                    await self.__authorize()
                    self.authorized_event.set()
                    try:
                        await ws.wait_closed()
                    except asyncio.CancelledError:
                        loggers.chatbot.info("🛑 Cancellation requested; closing ws")
                        with contextlib.suppress(Exception):
                            await ws.close()
                        raise

                except websockets.exceptions.ConnectionClosed as e:
                    loggers.chatbot.warning(
                        f"🔌 Connection closed: {getattr(e, 'code', '?')} - {getattr(e, 'reason', '?')}"
                    )
                    continue
                except asyncio.CancelledError:
                    loggers.chatbot.info("🛑 Connect loop cancelled")
                    raise
                except ApiError as e:
                    print(e)
                    await self.shutdown()
                finally:
                    self.connected_event.clear()
                    if self._session:
                        await self._session.detach()
                if self._stop:
                    break
        except asyncio.CancelledError:
            loggers.chatbot.info("🛑 connect_and_listen task finished by cancellation")
            raise

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
            self, chat_id: str, user_id: str
    ) -> AddChatParticipantResponse:
        """
        Adds a participant to the specified chat.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#adding-a-participant-to-the-chat

        Args:
            chat_id (str): Identifier of the chat to add the participant to.
            user_id (str): Identifier of the user to be added.

        Returns:
            AddChatParticipantResponse: Object containing the result of the participant addition.
        """

        if "@" not in user_id:
            user_id = f"{user_id}@{self.server_name}"

        call = AddChatParticipant(chat_id=chat_id, user_id=user_id)
        return await self(call)

    async def create_channel(self, title: str) -> CreateChannelResponse:
        """
        Creates a new channel with the specified title.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#creating-a-channel

        Args:
            title (str): Title of the new channel.

        Returns:
            CreateChannelResponse: Object containing the result of the channel creation.
        """

        loggers.chatbot.info(f"✉️ Create channel with name {title}")
        call = CreateChannel(title=title)
        return await self(call)

    async def create_group_chat(self, title: str) -> CreateGroupChatResponse:
        """
        Creates a new group chat with the specified title.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#creating-a-group-chat

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
            https://trueconf.com/docs/chatbot-connector/en/chats/#creating-a-personal-chat-with-a-user

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
            user_id = f"{user_id}@{self.server_name}"

        call = CreateP2PChat(user_id=user_id)
        return await self(call)

    async def delete_chat(self, chat_id: str) -> RemoveChatResponse:
        """
        Deletes a chat by its identifier.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/chats/#deleting-chat

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
            https://trueconf.com/docs/chatbot-connector/en/messages/#editing-an-existing-message

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
            https://trueconf.com/docs/chatbot-connector/en/surveys/#editing-a-poll-message

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
            https://trueconf.com/docs/chatbot-connector/en/messages/#forwarding-a-message-to-another-chat

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
            https://trueconf.com/docs/chatbot-connector/en/chats/#retrieving-the-list-of-chats

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
            https://trueconf.com/docs/chatbot-connector/en/chats/#retrieving-chat-information-by-id

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
            https://trueconf.com/docs/chatbot-connector/en/chats/#retrieving-the-list-of-chat-participants

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
            https://trueconf.com/docs/chatbot-connector/en/messages/#retrieving-chat-history

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
            https://trueconf.com/docs/chatbot-connector/en/files/#retrieving-file-information-and-downloading-the-file

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
            https://trueconf.com/docs/chatbot-connector/en/messages/#retrieving-a-message-by-its-id

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
            https://trueconf.com/docs/chatbot-connector/en/contacts/#retrieving-the-display-name-of-a-user-by-their-trueconf-id

        Args:
            user_id (str): User's TrueConf ID. Can be specified with or without a domain.

        Returns:
            GetUserDisplayNameResponse: Object containing the user's display name.
        """

        if "@" not in user_id:
            user_id = f"{user_id}@{self.server_name}"

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
            https://trueconf.com/docs/chatbot-connector/en/chats/#checking-participant-presence-in-chat

        Args:
            chat_id (str): Identifier of the chat.
            user_id (str): Identifier of the user. Can be with or without a domain.

        Returns:
            HasChatParticipantResponse: Object containing the result of the check.
        """

        if "@" not in user_id:
            user_id = f"{user_id}@{self.server_name}"

        call = HasChatParticipant(chat_id=chat_id, user_id=user_id)
        return await self(call)

    async def remove_message(
            self, message_id: str, for_all: bool = False
    ) -> RemoveMessageResponse:
        """
        Removes a message by its identifier.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/messages/#deleting-a-message

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
            https://trueconf.com/docs/chatbot-connector/en/chats/#removing-a-participant-from-the-chat

        Args:
            chat_id (str): Identifier of the chat to remove the participant from.
            user_id (str): Identifier of the user to be removed.

        Returns:
            RemoveChatParticipantResponse: Object containing the result of the participant removal.
        """

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
            https://trueconf.com/docs/chatbot-connector/en/messages/#reply-to-an-existing-message

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

    async def send_document(self, chat_id: str, file_path: str) -> SendFileResponse:
        """
        Sends a document to the specified chat.

        Files of any format are supported. A preview is automatically generated for the following file types:
        .jpg, .jpeg, .png, .webp, .bmp, .gif, .tiff, .pdf

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#file-transfer

        Args:
            chat_id (str): Identifier of the chat to send the document to.
            file_path (str): Path to the document file.

        Returns:
            SendFileResponse: Object containing the result of the file upload.
        """

        loggers.chatbot.info(f"✉️ Sending file to {chat_id}")

        temporal_file_id = await self.__upload_file_to_server(
            file_path=file_path,
            verify=self.verify_ssl,
        )

        call = SendFile(chat_id=chat_id, temporal_file_id=temporal_file_id)
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
            https://trueconf.com/docs/chatbot-connector/en/messages/#sending-a-text-message-in-chat

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

    async def send_photo(self, chat_id: str, file_path: str, preview_path: str | None) -> SendFileResponse:
        """
        Sends a photo to the specified chat with preview (optional).

        Supported image formats: .jpg, .jpeg, .png, .webp, .bmp, .gif, .tiff

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#file-transfer

        Args:
            chat_id (str): Identifier of the chat to send the photo to.
            file_path (str): Path to the image file.
            preview_path (str | None): Path to the preview image.

        Returns:
            SendFileResponse: Object containing the result of the file upload.

        Examples:
            >>> bot.send_photo(chat_id="a1s2d3f4f5g6", file_path="/path/to/image.jpg", preview_path="/path/to/preview.webp")
        """

        loggers.chatbot.info(f"✉️ Sending photo to {chat_id}")

        temporal_file_id = await self.__upload_file_to_server(
            file_path=file_path,
            preview_path=preview_path,
            verify=self.verify_ssl,
        )

        call = SendFile(chat_id=chat_id, temporal_file_id=temporal_file_id)
        return await self(call)

    async def send_sticker(
            self, chat_id: str, file_path: str
    ) -> SendFileResponse:
        """
        Sends a WebP-format sticker to the specified chat.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#file-transfer

        Args:
            chat_id (str): Identifier of the chat to send the sticker to.
            file_path (str): Path to the sticker file in WebP format.

        Returns:
            SendFileResponse: Object containing the result of the file upload.

        Raises:
            TypeError: If the file does not have the MIME type 'image/webp'.
        """

        if mimetypes.guess_type(file_path)[0] != "image/webp":
            raise TypeError("File type not supported. File type must be 'image/webp'")

        loggers.chatbot.info(f"✉️ Sending file to {chat_id}")

        temporal_file_id = await self.__upload_file_to_server(
            file_path=file_path, preview_mimetype="sticker/webp", verify=self.verify_ssl
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
            https://trueconf.com/docs/chatbot-connector/en/surveys/#sending-a-poll-message-in-chat

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
            https://trueconf.com/docs/chatbot-connector/en/files/#subscription-to-file-upload-progress-on-the-server

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
            https://trueconf.com/docs/chatbot-connector/en/files/#unsubscribe-from-receiving-upload-event-notifications

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
