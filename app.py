import csv
import requests
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth1Session
import os
import json
import re
import time

consumer_key = ["YOUR KEY"]
consumer_secret = ["YOUR SECRET KEY"]
request_token_url = "https://api.twitter.com/oauth/request_token"
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

try:
	fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
	print(
		"There may have been an issue with the consumer_key or consumer_secret you entered."
	)

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")
print("Got OAuth token: %s" % resource_owner_key)

# Get authorization
base_authorization_url = "https://api.twitter.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)
print("Please go here and authorize: %s" % authorization_url)
verifier = input("Paste the PIN here: ")

# Get the access token
access_token_url = "https://api.twitter.com/oauth/access_token"
oauth = OAuth1Session(
	consumer_key,
	client_secret=consumer_secret,
	resource_owner_key=resource_owner_key,
	resource_owner_secret=resource_owner_secret,
	verifier=verifier,
)
oauth_tokens = oauth.fetch_access_token(access_token_url)
access_token = oauth_tokens["oauth_token"]
access_token_secret = oauth_tokens["oauth_token_secret"]

# Make the request
oauth = OAuth1Session(
	consumer_key,
	client_secret=consumer_secret,
	resource_owner_key=access_token,
	resource_owner_secret=access_token_secret,
)

# Set the directory you want to list the files from
directory = '.'

# Use os.listdir() to get a list of the files in the directory
files = os.listdir(directory)

# Loop through the list of files
for csv_file in files:
	if csv_file.endswith('.csv'):
		# Open the CSV file and create a reader object
		with open(csv_file, 'r') as file:
			reader = csv.reader(file)

			# Create a list to hold the updated rows
			updated_rows = []

			# Loop through the rows in the file
			for row in reader:
				# Only change the data in the 13th column if it meets a certain condition
				try:
					url = row["ROW NUMBER WITH TWITTER LINK"]
					print(f" URL: {url}")
					ids = re.search(r"/status/(.*?)\?", url)
					if ids:
						id = ids.group(1)
						print(f" Id: {id}")
					else:
						ids = re.search(r"/status/(.*)", url)
						if ids:
							id = ids.group(1)
							print(f" Id: {id}")
						else:
							id = "NULL"
							print("No luck brother.")
					params = {"ids": id, "tweet.fields": "text"}
					response = oauth.get("https://api.twitter.com/2/tweets", params=params)
					print(f" Response: {response}")
					json_response = response.json()
					# print(f"Json Response {json_response}")
					row["COLUMN WHERE YOU PRINT TWITTER TEXT"] = json_response["data"][0]["text"]
					print(f"Inserted Row: {row[COLUMN]}")
				except Exception:
					print(f"This url failed: {url}")
					row["COLUMN WHERE YOU PRINT TWITTER TEXT"] = "NULL"
					pass
				# Add the updated row to the list
				updated_rows.append(row)
				# Write the updated rows to the same file
			with open(csv_file, 'w') as file:
				writer = csv.writer(file)
				writer.writerows(updated_rows)
			print(f"Finished update {csv_file}")
			time.sleep(300)
	
print("Done!")
