import pytesseract
from PIL import Image

original = Image.open('tmp/1.jpeg')
bw = original.convert("L")
print(pytesseract.image_to_string(bw))
