# base imports
import argparse
import urllib.request
import pytesseract
from PIL import Image
from subprocess import check_output

# selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


driver = None
url = 'https://sutramiteconsular.maec.es/'
captcha_image_path = 'captcha.png'


def argparser():
    argparser = argparse.ArgumentParser(description="Spanish Consular Procedure")
    argparser.add_argument('-p', '--path', dest='path', type=str, help = 'Captcha file path')
    argparser.add_argument('-i', '--identifier', dest='identifier', type=str, help = 'Consular Procedure Identifier')
    argparser.add_argument('-b', '--birthday', dest='birthday', type=int, help = 'Year Of Birth')
    return argparser.parse_args()


def get_captcha_image():
    print("Getting Catpcha Image")
    captcha_image_src = driver.find_element_by_id('imagenCaptcha').get_attribute("src")
    urllib.request.urlretrieve(captcha_image_src, captcha_image_path)


def resolve_captcha():
    print("Resampling the Image")
    check_output(['convert', captcha_image_path, '-resample', '600', captcha_image_path])

    print('Resolving Captcha')
    return pytesseract.image_to_string(Image.open(captcha_image_path))


def fill_form():
    args = argparser()
    identifier = args.identifier
    birthday = args.birthday

    print('Filling Form\n')

    service_select = Select(driver.find_element_by_id('infServicio'))
    service_select.select_by_value('VISADO')

    identifier_input = driver.find_element_by_id('txIdentificador')
    identifier_input.clear()
    identifier_input.send_keys(identifier)

    birthday_input = driver.find_element_by_id('txtFechaNacimiento')
    birthday_input.clear()
    birthday_input.send_keys(birthday)

    try:
        get_captcha_image()
    except Exception as e:
        print('\nAn error accur while gettting captcha image. Exception was: {0}'.format(str(e)))
        driver.quit()
        raise e

    try:
        captcha_text = resolve_captcha()
        print('Text Extracted\n')
    except expression as identifier:
        print('\nAn error accur while resolving captcha. Exception was: {0}'.format(str(e)))
        driver.quit()
        raise e

    captcha_input = driver.find_element_by_id('imgcaptcha')
    captcha_input.clear()
    captcha_input.send_keys("789845")

    print('Form Filled\n')


def main():
    # suggested options for docker env
    options = Options()
    # just in case, disable usage of /dev/shm
    # https://developers.google.com/web/tools/puppeteer/troubleshooting#tips
    options.add_argument('--disable-dev-shm-usage')

    global driver
    driver = webdriver.Chrome(port=8000, options=options)  # or add to your PATH
    driver.set_window_size(1920, 1080)

    print("Opening sutramiteconsular url: %s" % url)
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'FormSolicitante')))
        print("url (%s) successfully opened\n" % url)
    except WebDriverException as e:
        print("We couldn't open sutramiteconsular: {0}. Exception was: {1}".format(e.msg, type(e).__name__))
        driver.quit()
        raise e

    driver.find_element_by_css_selector('a.headRounded').click()

    try:
        fill_form()
    except Exception as e:
        print('An error accur while filling form. Exception was: {0}'.format(str(e)))
        driver.quit()
        raise e

    driver.find_element_by_id('imgVerSuTramite').click()

    driver.quit()


if __name__ == '__main__':
    main()
