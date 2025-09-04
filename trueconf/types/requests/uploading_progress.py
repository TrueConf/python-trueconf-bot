from __future__ import annotations
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from trueconf.client.context_controller import BoundToBot


@dataclass
class UploadingProgress(BoundToBot, DataClassDictMixin):
    """
        **Event type:** file upload progress.

        This object is received in the handler when a file is being uploaded and the upload progress is updated.

        Notes:
            This class is used as the event type in handler functions decorated with `@<router>.uploading_progress()`.

        Source:
            https://trueconf.com/docs/chatbot-connector/en/server-requests/#uploadingProgress

        Attributes:
            file_id (str): Unique identifier of the file being uploaded.
            progress (int): Number of bytes uploaded to the server.

        Examples:
            ```python
            from trueconf.types import UploadingProgress

            @<router>.uploading_progress()
            async def on_progress(event: UploadingProgress):
                print(f"File {event.file_id}: uploaded {event.progress} bytes")
            ```
    """
    file_id: str = field(metadata={"alias": "fileId"})
    progress: int
