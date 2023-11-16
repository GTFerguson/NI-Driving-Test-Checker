import os.path
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"]

class GMailChecker:

	creds = None

	def load_creds(self):
		# The file token.json stores the user's access and refresh tokens, and is
		# created automatically when the authorization flow completes for the first
		# time.
		if os.path.exists("token.json"):
			self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
		# If there are no (valid) credentials available, let the user log in.
		if not self.creds or not self.creds.valid:
			if self.creds and self.creds.expired and self.creds.refresh_token:
				self.creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
						"credentials.json", SCOPES
				)
				self.creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open("token.json", "w") as token:
				token.write(self.creds.to_json())


	# This method retrieves the latest email from a specific address.
	def get_latest_email(self, address):
		try:
			# Call the Gmail API
			service = build("gmail", "v1", credentials=self.creds)

			# List unread messages from a specific address
			response = service.users().messages().list(
				userId="me",
				q="is:unread from:" + address,
				maxResults=1,
			).execute()

			return response.get("messages", [])

		except HttpError as error: 
			# TODO: Handle errors from Gmail API.
			print(f"An error occurred: {error}")

	def get_auth_code(self, email_id):
		service = build("gmail", "v1", credentials=self.creds)
		message = service.users().messages().get(userId="me", id=email_id).execute()

		# Extract and print the email body
		body = ""
		if "parts" in message["payload"]:
			for part in message["payload"]["parts"]:
				if part["mimeType"] == "text/plain":
					body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
					# Extract the authentication code using regex
					authentication_code_match = re.search(r'<td><b>Authentication code: </b>(\d+)</td>', body)
					if authentication_code_match:
						return authentication_code_match.group(1)
					else:
						return None
					break
		elif "body" in message["payload"]:
			body = base64.urlsafe_b64decode(message["payload"]["body"]["data"]).decode("utf-8")
			# Extract the authentication code using regex
			authentication_code_match = re.search(r'<td><b>Authentication code: </b>(\d+)</td>', body)
			if authentication_code_match:
					return authentication_code_match.group(1)
			else:
					return None

	def mark_as_read(self, email_id):
		try:
			service = build("gmail", "v1", credentials=self.creds)
			# Modify the "labelIds" property to remove the "UNREAD" label
			modified_labels = {"removeLabelIds": ["UNREAD"]}
			# Modify the message using the "modify" method
			service.users().messages().modify(userId="me", id=email_id, body=modified_labels).execute()

		except HttpError as error:
			# TODO: Handle errors from Gmail API.
			print(f"An error occurred while marking the email as read: {error}")

if __name__ == "__main__":
	gmc = GMailChecker()
	gmc.load_creds()
	
	latest_email = gmc.get_latest_email("noreply@infrastructure-ni.gov.uk")
	
	if not latest_email:
		print("No email found.")
	else:
		# If email was found extract auth code
		auth_code = gmc.get_auth_code(latest_email[0]["id"])
		if auth_code:
			print("Authentication Code: " + auth_code)
		else:#
			print("No authorisation code found.")
		
		gmc.mark_as_read(latest_email[0]["id"])