---
title: Working with files
icon:
---

# Working with Files

{{product_chatbot}} does not impose any restrictions on uploading files to the
server. However, starting from version {{product_server}} 5.5.2 and above, the
administrator can set limits on the maximum file size and allowable formats
(extensions).

The **{{product_name}}** library offers convenient tools for file handling, both
for sending and uploading. To send a file, use one of the InputFile subclasses,
depending on the data source.

Three built-in classes are available for file transfer:

- FSInputFile — uploading a file from the local file system
- BufferedInputFile — loading from a byte buffer
- URLInputFile — uploading a file from a remote URL

All classes are located in the [trueconf.types](../reference/Types.md) module.

You can use these classes in methods:

- bot.send_document(...)
- bot.send_photo(...)
- bot.send_sticker(...)

## How to send a file?

### 🗂️ FSInputFile

It is used for uploading files from the local file system. It is recommended to
use this when you have a file path.

```python
from trueconf.types import FSInputFile

await bot.send_document(
    chat_id="a1b2c3d4",
    file=FSInputFile("docs/report.pdf"),
    caption="📄 Annual report for **2025**",
    parse_mode=ParseMode.MARKDOWN
)

await bot.send_sticker(
    chat_id="a1b2c3d4",
    file=FSInputFile("stickers/cat.webp")
)
```

### 🧠 BufferedInputFile

Used when the file is already in memory (for example, received from an API,
loaded into RAM, or from a database).

```python
from trueconf.types import BufferedInputFile

image_bytes = open("image.jpg", "rb").read()
preview_bytes = open("preview.jpg", "rb").read()

await bot.send_photo(
    chat_id="a1b2c3d4",
    file=BufferedInputFile(
        file=image_bytes,
        filename="image.jpg"
    ),
    preview=BufferedInputFile(
        file=preview_bytes,
        filename="preview.jpg"
    ),
    caption="This is my photo"
)
```

The convenient method `from_file()` is also available:

```python
file = BufferedInputFile.from_file("archive.zip")
await bot.send_document(chat_id="...", file=file)
```

### 🌐 URLInputFile

If the file is available online, you can provide a link, and the bot will
download it automatically.

```python
from trueconf.types import URLInputFile

file = URLInputFile(
    url="https://example.com/image.png",
    filename="image.png",  # optional — it will be determined automatically
)
```

### Recommendations

- **MIME type**: determined automatically. If the
[python-magic](https://pypi.org/project/python-magic) package is installed,
the MIME type will be calculated based on the file's content (bytes), which is
significantly more accurate than determining it by extension. Install it with
dependencies as follows:

```shell
pip install python-trueconf-bot[python-magic]
```

- **clone()**: each file type supports the `.clone()` method, which creates a new
copy of the object with a different `id(object)`.

## How to download a file?

To easily download incoming media files, such as images (`message.photo`) or
documents (`message.document`), the library provides the shortcut method
`.download()`. This is syntactic sugar over the `bot.download_file_by_id(...)`
method, simplifying the handling of attachments.

It is recommended to use `.download()` because it:

- automatically retrieves file_id from the object;
- uses the current bot instance;
- minimizes the amount of code.

```python
@router.message(F.document)
async def handle_doc(msg: Message):
    await msg.document.download(dest_path="document.pdf")
```

!!! Notes The `dest_path` can be either relative or absolute.

The method `download_file_by_id(...)` is also available for more flexible control:

```python
await bot.download_file_by_id(
    file_id=msg.document.file_id, 
    dest_path="document.pdf"
)
```
