import sys
import time
import jdatetime
import selenium.common.exceptions
from PyQt5.QtWidgets import QApplication
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from logger import setup_logging
from utils import decrypt_credentials, read_preferred_sessions, remove_json_file
from gui import *

class GymReservation:
    """
    Class to automate gym session reservations on samad.aut.ac.ir using Selenium.

    Attributes:
    - kill: Indicates the status of the application termination.
    - reserve_time: Tracks the availability of reservation slots.
    - username: Stores the username for logging into the system.
    - password: Stores the password for logging into the system.
    - output_logger: Logging setup for storing reservation results.
    - error_msg_default: Default error message when no program is defined.
    - url: URL for the website 'samad.aut.ac.ir'.
    - driver: WebDriver instance for Selenium.
    - gym_name: Name of the gym for reservation.
    - asked_days: Stores the requested days for reservations.
    - reserved_days: Tracks the days for which reservations have been made.
    """

    def __init__(self):
        """
        Initializes necessary attributes for the GymReservation class.
        """
        self.kill = None
        self.reserve_time = None
        self.username = None
        self.password = None
        self.output_logger = setup_logging('./Logs', './Logs/result.txt')
        self.error_msg_default = 'هیچ برنامه ی غذایی ای تعریف نشده است.'
        self.url = 'https://samad.aut.ac.ir'
        self.driver = None
        self.gym_name = 'مجتمع ورزشی(بدنسازی پسران) - 17'
        self.asked_days = None
        self.reserved_days = []

    def config_chrome_driver(self):
        """
        Initializes the Chrome WebDriver and options for the automation process.
        """
        service = Service(executable_path='./chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(service=service, options=options)

    def log_in(self):
        """
        Logs into the website using decrypted credentials.
        """
        self.driver.get(self.url)
        self.username, self.password = decrypt_credentials()

        username_field, password_field = self.driver.find_elements(By.CLASS_NAME, 'form-input')
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)

        login_button = self.driver.find_element(By.XPATH, '//*[@id="login_btn_submit"]')
        login_button.click()

    def gym_panel(self):
        """
        Navigates to the gym reservation panel from the main page of samad.aut.ac.ir.
        """
        food_reservation_button = self.driver.find_element(By.XPATH, '//*[@id="1_div"]/div[1]/span')
        food_reservation_button.click()
        time.sleep(2)
        select_fr = Select(self.driver.find_element(By.CSS_SELECTOR, "#selectself_selfListId"))
        select_fr.select_by_visible_text(self.gym_name)
        continue_btn = self.driver.find_element(By.XPATH, '//*[@id="generalAjaxDialogBodyDiv"]/table/tbody/tr[3]/td/input')
        continue_btn.click()

    def choose_correct_week(self):
        """
        Chooses the correct week for reservations based on the current and available dates.
        Skips to the next available week if the chosen week has passed.
        """
        table = self.driver.find_element(By.XPATH, '//*[@id="pageTD"]/table/tbody/tr[2]/td/table/tbody')
        saturday = table.find_element(By.XPATH, '//*[@id="pageTD"]/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]').text.split('\n')[1]
        saturday_date = jdatetime.datetime.strptime(saturday, "%Y/%m/%d")

        current_date = jdatetime.datetime.now()

        delta_time = current_date - saturday_date

        # if delta_time.days > 0:
        #     next_table_btn = self.driver.find_element(By.XPATH, '//*[@id="nextWeekBtn"]')
        #     next_table_btn.click()
        #     time.sleep(10)
    def check_released_or_not(self):
        """
        Checks if the reservation table has been released for the desired sessions.
        """
        self.reserve_time = False
        while not self.reserve_time:
            try:
                error_msg = self.driver.find_element(By.XPATH, '//*[@id="errorMessages"]')
                if error_msg.text == self.error_msg_default:
                    self.reserve_time = False
            except selenium.common.exceptions.NoSuchElementException:
                self.reserve_time = True
                self.output_logger.info("The new reservation table has been updated and is now available.")

    def do_reservations(self):
        """
        Performs the actual reservation process for the preferred sessions and days.
        Checks for available slots and makes reservations accordingly.
        """
        self.asked_sessions = read_preferred_sessions()
        while self.reserved_days != self.asked_days:
            self.asked_days = [day for day in self.asked_sessions.keys() if self.asked_sessions[day] != []]
            for day in self.asked_sessions.keys():
                for idx, session in enumerate(self.asked_sessions[day]):
                    before_balance = self.driver.find_element(By.ID, 'creditId').text

                    session_input = self.driver.find_element(By.XPATH, week_sessions[day][session])
                    if session_input.is_selected():
                        if day not in self.reserved_days:
                            self.output_logger.info(f"Reservation already made for {day} at {session}.")
                            self.reserved_days.append(day)
                        break

                    session_input.click()
                    confirm_btn = self.driver.find_element(By.XPATH, '//*[@id="doReservBtn"]')
                    self.driver.implicitly_wait(8)
                    confirm_btn.click()
                    after_balance = self.driver.find_element(By.ID, 'creditId').text

                    if before_balance == after_balance:
                        self.output_logger.error(f"No reservation made for {day} at {session}.")

                    else:
                        self.output_logger.info(f"Reservation has been made for {day} at {session}.")
                        self.reserved_days.append(day)
                        break
        self.output_logger.info('All preferred sessions have been successfully reserved.')
        remove_json_file('data/preferred_sessions.json')

    def check_preferred_existence(self):
        """
        Checks for the existence of preferred sessions stored in a file.
        If not available, prompts the user to input preferences.
        """
        data = read_preferred_sessions()
        if data is None:
            self.output_logger.error("Please run the application, enter your username, password, and preferred sessions.")
            self.kill = True

    def run(self):
        """
        Executes the entire automation process for gym session reservations.
        """
        self.kill = False
        self.check_preferred_existence()
        if self.kill:
            app = QApplication(sys.argv)
            login_window = LoginWindow()
            login_window.show()
            app.exec_()
            app.quit()

        self.config_chrome_driver()
        self.log_in()
        self.gym_panel()
        self.choose_correct_week()
        self.check_released_or_not()
        self.do_reservations()

a = GymReservation()
a.run()
