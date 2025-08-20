import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def create_test_image(filename="test_photo.jpg", color="red", size=(100, 100)):
    """
    Создает временное изображение и возвращает его в виде SimpleUploadedFile.

    :param filename: Имя файла (по умолчанию 'test_photo.jpg')
    :param color: Цвет фона изображения (по умолчанию 'red')
    :param size: Размер изображения (по умолчанию (100, 100))
    :return: Объект SimpleUploadedFile с временным изображением
    """
    image = Image.new("RGB", size, color)
    image_io = tempfile.NamedTemporaryFile(suffix=".jpg")
    image.save(image_io, format="JPEG")
    image_io.seek(0)
    return SimpleUploadedFile(filename, image_io.read(), content_type="image/jpeg")
