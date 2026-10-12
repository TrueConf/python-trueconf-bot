from __future__ import annotations

import io
import os
import re
import warnings
from abc import ABC, abstractmethod
from mimetypes import guess_extension, guess_type
from pathlib import Path
from typing import Any, Dict
from urllib.parse import unquote, urlparse

import aiofiles
import filetype
from httpx2 import AsyncClient
from typing_extensions import Self

from trueconf import loggers
from trueconf.exceptions import FileSizeTooLargeError, FileUploadError
from trueconf.utils._user_agent import get_user_agent

try:
    import magic
except ImportError as e:
    raise ImportError(
        "python-magic couldn't load the system dependency 'libmagic'.\n"
        "\n"
        "To fix this error you need to install a native (C) library in your OS.\n"
        "\n"
        "Install examples:\n"
        "  - macOS:   brew install libmagic\n"
        "  - Linux:   sudo apt install libmagic1\n"
        "  - Windows: pip install python-magic-bin\n"
        "\n"
        "Also see docs:\n"
        "  https://trueconf.github.io/python-trueconf-bot/latest/learn/files/#mime-detection-with-python-magic\n"
    ) from e


def detect_mime_type(data: bytes, file_name: str = "") -> str:
    mime_type, _ = guess_type(file_name) if file_name else (None, None)

    if not mime_type or mime_type == "application/octet-stream":
        kind = filetype.guess(data)
        if kind:
            mime_type = kind.mime

    if (not mime_type or mime_type == "application/octet-stream") and magic:
        try:
            mime_type = magic.from_buffer(data, mime=True)
        except Exception as error:
            loggers.chatbot.debug(f"Failed to detect mime_type via magic: {error}")
    return mime_type or "application/octet-stream"


def file_name_from_url(url: str) -> str:
    path = urlparse(url).path
    return Path(unquote(path)).name


def file_name_from_content_disposition(header: str) -> str | None:
    match = re.search(r'file_name\*?=(?:UTF-8\'\')?"?([^\";]+)"?', header)
    if match:
        return unquote(match.group(1))
    return None


class InputFile(ABC):
    """
    Base abstract class representing uploadable files.

    This class defines a common interface for all file types that can be uploaded
    to the TrueConf Server. It should not be used directly.
    Instead, use one of its subclasses:

    - `BufferedInputFile` — for in-memory byte data
    - `FSInputFile` — for files from the local filesystem
    - `URLInputFile` — for downloading files from a URL

    Each subclass implements the `read()` and `clone()` methods required for
    asynchronous uploads and reusability of the same file object.

    Source:
        https://trueconf.com/docs/chatbot-connector/en/files/#upload-file-to-server-storage

    Args:
        file_name (str): Name of the file to display when sending.
        file_size (int | None): File size in bytes (optional).
        mime_type (str | None): MIME type of the file. Can be detected automatically.

    Abstract Methods:
        read(): Asynchronously reads the file content.
        clone(): Creates a new copy of the file object. Useful for reuse (e.g., preview uploads).

    Example:
        ```python
        file = FSInputFile("example.pdf")
        await bot.send_document(chat_id="...", file=file)
        ```
    """

    def __init__(
        self,
        file_name: str | None = None,
        file_size: int | None = None,
        mime_type: str | None = None,
    ):

        if file_name and not guess_type(file_name)[0]:
            if ext := guess_extension(mime_type):
                file_name = file_name + ext

        self.file_name = file_name
        self.file_size = file_size
        self.mime_type = mime_type
        self.extension = Path(file_name).suffix.lower()[1:] if file_name else ""

    @abstractmethod
    async def read(self):  # pragma: no cover
        yield b""

    @abstractmethod
    def clone(self) -> Self:
        raise NotImplementedError("This file type does not support cloning.")


