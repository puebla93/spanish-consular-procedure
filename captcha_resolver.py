import pytesseract
import sys
import argparse
from PIL import Image
from subprocess import check_output

def argparser():
    argparser = argparse.ArgumentParser(description="Captcha Resolver")
	argparser.add_argument('path', help = 'Captcha file path')
	return args = argparser.parse_args()

def resolve(path):
	print("Resampling the Image")
	check_output(['convert', path, '-resample', '600', path])
	return pytesseract.image_to_string(Image.open(path))

if __name__ == "__main__":
	args = argparser()
	path = args.path

	print('Resolving Captcha')
	captcha_text = resolve(path)
	print('Extracted Text',captcha_text)
