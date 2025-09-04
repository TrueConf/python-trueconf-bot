from __future__ import annotations
import logging
from asyncio import get_running_loop
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, TYPE_CHECKING, ClassVar, Protocol, runtime_checkable
from trueconf.exceptions import ApiError as ApiErrorException
from trueconf.types.responses.api_error import ApiError

logger = logging.getLogger("chat_bot")

T = TypeVar("T")


@runtime_checkable
class ReturnResolver(Protocol[T]):
    @staticmethod
    def parse(resp: dict) -> T: ...


class MessageIdCounter:
    _counter = 0

    @classmethod
    def get_next_id(cls) -> int:
        cls._counter += 1
        return cls._counter


class TrueConfMethod(ABC, Generic[T]):
    def __init__(self):
        self.id = MessageIdCounter.get_next_id()

    if TYPE_CHECKING:
        __api_method__: ClassVar[str]
        __returning__: ClassVar[type[T]]
    else:
        @property
        @abstractmethod
        def __api_method__(self) -> str:
            ...

        @property
        @abstractmethod
        def __returning__(self) -> type[T]:
            ...

    @abstractmethod
    def payload(self) -> dict:
        ...

    def _parse_return(self, resp: dict) -> T:
        ret = self.__returning__

        payload = (resp.get("payload") or {})

        # 2) Ошибка API имеет приоритет
        if isinstance(payload, dict) and payload.get("errorCode", 0) != 0:
            return ApiError.from_dict(payload)  # type: ignore[return-value] # type: ignore[return-value]

        # 1) Кастомный парсер (если класс его предоставляет)
        if hasattr(ret, "parse"):
            return ret.parse(resp)  # type: ignore[return-value]

        # 3) Если просят dict — отдать как есть
        if ret is dict:
            return payload  # type: ignore[return-value]

        # 4) Поддержка mashumaro: есть from_dict -> используем alias-ы
        if hasattr(ret, "from_dict"):
            if isinstance(payload, list):
                return ret.from_dict({"chats": payload})  # type: ignore[return-value]
            return ret.from_dict(payload)  # type: ignore[return-value]

        # 5) Фоллбек: прямой конструктор (без alias-ов)
        return ret(**payload)  # type: ignore[misc]

    async def __call__(self, bot: "ChatBot") -> T:
        loop = get_running_loop()
        future = loop.create_future()
        bot._register_future(self.id, future)

        try:
            message = {
                "type": 1,
                "id": self.id,
                "method": self.__api_method__,
                "payload": self.payload(),
            }

        except AttributeError:
            raise RuntimeError(
                f"{type(self).__name__} must define __api_method__ and __returning__"
            )

        logger.debug(f"📤 Sending message: {message}")

        await bot._send_ws_payload(message)

        data = await future
        logger.debug(f"✅ Received response for {self.__api_method__}: {data}")

        result = self._parse_return(data)

        if isinstance(result, ApiError):
            raise ApiErrorException(str(result))

        return result
