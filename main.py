# base imports
import argparse

# selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import ui
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

# our imports
from captcha_resolver import resolve

def argparser():
    argparser = argparse.ArgumentParser(description="Spanish Consular Procedure")
	argparser.add_argument('path', help = 'Captcha file path')
	return args = argparser.parse_args()

def main():
    pass

if __name__ == '__main__':
    main()
