# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from sensitive_details import TwilioDetails 

# Set environment variables for your credentials
# Read more at http://twil.io/secure
t = TwilioDetails()

client = Client(t.account_sid, t.auth_token)

def call_me():
	call = client.calls.create(
		url="http://demo.twilio.com/docs/voice.xml",
		to=t.my_phone_no,
		from_=t.my_twilio_no
	)