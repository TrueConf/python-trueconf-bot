import os
from io import BytesIO

from PIL import Image


def resize_image(image_path: str) -> bytes:
    MAX_SIDE = 1280
    MAX_SIZE = 300 * 1024  # 300 KB
    SUPPORTED_ORIGINAL_FORMATS = ("jpeg", "jpg", "png", "webp")

    # Получаем формат, размер, разрешение
    file_size = os.path.getsize(image_path)

    with Image.open(image_path) as img:
        width, height = img.size
        img_format = img.format.lower()
        has_alpha = "A" in img.getbands()

        # Картинка подходит без изменений
        if (
            img_format in SUPPORTED_ORIGINAL_FORMATS
            and max(width, height) <= MAX_SIDE
            and file_size <= MAX_SIZE
        ):
            return {
                "image_bytes": open(image_path, "rb").read(),
                "width": width,
                "height": height,
                "is_original": True  # не скрываем название
            }

        # --- Обработка сжатия ---
        def to_webp(img_obj: Image.Image, quality=95, max_size=None) -> bytes:
            buffer = BytesIO()
            save_args = {
                "format": "WEBP",
                "quality": quality,
                "method": 6,
                "lossless": False,
            }
            if not img_format.startswith("jpeg") and has_alpha:
                save_args["alpha_quality"] = 100
            if max_size:
                save_args["exact"] = True
                save_args["allow_mixed"] = True
                save_args["lossless"] = False
                save_args["qmin"] = 0
                save_args["qmax"] = 100
            img_obj.save(buffer, **save_args)
            return buffer.getvalue()

        # --- Ресайз до 1280 по большей стороне ---
        if max(width, height) > MAX_SIDE:
            scale = MAX_SIDE / max(width, height)
            new_size = (round(width * scale), round(height * scale))
            img = img.resize(new_size, Image.LANCZOS)
            webp_data = to_webp(img, quality=95)
        elif file_size > MAX_SIZE:
            webp_data = to_webp(img, quality=95)
        else:
            # форматы кроме jpeg/png/webp, даже если <1280 и <300KB
            webp_data = to_webp(img, quality=100)

        # Повторное перекодирование если размер > 300KB
        if len(webp_data) > MAX_SIZE:
            webp_data = to_webp(img, quality=95, max_size=MAX_SIZE)

        return webp_data

    # {
    #     "image_bytes": webp_data,
    #     "width": img.width,
    #     "height": img.height,
    #     "is_original": False  # название скрываем
    # }