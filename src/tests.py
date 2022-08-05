from torch.specimens.specimens import is_portrait

def image_orientation():
    print("Testing image orientation") 

    print("Testing file BRIT240602.jpg")
    isPortrait = is_portrait("./test/BRIT240602.jpg")
    print(f'Image orientation : {"Portrait" if isPortrait else "Landscape"}!')

    print("Testing file BRIT240602Landscape.png")
    isPortrait = is_portrait("./test/BRIT240602Landscape.png")
    print(f'Image orientation : {"Portrait" if isPortrait else "Landscape"}!')

if __name__ == "__main__":
    image_orientation()