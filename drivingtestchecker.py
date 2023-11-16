from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import re
from gmailchecker import GMailChecker

booking_reference = '0004881037'
driver_no = '32278727'
dob = '24-01-1995'

def startup_dva_site(d):
	# Navigate to the driving test website
	d.get('https://dva-bookings.nidirect.gov.uk/MyBookings/FindDriver')

	time.sleep(2)

	# Find and interact with the necessary elements (replace these with actual element locators)
	input_booking_reference = d.find_element(By.ID, 'BookingReference')
	input_driver_no = d.find_element(By.ID, 'DriverNo')
	input_dob = d.find_element(By.ID, 'dob')
	submit_button = d.find_element(By.XPATH, '//button[@type="submit"]')

	# Enter your login credentials and submit the form
	input_booking_reference.send_keys(booking_reference)
	input_driver_no.send_keys(driver_no)
	input_dob.send_keys(dob)

	time.sleep(2)

	submit_button.click()

def submit_auth_code(d, a_code):
	ipt_auth_code = d.find_element(By.ID, 'iptValidationCode')
	submit_button = d.find_element(By.XPATH, '//button[@type="submit"]')
	ipt_auth_code.send_keys(a_code)
	time.sleep(2)
	submit_button.click()

if __name__ == "__main__":
	print("Program Starting...")
	# Setup our Chrome driver for Selenium
	driver_path = 'chromedriver.exe'
	service = Service(driver_path)
	driver = webdriver.Chrome(service=service)

	startup_dva_site(driver)

	gmc = GMailChecker()
	gmc.load_creds()

	latest_email = None
	auth_code = None

	while not latest_email:
		time.sleep(10)
		print("Attempting to get latest_email.")
		latest_email = gmc.get_latest_email("noreply@infrastructure-ni.gov.uk")

	auth_code = gmc.get_auth_code(latest_email[0]["id"])	
	gmc.mark_as_read(latest_email[0]["id"])

	submit_auth_code(driver, auth_code)

	time.sleep(2)
	change_apt_button = driver.find_element(By.ID, 'btnChange')
	change_apt_button.click()

	time.sleep(2)

	dropdown_button = driver.find_element(By.CLASS_NAME, 'btn.dropdown-toggle.btn-default.bs-placeholder')
	dropdown_button.click()

	time.sleep(1)

	cookstown_field = driver.find_element(By.ID, 'bs-select-1-6')

	# Use a regular expression to extract the date
	date_match = re.search(r'\d+ \w+ \d{4}', cookstown_field.text)

	if date_match:
	    date = date_match.group()
	    print("Date:", date)
	else:
	    print("Date not found in the element text.")

	driver.quit()