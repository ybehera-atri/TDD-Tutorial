from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time

MAX_WAIT = 5 


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element(By.ID, "id_list_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertIn(row_text, [row.text for row in rows])   

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:  
            try:
                table = self.browser.find_element(By.ID, "id_nothing")  
                rows = table.find_elements(By.TAG_NAME, "tr")
                self.assertIn(row_text, [row.text for row in rows])
                return  
            except (AssertionError, WebDriverException):  
                if time.time() - start_time > MAX_WAIT:  
                    raise  
                inputbox.send_keys(Keys.ENTER)
                self.wait_for_row_in_list_table("1: TDD Training")

                # There is still a text box inviting her to add another item.
                # She enters "Use peacock feathers to make a fly"
                # (Edith is very methodical)
                inputbox = self.browser.find_element(By.ID, "id_new_item")
                inputbox.send_keys("TDD Documentation")
                inputbox.send_keys(Keys.ENTER)

                # The page updates again, and now shows both items on her list
                self.wait_for_row_in_list_table("1: TDD Training")
                self.wait_for_row_in_list_table("2: TDD Documentation")

    def test_can_start_a_todo_list(self):
        # Edith has heard about a cool new online to-do app.
        # She goes to check out its homepage
        self.browser.get(self.live_server_url)   

        # She notices the page title and header mention to-do lists
        self.assertIn("Notes", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Notes App", header_text)

        # She is invited to enter a to-do item straight away
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        # When she hits enter, the page updates, and now the page lists
        # "1: Buy peacock feathers" as an item in a to-do list table
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # There is still a text box inviting her to add another item.
        # She enters "Use peacock feathers to make a fly"
        # (Edith is very methodical)
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        inputbox.send_keys("Read TDD Documentation")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # The page updates again, and now shows both items on her list
        self.check_for_row_in_list_table("1: TDD Training")
        self.check_for_row_in_list_table("2: Read TDD Documentation")

        # Satisfied, she goes back to sleep

