# base imports
import argparse
import json
import urllib.request
from io import BytesIO
from subprocess import check_output

# Tesseract imports
import pytesseract
from PIL import Image

# selenium imports
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

driver = None
url = 'https://sutramiteconsular.maec.es/'
captcha_image_path = 'captcha.png'


def argparser():
    argparser = argparse.ArgumentParser(description="Spanish Consular Procedure")
    argparser.add_argument('-p', '--path', dest='path', type=str, help = 'Captcha file path')
    argparser.add_argument('-i', '--identifier', dest='identifier', type=str, help = 'Consular Procedure Identifier')
    argparser.add_argument('-b', '--birthday', dest='birthday', type=int, help = 'Year Of Birth')
    argparser.add_argument('-e', '--email', dest='email', type=str, help = 'Email where you want to receive notifications when the Spanish Consular Procedure status changes')
    return argparser.parse_args()


def get_captcha_image():
    print("Getting Catpcha Image")

    captcha_image_element = driver.find_element_by_id('imagenCaptcha')
    location = captcha_image_element.location
    size = captcha_image_element.size
    captcha_image = driver.get_screenshot_as_png()

    img = Image.open(BytesIO(captcha_image))

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']


    img = img.crop((left, top, right, bottom)) # defines crop points
    img.save(captcha_image_path) # saves new cropped image


def resolve_captcha():
    print("Resampling the Image")
    check_output(['convert', captcha_image_path, '-resample', '600', captcha_image_path])

    print('Resolving Captcha')
    return pytesseract.image_to_string(Image.open(captcha_image_path))


def fill_form(identifier, birthday):
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
        print('Extracted Text {0}'.format(captcha_text))
    except Exception as identifier:
        print('\nAn error accur while resolving captcha. Exception was: {0}'.format(str(e)))
        driver.quit()
        raise e

    captcha_input = driver.find_element_by_id('imgcaptcha')
    captcha_input.clear()
    captcha_input.send_keys(captcha_text)

    print('Form Filled\n')


def send_notification(status_title, status, email):
    driver.save_screenshot('current_status_screenshot.png')

    email_subject = "Spanish Consular Procedure status"
    email_body = "Your Spanish Consular Procedure status has change. Now is {0} {1}".format(status_title, status)

    # send email

    with open("last_status.json", "w") as last_status_file:
        json.dump({
            'status_title': status_title,
            'status': status
        }, last_status_file, indent=4)


def check_status(email):
    status_title = driver.find_element_by_id('ctl00_ContentPlaceHolderConsulta_TituloEstado').text
    status = driver.find_element_by_id('ctl00_ContentPlaceHolderConsulta_DescEstado').text

    try:
        with open("last_status.json", "r") as last_status_file:
            last_status_dict = json.load(last_status_file)

        if last_status_dict['status_title'] != status_title or last_status_dict['status'] != status:
            send_notification(status_title, status, email)
    except FileNotFoundError:
        send_notification(status_title, status, email)


def main():
    args = argparser()

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
        identifier = args.identifier
        birthday = args.birthday
        fill_form(identifier, birthday)
    except Exception as e:
        print('An error accur while filling form. Exception was: {0}'.format(str(e)))
        driver.quit()
        raise e

    driver.find_element_by_id('imgVerSuTramite').click()

    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'aspnetForm')))
    except WebDriverException as e:
        print("We couldn't open the status of your consular procedure: {0}. Exception was: {1}".format(e.msg, type(e).__name__))
        driver.quit()
        raise e

    try:
        email = args.email
        check_status(email)
    except Exception as e:
        print('\nAn error accur while checking consular procedure status. Exception was: {0}'.format(str(e)))
        driver.quit()
        raise e

    driver.quit()


if __name__ == '__main__':
    main()
