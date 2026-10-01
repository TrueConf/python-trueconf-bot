from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from trueconf.client.context_controller import BoundToBot
from trueconf.types.content.base import AbstractEnvelopeContent


@dataclass
class Voice(BoundToBot, AbstractEnvelopeContent):
    """
    Represents a voice attached to a message.

    This class provides access to file metadata and utility methods such as downloading and preview access.

    Attributes:
        file_id (str): Unique identifier of the voice file.
        file_size (int): Size of the file in bytes.
        mime_type (str): MIME type of the voice file.
        duration (int):
    """

    file_id: str = field(metadata={"alias": "fileId"})
    file_size: int = field(metadata={"alias": "size"})
    mime_type: str = field(metadata={"alias": "mimeType"})
    duration: int

    @property
    async def url(self) -> str:
        """
        Returns the direct download URL of the voice file.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#getFileInfo

        Returns:
            str: A URL pointing to the original voice file.
        """

        r = await self.bot.get_file_info(self.file_id)
        return r.download_url

    @property
    async def preview_url(self) -> str:
        """
        Returns the preview URL of the voice file, if available.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/files/#getFileInfo

        Returns:
            str: A URL pointing to the preview version of the voice file.
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
