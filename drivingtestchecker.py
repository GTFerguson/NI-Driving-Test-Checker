from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import re
from gmailchecker import GMailChecker
from datetime import datetime
import phonehandler
from sensitive_details import PersonalDetails


# Booking variables
date_format = '%d %B %Y'
current_date = datetime.strptime('08 March 2024', date_format)


# Finds a button by id and clicks it, just makes main cleaner
def click_btn(d, btn_id):
	d.find_element(By.ID, btn_id).click()


def input_to_field(d, field, input):
	d.find_element(By.ID, field).send_keys(input)


def startup_dva_site(d):
	# Navigate to the driving test website
	d.get('https://dva-bookings.nidirect.gov.uk/MyBookings/FindDriver')
	time.sleep(1)

	pd = PersonalDetails()
	input_to_field(d, 'BookingReference', pd.booking_reference)
	input_to_field(d, 'DriverNo', pd.driver_no)
	input_to_field(d, 'dob', pd.dob)

	time.sleep(1)
	submit_button = d.find_element(By.XPATH, '//button[@type="submit"]')
	submit_button.click()


# This function compares a given date against the current booking date.
# It returns True if the date is sooner, false if not.
def is_better_date(date):
	if (date < current_date):
		return True
	else:
		return False


def submit_auth_code(d, a_code):
	input_to_field(d, 'iptValidationCode', a_code)
	submit_button = d.find_element(By.XPATH, '//button[@type="submit"]')
	time.sleep(2)
	submit_button.click()


def reserve_date():
	click_btn(d, 'bs-select-1-6')
	click_btn(d, 'group-day-0')
	
	ipt_time = None
	# Start at 2 to try and get the latest time
	ipt_time_pos = 2
	while not ipt_time:
		try:
			ipt_time = find_element(By.ID, 'group-time-' + ipt_time_str)
		except NoSuchElementException:
			--ipt_time_pos

	ipt_time.click()
	click_btn(d, 'reservebtn')


def get_gmail_auth():
	gmc = GMailChecker()
	gmc.load_creds()

	latest_email = None
	auth_code = None

	while not latest_email:
		time.sleep(4)
		print("Attempting to retrieve latest_email...")
		latest_email = gmc.get_latest_email("noreply@infrastructure-ni.gov.uk")

	auth_code = gmc.get_auth_code(latest_email[0]["id"])	
	gmc.mark_as_read(latest_email[0]["id"])
	return auth_code


if __name__ == "__main__":
	print("Program Starting...")
	# Setup our Chrome driver for Selenium
	driver_path = 'chromedriver.exe'
	service = Service(driver_path)s
	driver = webdriver.Chrome(service=service)

	startup_dva_site(driver)

	auth_code = get_gmail_auth()

	print("Submitting authorisation code.")
	submit_auth_code(driver, auth_code)
	time.sleep(1)

	click_btn(driver, 'btnChange')
	time.sleep(1)

	click_btn(driver, 'btn.dropdown-toggle.btn-default.bs-placeholder')
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
			reserve_date()
			print("Better date found, calling user...")
			call_me()
		else:
			print("Date is worse than current booking.")

	input("Press Enter to close program...")
	driver.quit()