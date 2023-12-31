from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
import re
from gmailchecker import GMailChecker
from datetime import datetime
import phonehandler
from sensitive_details import PersonalDetails

#Constants
WAIT_LIMIT = 20

# Booking variables
date_format = '%d %B %Y'
current_date = datetime.strptime('17 January 2024', date_format)

# Setup our Chrome driver for Selenium
driver_path = 'chromedriver.exe'


class DrivingTestChecker():
	# Finds a button by id and clicks it, just makes main cleaner
	def click_btn(self, d, selector, btn_id):
		wait = WebDriverWait(d, WAIT_LIMIT)
		try:
			btn = wait.until(EC.presence_of_element_located((selector, btn_id)))
			btn.click()
		except TimeoutException:
			print('Could not locate ' + btn_id)


	def input_to_field(self, d, field_id, input):
		wait = WebDriverWait(d, WAIT_LIMIT)
		try:
			ipt_field = wait.until(EC.presence_of_element_located((By.ID, field_id)))
			ipt_field.send_keys(input)
		except TimeoutException:
			print('Could not locate ' + btn_id)


	def startup_dva_site(self, d):
		# Navigate to the driving test website
		d.get('https://dva-bookings.nidirect.gov.uk/MyBookings/FindDriver')

		queue_url_start = 'https://dva.queue-it.net'
		expected_url_start = 'https://dva-bookings.nidirect.gov.uk'
		WebDriverWait(d, 1800).until(lambda driver: expected_url_start in d.current_url)

		pd = PersonalDetails()
		self.input_to_field(d, 'BookingReference', pd.booking_reference)
		self.input_to_field(d, 'DriverNo', pd.driver_no)
		self.input_to_field(d, 'dob', pd.dob)

		time.sleep(1)
		submit_button = d.find_element(By.XPATH, '//button[@type="submit"]')
		submit_button.click()


	# This function compares a given date against the current booking date.
	# It returns True if the date is sooner, false if not.
	def is_better_date(self, date):
		if (date < current_date):
			return True
		else:
			return False


	def submit_auth_code(self, d, a_code):
		self.input_to_field(d, 'iptValidationCode', a_code)
		submit_button = d.find_element(By.XPATH, '//button[@type="submit"]')
		time.sleep(2)
		submit_button.click()


	def reserve_date(self, d):
		self.click_btn(d, By.ID, 'bs-select-1-6')
		self.click_btn(d, By.ID, 'group-day-0')
		
		ipt_time = None
		# Start at 2 to try and get the latest time
		ipt_time_pos = 2
		while not ipt_time:
			try:
				ipt_time = d.find_element(By.ID, 'group-time-' + ipt_time_str)
			except NoSuchElementException:
				--ipt_time_pos

		ipt_time.click()
		click_btn(d, By.ID, 'reservebtn')


	def get_gmail_auth(self):
		gmc = GMailChecker()
		gmc.load_creds()

		latest_email = None
		auth_code = None

		while not latest_email:
			time.sleep(4)
			print("Attempting to retrieve latest email...")
			latest_email = gmc.get_latest_email("noreply@infrastructure-ni.gov.uk")

		auth_code = gmc.get_auth_code(latest_email[0]["id"])	
		gmc.mark_as_read(latest_email[0]["id"])
		return auth_code

	def start_checker(self):
		print("Program Starting...")
		service = Service(driver_path)
		driver = webdriver.Chrome(service=service)
		
		self.startup_dva_site(driver)

		auth_code = self.get_gmail_auth()

		print("Submitting authorisation code.")
		self.submit_auth_code(driver, auth_code)
		time.sleep(1)

		self.click_btn(driver, By.ID, 'btnChange')
		time.sleep(1)

		self.click_btn(driver, By.CLASS_NAME, 'btn.dropdown-toggle.btn-default.bs-placeholder')
		time.sleep(1)

		cookstown_field = driver.find_element(By.ID, 'bs-select-1-6')
		# Use a regular expression to extract the date
		date_match = re.search(r'\d+ \w+ \d{4}', cookstown_field.text)

		if not date_match:
			print("Date not found in the element text.")
		else:
			date = date_match.group()
			print("Date:", date)

			if is_better_date(datetime.strptime(date, date_format)):
				self.reserve_date(driver)
				print("Better date found, calling user...")
				call_me()
			else:
				print("Date is worse than current booking.")

		input("Press Enter to close program...")
		driver.quit()


if __name__ == '__main__':
	dtc = DrivingTestChecker()
	dtc.start_checker()