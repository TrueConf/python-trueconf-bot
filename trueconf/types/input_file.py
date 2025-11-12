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


def detect_mimetype(data: bytes, filename: str = "") -> str:
    mimetype = guess_type(filename or "")[0]
    if not mimetype and magic:
        try:
            mimetype = magic.from_buffer(data, mime=True)
        except Exception as e:
            loggers.chatbot.debug(f"Failed to detect mimetype via magic: {e}")
    return mimetype or "application/octet-stream"

def filename_from_url(url: str) -> str:
    path = urlparse(url).path
    return Path(unquote(path)).name

def filename_from_content_disposition(header: str) -> str | None:
    match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^\";]+)"?', header)
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
        filename (str | None): Name of the file to display when sending.
        file_size (int | None): File size in bytes (optional).
        mimetype (str | None): MIME type of the file. Can be detected automatically.

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
            filename: Optional[str] = None,
            file_size: Optional[int] = None,
            mimetype: Optional[str] = None,
    ):

        self.filename = filename
        self.file_size = file_size
        self.mimetype = mimetype


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
        file = BufferedInputFile(file=data_bytes, filename="example.txt")
        await bot.send_document(chat_id="...", file=file)
        ```

    Note:
        Use `BufferedInputFile.from_file(...)` for convenient file loading from disk.
    """

    def __init__(
            self,
            file: bytes,
            filename: str,
            file_size: Optional[int] = None,
            mimetype: Optional[str] = None,
    ):
        """
        Initializes a file from a bytes buffer.

        Args:
            file (bytes): Raw file content in bytes.
            filename (str): The name of the file.
            file_size (Optional[int]): Size of the file in bytes. Auto-detected if not specified.
            mimetype (Optional[str]): MIME type of the file. Auto-detected if not specified.
        """

        if file_size is None:
            file_size = len(file)
        if mimetype is None:
            mimetype = detect_mimetype(file, filename)


        super().__init__(filename=filename, file_size=file_size, mimetype=mimetype)

        self.data = file

    @classmethod
    def from_file(
        cls,
        path: Union[str, Path],
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        mimetype: Optional[str] = None,
    ) -> BufferedInputFile:
        """
        Creates a `BufferedInputFile` from a file on disk.

        This is a convenient way to load a file into memory if it needs to be reused
        or processed before sending.

        Args:
            path (str | Path): Path to the local file.
            filename (Optional[str]): File name to propagate. Defaults to the name extracted from path.
            file_size (Optional[int]): File size in bytes. Auto-detected if not specified.
            mimetype (Optional[str]): MIME type of the file. Auto-detected if not specified.

        Returns:
            BufferedInputFile: A new instance ready for upload.
        """
        if filename is None:
            filename = os.path.basename(path)
        with open(path, "rb") as f:
            data = f.read()

        if file_size is None:
            file_size = len(data)

        if mimetype is None:
            mimetype = detect_mimetype(data, filename)

        return cls(data, filename=filename, file_size=file_size, mimetype=mimetype)

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
            filename=self.filename,
            file_size=self.file_size,
            mimetype=self.mimetype,
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
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        mimetype: Optional[str] = None,
    ):
        """
        Initializes an `FSInputFile` instance from a local file.

        If not provided, `filename`, `file_size`, and `mimetype` are automatically detected:

        - `filename` is extracted from the file path.
        - `file_size` is determined via `os.path.getsize()`.
        - `mimetype` is detected from the first 2048 bytes of the file content (using `python-magic` if available).

        Args:
            path (str | Path): Path to the local file.
            filename (Optional[str]): File name to be propagated in the upload.
            file_size (Optional[int]): File size in bytes.
            mimetype (Optional[str]): File MIME type.
        """
        if filename is None:
            filename = os.path.basename(path)

        if file_size is None:
            file_size = os.path.getsize(path)

        if mimetype is None:
            with open(path, "rb") as f:
                head = f.read(2048)
                mimetype = detect_mimetype(head, filename)

        super().__init__(filename=filename, file_size=file_size, mimetype=mimetype)

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
            filename=self.filename,
            file_size=self.file_size,
            mimetype=self.mimetype,
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
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        mimetype: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initializes a `URLInputFile` instance from a remote URL.

        Args:
            url (str): URL of the file to download.
            headers (Optional[Dict[str, Any]]): Optional HTTP headers for the request.
            filename (Optional[str]): Optional file name to propagate in the upload.
            file_size (Optional[int]): Optional file size in bytes.
            mimetype (Optional[str]): Optional MIME type of the file.
            timeout (int): Timeout (in seconds) for the HTTP request.
        """
        super().__init__(filename=filename, file_size=file_size, mimetype=mimetype)
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
        if self.file_size is not None and self.mimetype is not None:
            return

        async with AsyncClient() as client:
            async with client.stream("HEAD", self.url, headers=self.headers, timeout=self.timeout) as response:
                if self.mimetype is None:
                    content_type = response.headers.get("Content-Type")
                    if content_type:
                        self.mimetype = content_type.split(";")[0].strip()

                content_length = response.headers.get("Content-Length")
                if content_length and content_length.isdigit():
                    self.file_size = int(content_length)
                else:
                    raise ValueError("Server did not provide Content-Length, unable to determine file size.")

                content_disp = response.headers.get("Content-Disposition", "")
                self.filename = (
                        filename_from_content_disposition(content_disp)
                        or filename_from_url(self.url)
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
            filename=self.filename,
            timeout=self.timeout,
        )