class BufferedInputFile(InputFile):
    """
    Represents a file uploaded from a bytes buffer.

    This class is useful when the file is already available as a `bytes` object, for example,
    if it was retrieved from a database, memory, or downloaded from an external source.
    Automatically detects MIME type and file size if not provided.

    Example:
        ```python
        file = BufferedInputFile(file=data_bytes, file_name="example.txt")
        await bot.send_document(chat_id="...", file=file)
        ```

    Note:
        Use `BufferedInputFile.from_file(...)` for convenient file loading from disk.
    """

    def __init__(
        self,
        file: bytes,
        file_name: str | None = None,
        file_size: int | None = None,
        mime_type: str | None = None,
        **kwargs,
    ):
        """
        Initializes a file from a bytes buffer.

        Args:
            file (bytes): Raw file content in bytes.
            file_name (str, optional): The name of the file.
            file_size (int, optional): Size of the file in bytes. Auto-detected if not specified.
            mime_type (str, optional): MIME type of the file. Auto-detected if not specified.
        """

        if "filename" in kwargs:
            warnings.warn(
                "'filename' is deprecated; use 'file_name' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            file_name = file_name or kwargs.pop("filename")

        if "mimetype" in kwargs:
            warnings.warn(
                "'mimetype' is deprecated; use 'mime_type' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            mime_type = mime_type or kwargs.pop("mimetype")

        if not file_name:
            raise TypeError("BufferedInputFile.__init__() requires a non-empty 'file_name'")

        if file_size is None:
            file_size = len(file)
        if mime_type is None:
            mime_type = detect_mime_type(file, file_name)

        super().__init__(file_name=file_name, file_size=file_size, mime_type=mime_type)

        self.data = file

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        file_name: str | None = None,
        file_size: int | None = None,
        mime_type: str | None = None,
        **kwargs,
    ) -> BufferedInputFile:
        """
        Creates a `BufferedInputFile` from a file on disk.

        This is a convenient way to load a file into memory if it needs to be reused
        or processed before sending.

        Args:
            path (str | Path): Path to the local file.
            file_name (str, optional): File name to propagate. Defaults to the name extracted from path.
            file_size (int, optional): File size in bytes. Auto-detected if not specified.
            mime_type (str, optional): MIME type of the file. Auto-detected if not specified.

        Returns:
            BufferedInputFile: A new instance ready for upload.
        """

        if "filename" in kwargs:
            warnings.warn(
                "'filename' is deprecated; use 'file_name' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            file_name = file_name or kwargs.pop("filename")

        if "mimetype" in kwargs:
            warnings.warn(
                "'mimetype' is deprecated; use 'mime_type' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            mime_type = mime_type or kwargs.pop("mimetype")

        if file_name is None:
            file_name = os.path.basename(path)
        if not file_name:
            raise ValueError(f"Cannot determine file name from path: {path}")
        with open(path, "rb") as f:
            data = f.read()

        if file_size is None:
            file_size = len(data)

        if mime_type is None:
            mime_type = detect_mime_type(data, file_name)

        return cls(data, file_name=file_name, file_size=file_size, mime_type=mime_type)

    async def read(self):
        """
        Asynchronously returns the file content as a `BytesIO` stream.

        Returns:
            BytesIO: A stream containing the file content.
        """
        return io.BytesIO(self.data)

    def clone(self) -> BufferedInputFile:
        """
        Creates a clone of the current file object.

        This method is useful when the same file needs to be reused (e.g., as a preview),
        while keeping the original instance intact.

        Returns:
            BufferedInputFile: A new instance with identical content.
        """

        return BufferedInputFile(
            file=self.data,
            file_name=self.file_name,
            file_size=self.file_size,
            mime_type=self.mime_type,
        )


class FSInputFile(InputFile):
    """
    Represents a file uploaded from the local filesystem.

    Used for uploading documents, images, or any other files directly from disk.
    Automatically detects the file name, size, and MIME type when not explicitly provided.

    Example:
        ```python
        file = FSInputFile("path/to/file.zip")
        await bot.send_document(chat_id="...", file=file)
        ```
    """

    def __init__(
        self,
        path: str | Path,
        file_name: str | None = None,
        file_size: int | None = None,
        mime_type: str | None = None,
        **kwargs,
    ):
        """
        Initializes an `FSInputFile` instance from a local file.

        If not provided, `file_name`, `file_size`, and `mime_type` are automatically detected:

        - `file_name` is extracted from the file path.
        - `file_size` is determined via `os.path.getsize()`.
        - `mime_type` is detected from the first 2048 bytes of the file content (using `python-magic` if available).

        Args:
            path (str | Path): Path to the local file.
            file_name (str, optional): File name to be propagated in the upload.
            file_size (int, optional): File size in bytes.
            mime_type (str, optional): File MIME type.
        """

        if "filename" in kwargs:
            warnings.warn(
                "'filename' is deprecated; use 'file_name' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            file_name = file_name or kwargs.pop("filename")

        if "mimetype" in kwargs:
            warnings.warn(
                "'mimetype' is deprecated; use 'mime_type' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            mime_type = mime_type or kwargs.pop("mimetype")

        if file_name is None:
            file_name = os.path.basename(path)
        if not file_name:
            raise ValueError(f"Cannot determine file name from path: {path}")

        if file_size is None:
            file_size = os.path.getsize(path)

        if mime_type is None:
            with open(path, "rb") as f:
                head = f.read(2048)
                mime_type = detect_mime_type(head, file_name)

        super().__init__(file_name=file_name, file_size=file_size, mime_type=mime_type)

        self.path = path

    async def read(self):
        """
        Asynchronously reads the file content from the local filesystem.

        Returns:
            bytes: The file content as raw bytes.
        """
        async with aiofiles.open(self.path, "rb") as f:
            return await f.read()

    def clone(self) -> FSInputFile:
        """
        Creates a clone of the current `FSInputFile` instance.

        Useful when the same file needs to be reused, for example, when sending preview images.
        The cloned object retains the same path, name, size, and MIME type but is a separate instance in memory.

        Returns:
            FSInputFile: A new instance of `FSInputFile` with identical properties.
        """
        return FSInputFile(
            path=self.path,
            file_name=self.file_name,
            file_size=self.file_size,
            mime_type=self.mime_type,
        )


class URLInputFile(InputFile):
    """
    Represents a file to be downloaded and uploaded from a remote URL.

    Used for uploading files from external sources (e.g., public file links, APIs).
    Automatically handles MIME type detection and file size parsing from HTTP headers.

    Example:
        ```python
        file = URLInputFile("https://example.com/file.pdf")
        await bot.send_document(chat_id="...", file=file)
        ```
    """

    def __init__(
        self,
        url: str,
        headers: Dict[str, Any] | None = None,
        file_name: str | None = None,
        file_size: int | None = None,
        mime_type: str | None = None,
        timeout: int = 30,
        verify_ssl=True,
        **kwargs,
    ):
        """
        Initializes a `URLInputFile` instance from a remote URL.

        Args:
            url (str): URL of the file to download.
            headers (Optional[Dict[str, Any]]): Optional HTTP headers for the request.
            file_name (str, optional): Optional file name to propagate in the upload.
            file_size (int, optional): Optional file size in bytes.
            mime_type (str, optional): Optional MIME type of the file.
            timeout (int): Timeout (in seconds) for the HTTP request.
        """

        if "filename" in kwargs:
            warnings.warn(
                "'filename' is deprecated; use 'file_name' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            file_name = file_name or kwargs.pop("filename")

        if "mimetype" in kwargs:
            warnings.warn(
                "'mimetype' is deprecated; use 'mime_type' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            mime_type = mime_type or kwargs.pop("mimetype")

        super().__init__(file_name=file_name, file_size=file_size, mime_type=mime_type)
        if headers is None:
            headers = {}

        self.url = url
        self.headers = headers
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        # Shared with clones: they see the content even if cloned before the download.
        self._downloaded_content: list[bytes | None] = [None]

    @property
    def _content(self) -> bytes | None:
        return self._downloaded_content[0]

    @_content.setter
    def _content(self, value: bytes | None) -> None:
        self._downloaded_content[0] = value

    async def prepare(self):
        """
        Prepares file metadata from HTTP response headers without downloading the body.

        Sends a streaming GET request and reads only the response headers:

          - MIME type from the `Content-Type` header.
          - File name from the `Content-Disposition` header or URL path.
          - File size from the `Content-Length` header.

        Note:
            `Content-Length` is only an estimate for dynamic sources (e.g. a camera
            snapshot endpoint returns a new image per request). The authoritative
            `file_size` is set by `read()` from the actual downloaded bytes.

        Raises:
            HTTPStatusError: If the server responds with an error status code.
            FileUploadError: If the file name cannot be resolved from the
                `Content-Disposition` header or the URL path.
        """
        if self._content is not None or (self.file_size is not None and self.mime_type is not None):
            self.__resolve_file_name()
            return

        async with (
            AsyncClient(
                verify=self.verify_ssl,
                headers={"User-Agent": get_user_agent(), **self.headers},
                follow_redirects=True,
            ) as client,
            client.stream("GET", self.url, headers=self.headers, timeout=self.timeout) as response,
        ):
            response.raise_for_status()

            if self.mime_type is None:
                content_type = response.headers.get("Content-Type")
                if content_type:
                    self.mime_type = content_type.split(";")[0].strip()

            if self.file_name is None:
                content_disp = response.headers.get("Content-Disposition", "")
                self.file_name = file_name_from_content_disposition(content_disp) or file_name_from_url(self.url)

            if self.file_size is None:
                content_length = response.headers.get("Content-Length")
                if content_length and content_length.isdigit():
                    self.file_size = int(content_length)

        self.__resolve_file_name()

    def __resolve_file_name(self) -> None:
        if self.file_name is None:
            self.file_name = file_name_from_url(self.url)
        if not self.file_name:
            raise FileUploadError(f"Unable to determine file name from URL: {self.url}")

    async def read(self, max_size: int | None = None):
        """
        Downloads the file content from the remote URL.

        The content is downloaded once and cached: repeated calls (and calls on
        clones) return the same bytes. After a successful download `file_size` is
        set to the actual size of the downloaded body, so the size declared to the
        server always matches the uploaded content — even for sources that return
        a new file per request.

        Args:
            max_size (int | None): Optional download limit in bytes. If the
                accumulated content exceeds it, the download is aborted and
                `FileSizeTooLargeError` is raised.

        Returns:
            bytes: File content.

        Raises:
            HTTPStatusError: If the server responds with an error status code.
            FileSizeTooLargeError: If the content exceeds `max_size`.
        """
        if self._content is not None:
            return self._content

        async with AsyncClient(
            verify=self.verify_ssl, headers={"User-Agent": get_user_agent(), **self.headers}
        ) as client:
            data = bytearray()
            async with client.stream(
                "GET",
                self.url,
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    data.extend(chunk)
                    if max_size is not None and len(data) > max_size:
                        raise FileSizeTooLargeError(actual_size=len(data), limit=max_size)

        self._content = bytes(data)
        if self.file_size != len(self._content):
            if self.file_size is not None:
                loggers.chatbot.debug(
                    f"Content-Length {self.file_size} != actual {len(self._content)} bytes, using actual size"
                )
            self.file_size = len(self._content)
        return self._content

    def clone(self) -> URLInputFile:
        """
        Creates a clone of the current `URLInputFile` instance.

        Useful when the same file needs to be reused (e.g., sending a preview).
        The cloned object retains the same URL, headers, and metadata, and shares
        the already downloaded content: no second download is performed.

        Returns:
            URLInputFile: A new instance with identical parameters.
        """
        cloned = URLInputFile(
            url=self.url,
            headers=self.headers.copy(),
            file_name=self.file_name,
            file_size=self.file_size,
            mime_type=self.mime_type,
            timeout=self.timeout,
            verify_ssl=self.verify_ssl,
        )
        cloned._downloaded_content = self._downloaded_content
        return cloned
