---
title: Работа с файлами
icon: 
---

# Работа с файлами

{{product_chatbot}} не накладывает ограничений на загрузку файлов на сервер.
Однако, начиная с версии {{product_server}} 5.5.2 и выше, администратор может настроить ограничения на максимальный размер файла и допустимые форматы (расширения).

Библиотека **{{product_name}}** предоставляет удобные средства для работы с файлами: как для отправки, так и для загрузки.
Чтобы отправить файл, используйте один из подклассов InputFile, в зависимости от источника данных.

Доступны три встроенных класса для передачи файлов:

- FSInputFile — загрузка файла с локальной файловой системы
- BufferedInputFile — загрузка из байтового буфера
- URLInputFile — загрузка файла с удалённого URL

Все классы расположены в модуле [trueconf.types](../reference/Types.md).

Вы можете использовать эти классы в методах:

- bot.send_document(...)
- bot.send_photo(...)
- bot.send_sticker(...)

## Как отправить файл?

### 🗂️ FSInputFile

Используется для загрузки файлов с локальной файловой системы. Рекомендуется использовать, когда у вас есть путь к файлу.

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

Используется, когда файл уже находится в памяти (например, получен из API, загружен в память (ОЗУ) или из базы данных).

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

Также доступен удобный метод `from_file()`:

```python
file = BufferedInputFile.from_file("archive.zip")
await bot.send_document(chat_id="...", file=file)
```

### 🌐 URLInputFile

Если файл находится в интернете, вы можете указать ссылку и бот скачает его самостоятельно.

```python
from trueconf.types import URLInputFile

file = URLInputFile(
    url="https://example.com/image.png",
    filename="image.png",  # можно опустить — будет определено автоматически
)
```

### Рекомендации

- **MIME-тип**: определяется автоматически. Если установлен пакет [python-magic](https://pypi.org/project/python-magic), MIME-тип будет вычислен по содержимому файла (байтам), что значительно точнее, чем определение по расширению.
Установите его с зависимостями так:

```shell
pip install python-trueconf-bot[python-magic]
```

- **clone()**: каждый тип файла поддерживает метод `.clone()` — он создаёт новую копию объекта с другим `id(object)`.

## Как скачать файл?

Для удобной загрузки входящих медиафайлов, таких как изображения (`message.photo`) или документы (`message.document`), 
библиотека предоставляет шорткат-метод `.download()`. 
Это синтаксический сахар над методом `bot.download_file_by_id(...)`, упрощающий работу с вложениями.

Рекомендуется использовать именно `.download()`, так как он:

- автоматически получает file_id из объекта;
- использует текущий экземпляр бота;
- минимизирует количество кода.


```python
@router.message(F.document)
async def handle_doc(msg: Message):
    await msg.document.download(dest_path="document.pdf")
```

!!! Notes
    Путь `dest_path` может быть как относительным, так и абсолютным.

Также доступен метод `download_file_by_id(...)`, если требуется более гибкий контроль:

```python
await bot.download_file_by_id(
    file_id=msg.document.file_id, 
    dest_path="document.pdf"
)
```

## Определение MIME-типа с помощью python-magic

MIME‑тип файла может определяться автоматически. В библиотеке поддерживаются два подхода:

* **По расширению файла** — работает без дополнительных зависимостей, но может быть неточным.
* **По содержимому файла (bytes)** — заметно точнее, но требует `python-magic`.

### Как это работает

Пакет `python-magic` сам по себе MIME‑типы не определяет. Это Python‑обёртка над нативной (C‑шной) библиотекой **libmagic**, которая и выполняет распознавание типа файла по содержимому.

Именно поэтому `python-magic` может не работать «из коробки» на некоторых системах: Python‑пакет устанавливается через `pip`, но системная библиотека `libmagic` должна быть установлена отдельно.

Если `libmagic` отсутствует, импорт `magic` может завершиться ошибкой вида:

* `ImportError: failed to find libmagic. Check your installation`

### Установка

Установите системные зависимости:

* **macOS (Homebrew):**

  ```bash
  brew install libmagic
  ```

* **Linux (Debian/Ubuntu):**

  ```bash
  sudo apt install libmagic1
  ```

* **Windows:**

  ```bash
  pip install python-magic-bin
  ```

Также рекомендуем ознакомиться с репозиторием [https://github.com/ahupp/python-magic](https://github.com/ahupp/python-magic).

### Примечания

* При наличии `python-magic` MIME‑тип определяется **по байтам файла**, что обычно точнее, чем определение по имени или расширению.






