'''
Parser Coding Challenge
'''
import base64
from PIL import Image
from io import BytesIO
import base64


VERY_LARGE_SIZE_BOX = 10000
FILE_PATH = 'text0.mp4'


def decode_base64(encoded_data):
    return base64.b64decode(encoded_data).decode('utf-8')


def extract_image_info(xml_string):
    images = []
    xml_lines = xml_string.splitlines()

    # read line by line searching for images
    for i in range(len(xml_lines)):
        if '<smpte:image' in xml_lines[i]:
            image = {}
            image["Name"] = xml_lines[i].split('"')[1]
            image["Type"] = xml_lines[i].split('"')[3]
            image["Content"] = xml_lines[i+1]
            images.append(image)

    return images


def export_image(metadata):
    images = extract_image_info(metadata)

    for image_data in images:
        # Decode Base64
        img_data = base64.b64decode(image_data["Content"])

        # Open the image using PIL
        image = Image.open(BytesIO(img_data))

        # Save the image to a file
        image.save(image_data["Name"] + "." + image_data["Type"], image_data["Type"])


def parser():
    with open(FILE_PATH, 'rb') as file:
        first_8_bytes = file.read(8)
        while first_8_bytes:
            first_8_bytes = file.read(8)
            size_of_box = int.from_bytes(first_8_bytes[0:4], 'big')
            name_of_box = first_8_bytes[4:8].decode('utf-8').lower()

            if name_of_box == 'moof':
                print(f'Box ID: {name_of_box} of size {size_of_box}')

            elif name_of_box == 'mfhd':
                file.seek(size_of_box - 8, 1)
                print(f'\tBox ID: {name_of_box} of size {size_of_box}')

            elif name_of_box == 'traf':
                print(f'\tBox ID: {name_of_box} of size {size_of_box}')

            elif name_of_box in ['tfhd', 'trun', 'uuid']:
                file.seek(size_of_box - 8, 1)
                print(f'\t\tBox ID: {name_of_box} of size {size_of_box}')

            elif name_of_box == 'mdat':
                if size_of_box > VERY_LARGE_SIZE_BOX:
                    counter = 0
                    remainder = 0

                    # Manage the size of the box
                    while size_of_box > VERY_LARGE_SIZE_BOX * counter + remainder: 
                        metadata = file.read(VERY_LARGE_SIZE_BOX).decode('utf-8')

                        #if metadata of image are between two VERY_LARGE_SIZE_BOX extract till the end
                        if metadata.count('smpte:image') % 2 == 0:
                            very_large_size_box_manager(metadata)
                        else:
                            while metadata.count('smpte:image') % 2 == 1:
                                metadata += file.read(1).decode('utf-8')
                                remainder += 1
                            very_large_size_box_manager(metadata)
                        counter += 1
                else:
                    metadata = file.read(size_of_box).decode('utf-8')
                    print(metadata)
                    export_image(metadata)


def very_large_size_box_manager(metadata):
    print(metadata)
    export_image(metadata)


def main():
    parser()


if __name__ == "__main__":
    main()