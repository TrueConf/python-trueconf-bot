from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path

from trueconf.client.context_controller import BoundToBot


@dataclass
class Video(BoundToBot):
    """
    Represents a video file attached to a message.

    This class provides access to file metadata and utility methods such as downloading and preview access.

    Attributes:
        file_id (str): Unique identifier of the video file.
        file_name (str): Name of the file as stored on the server.
        file_size (int): Size of the file in bytes.
        mime_type (str): MIME type of the video.
    """

    file_id: str
    file_name: str
    file_size: int
    mime_type: str

    @property
    def mimetype(self) -> str:
        warnings.warn(
            "mimetype is deprecated; use mime_type instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.mime_type

    @property
    async def url(self) -> str:
        """
        Returns the direct download URL of the video file.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#getFileInfo

        Returns:
            str: A URL pointing to the original video file.
        """

        r = await self.bot.get_file_info(self.file_id)
        return r.download_url

    @property
    async def preview_url(self) -> str:
        """
        Returns the preview URL of the video file, if available.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#getFileInfo

        Returns:
            str: A URL pointing to the preview version of the video file.
        """

        r = await self.bot.get_file_info(self.file_id)
        return r.previews.download_url

    async def download(
        self,
        dest_path: str | Path | None = None,
        *,
        file_path: str | Path | None = None,
    ) -> bytes | Path | None:
        """
        Shortcut for the `download_file_by_id` method of the bot instance.

        Automatically fills the following attributes:
            - `file_id`

        Use this method to download the current file by its ID.

        Args:
            dest_path (str | Path, optional): Deprecated destination directory.
            file_path (str | Path, optional): Exact path where the file should be saved.
                If neither path is specified, the file content is returned as bytes.

        Returns:
            bytes | Path | None: File content, saved path, or None if the download failed.
        """
        return await self.bot.download_file_by_id(file_id=self.file_id, dest_path=dest_path, file_path=file_path)
