from __future__ import annotations

import io
import re
import os
import aiofiles
from urllib.parse import urlparse, unquote
from pathlib import Path
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Optional, Union, Self
from mimetypes import guess_type
from trueconf import loggers
from httpx import AsyncClient

try:
    import magic
except ImportError:
    magic = None

if TYPE_CHECKING:
    from trueconf.client.bot import Bot


def detect_mime_type(data: bytes, file_name: str = "") -> str:
    mime_type = guess_type(file_name or "")[0]
    if not mime_type and magic:
        try:
            mime_type = magic.from_buffer(data, mime=True)
        except Exception as e:
            loggers.chatbot.debug(f"Failed to detect mime_type via magic: {e}")
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
        file_name (str | None): Name of the file to display when sending.
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
            file_name: Optional[str] = None,
            file_size: Optional[int] = None,
            mime_type: Optional[str] = None,
    ):

        self.file_name = file_name
        self.file_size = file_size
        self.mime_type = mime_type


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
            file_name: str,
            file_size: Optional[int] = None,
            mime_type: Optional[str] = None,
    ):
        """
        Initializes a file from a bytes buffer.

        Args:
            file (bytes): Raw file content in bytes.
            file_name (str): The name of the file.
            file_size (Optional[int]): Size of the file in bytes. Auto-detected if not specified.
            mime_type (Optional[str]): MIME type of the file. Auto-detected if not specified.
        """

        if file_size is None:
            file_size = len(file)
        if mime_type is None:
            mime_type = detect_mime_type(file, file_name)


        super().__init__(file_name=file_name, file_size=file_size, mime_type=mime_type)

        self.data = file

    @classmethod
    def from_file(
        cls,
        path: Union[str, Path],
        file_name: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
    ) -> BufferedInputFile:
        """
        Creates a `BufferedInputFile` from a file on disk.

        This is a convenient way to load a file into memory if it needs to be reused
        or processed before sending.

        Args:
            path (str | Path): Path to the local file.
            file_name (Optional[str]): File name to propagate. Defaults to the name extracted from path.
            file_size (Optional[int]): File size in bytes. Auto-detected if not specified.
            mime_type (Optional[str]): MIME type of the file. Auto-detected if not specified.

        Returns:
            BufferedInputFile: A new instance ready for upload.
        """
        if file_name is None:
            file_name = os.path.basename(path)
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
        path: Union[str, Path],
        file_name: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
    ):
        """
        Initializes an `FSInputFile` instance from a local file.

        If not provided, `file_name`, `file_size`, and `mime_type` are automatically detected:

        - `file_name` is extracted from the file path.
        - `file_size` is determined via `os.path.getsize()`.
        - `mime_type` is detected from the first 2048 bytes of the file content (using `python-magic` if available).

        Args:
            path (str | Path): Path to the local file.
            file_name (Optional[str]): File name to be propagated in the upload.
            file_size (Optional[int]): File size in bytes.
            mime_type (Optional[str]): File MIME type.
        """
        if file_name is None:
            file_name = os.path.basename(path)

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
        headers: Optional[Dict[str, Any]] = None,
        file_name: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initializes a `URLInputFile` instance from a remote URL.

        Args:
            url (str): URL of the file to download.
            headers (Optional[Dict[str, Any]]): Optional HTTP headers for the request.
            file_name (Optional[str]): Optional file name to propagate in the upload.
            file_size (Optional[int]): Optional file size in bytes.
            mime_type (Optional[str]): Optional MIME type of the file.
            timeout (int): Timeout (in seconds) for the HTTP request.
        """
        super().__init__(file_name=file_name, file_size=file_size, mime_type=mime_type)
        if headers is None:
            headers = {}

        self.url = url
        self.headers = headers
        self.timeout = timeout

    async def prepare(self):
        """
        Prepares file metadata by sending a HEAD request to the specified URL.

        This method attempts to detect:

          - MIME type from the `Content-Type` header.
          - File size from the `Content-Length` header.
          - File name from the `Content-Disposition` header or URL path.

        Raises:
            ValueError: If the server does not provide a valid `Content-Length`.
        """
        if self.file_size is not None and self.mime_type is not None:
            return

        async with AsyncClient() as client:
            async with client.stream("HEAD", self.url, headers=self.headers, timeout=self.timeout) as response:
                if self.mime_type is None:
                    content_type = response.headers.get("Content-Type")
                    if content_type:
                        self.mime_type = content_type.split(";")[0].strip()

                content_length = response.headers.get("Content-Length")
                if content_length and content_length.isdigit():
                    self.file_size = int(content_length)
                else:
                    raise ValueError("Server did not provide Content-Length, unable to determine file size.")

                content_disp = response.headers.get("Content-Disposition", "")
                self.file_name = (
                        file_name_from_content_disposition(content_disp)
                        or file_name_from_url(self.url)
                )
        return

    async def read(self):
        """
        Downloads the file content from the remote URL.

        Performs a full GET request and returns the content as raw bytes.

        Returns:
            bytes: File content.
        """
        async with AsyncClient() as client:
            data = bytearray()
            async with client.stream(
                    "GET",
                    self.url,
                    headers=self.headers,
                    timeout=self.timeout,
                    follow_redirects=True,
            ) as response:
                async for chunk in response.aiter_bytes():
                    data.extend(chunk)
        return bytes(data)

    def clone(self) -> URLInputFile:
        """
        Creates a clone of the current `URLInputFile` instance.

        Useful when the same file needs to be reused (e.g., sending a preview).
        The cloned object retains the same URL, headers, and metadata.

        Returns:
            URLInputFile: A new instance with identical parameters.
        """
        return URLInputFile(
            url=self.url,
            headers=self.headers.copy(),
            file_name=self.file_name,
            timeout=self.timeout,
        )

