from torch_hub import is_portrait


def image_orientation():
    print("Testing image orientation")

    print("Testing file BRIT240602.jpg")
    test_is_portrait = is_portrait("./tests/imgs/BRIT240602.jpg")
    print(f'Image orientation : {"Portrait" if test_is_portrait else "Landscape"}!')

    print("Testing file BRIT240602Landscape.png")
    test_is_portrait = is_portrait("./tests/imgs/BRIT240602Landscape.png")
    print(f'Image orientation : {"Portrait" if test_is_portrait else "Landscape"}!')


if __name__ == "__main__":
    image_orientation()
