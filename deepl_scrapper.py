import logging
import time
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service
from urllib.parse import quote
from webdriver_manager.chrome import ChromeDriverManager


class DeepLScrapper:
    """
        A web scrapper for the DeepL translation service using Selenium.

        This class allows you to translate texts from one language to another using the DeepL translation service.
        It utilizes the Selenium WebDriver with a headless Chrome browser to interact with the DeepL website.

        Args:
            rate_limit_delay (int, optional): The delay in seconds between retries when rate-limited by DeepL. Default is 10.

        Attributes:
            RATE_LIMIT_DELAY (int): The delay in seconds between retries when rate-limited by DeepL.
            cache (dict): A dictionary to cache translation results to avoid redundant requests.
            driver (webdriver.Chrome): The WebDriver instance for controlling the headless Chrome browser.

        Note:
            - Language detection (auto-detection) is not supported in this version. Please provide the source language.
            - The 'fake_useragent' library is used to generate a random User-Agent for browser emulation.
    """

    def __init__(self, source, target, rate_limit_delay=10):
        self.RATE_LIMIT_DELAY = rate_limit_delay
        self.cache = {}
        self.source = source
        self.target = target
        self._initialize_driver()

    def _initialize_driver(self):
        ua = UserAgent()
        user_agent = ua.random
        options = Options()
        # options.add_experimental_option("detach", True)
        options.add_argument(f"user-agent={user_agent}")
        options.add_argument("--headless")
        # self.driver = webdriver.Chrome(options=options)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def translate(self, text, max_retries=3, retry_delay=1):
        if isinstance(text, str):
            return self._translate_single_text(text, max_retries, retry_delay)
        else:
            raise ValueError("Invalid 'text' parameter. It should be a string")
    
    def _translate_single_text(self, text, max_retries, retry_delay):
        retries = 0
        max_retries = 1
        while retries < max_retries:
            try:
                encoded_text = quote(text, safe='')
                url = f'https://www.deepl.com/translator#{self.source}/{self.target}/{encoded_text}'
                self.driver.get(url)

                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'sentence_highlight')))
                
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@aria-labelledby='translation-target-heading']//p//span")
                        )
                    )

                translations = self.driver.find_elements(By.XPATH, "//div[@aria-labelledby='translation-target-heading']//p//span")

                return ''.join([translation.text for translation in translations])
            except Exception as e:
                error_message = f"Translation failed for text: '{text}' with error: {e}"
                if self._is_rate_limited_error(e):
                    logging.warning(
                        f"Rate limited by DeepL. Waiting {self.RATE_LIMIT_DELAY} seconds before retrying.")
                    time.sleep(self.RATE_LIMIT_DELAY)
                else:
                    logging.error(error_message)
                    retries += 1
                    time.sleep(retry_delay)
        else:
            raise Exception("Failed to translate text after maximum retries.")

    def close(self):
        self.driver.quit()

    @staticmethod
    def _is_rate_limited_error(error):
        rate_limited_errors = ["Too many requests", "Service Temporarily Unavailable"]
        return any(message in str(error) for message in rate_limited_errors)