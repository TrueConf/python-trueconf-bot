from __future__ import annotations
from dataclasses import dataclass
from trueconf.client.context_controller import BoundToBot
from pathlib import Path

@dataclass
class Sticker(BoundToBot):
    """
    Represents a sticker file attached to a message.

    This class provides access to file metadata and utility methods such as downloading and preview access.

    Attributes:
        file_id (str): Unique identifier of the sticker file.
        file_name (str): Name of the file as stored on the server.
        file_size (int): Size of the file in bytes.
        mimetype (str): MIME type of the sticker.
    """

    file_id: str
    file_name: str
    file_size: int
    mimetype: str

    @property
    async def url(self) -> str:
        """
        Returns the direct download URL of the sticker file.

        Source: https://trueconf.com/docs/chatbot-connector/en/files/#retrieving-file-information-and-downloading-the-file

        Returns:
            str: A URL pointing to the original sticker file.
        """

        r = await self.bot.get_file_info(self.file_id)
        return r.download_url

    @property
    async def preview_url(self) -> str:
        """
        Returns the preview URL of the sticker file, if available.

        Source: https://trueconf.com/docs/chatbot-connector/en/files/#retrieving-file-information-and-downloading-the-file

        Returns:
            str: A URL pointing to the preview version of the sticker file.
        """

        r = await self.bot.get_file_info(self.file_id)
        return r.preview.download_url

    async def download(self, dest_path: str) -> Path | None:
        """
        Shortcut for the `download_file_by_id` method of the bot instance.

        Automatically fills the following attributes:
            - `file_id`

        Use this method to download the current file by its ID.

        Args:
            dest_path (str): Destination path to save the file.
                If not specified, a temporary file will be created using
                `NamedTemporaryFile(prefix="tc_dl_", suffix=file_name, delete=False)`.

        Returns:
            Path | None: Path to the downloaded file, or None if the download failed.
        """
        return await self.bot.download_file_by_id(file_id=self.file_id, dest_path=dest_path)
