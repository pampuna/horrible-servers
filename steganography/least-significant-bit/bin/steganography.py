from PIL import Image
from os.path import splitext

class Steganography:
    @staticmethod
    def get_target_path_for_agent(source_image: str, id: str) -> str:
        (name, ext) = splitext(source_image)
        return f".{name}-{id}{ext}"

    @staticmethod
    def embed_data_into_image(id: str, source_image: str, encoded_data: str):
        payload_length = len(encoded_data)
        length_binary = format(payload_length, '032b')
        separator = "±"
        encoded_data = length_binary + ''.join(format(ord(c), '08b') for c in separator) + ''.join(format(ord(c), '08b') for c in encoded_data)
        image = Image.open(source_image.lstrip('/'))
        pixels = image.load()
        max_data_size = image.width * image.height * 3
        if (len(length_binary) + len(encoded_data)) > max_data_size:
            print("Error: Image is too small to hide the data.")
            exit()

        data_index = 0
        for y in range(image.height):
            for x in range(image.width):
                if data_index < len(encoded_data):
                    pixel = list(pixels[x, y])
                    for i in range(3):
                        if data_index < len(encoded_data):
                            pixel[i] = (pixel[i] & ~1) | int(encoded_data[data_index])
                            data_index += 1
                    pixels[x, y] = tuple(pixel)
        output_image = Steganography.get_target_path_for_agent(source_image, id)
        image.save(output_image, 'PNG')
        return f"/{output_image.lstrip('./')}"