# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import signal
import sys
from types import FrameType

from flask import Flask

from utils.logging import logger
																			 
# Define service account credentials and other parameters
SERVICE_ACCOUNT_FILE = "utils/service_account.json"  # Replace with your path
PROJECT_ID = "puplampu-inc-project01"  # Replace with your project ID
KEYRING_LOCATION = "puplampu-inc-project01/us-central1/puplampu-key-timestamp-2024/"  # Replace with your keyring location
KEY_NAME = "puplampu-timestamp-key-2024"  # Replace with your key name
BUCKET_NAME = "http-timestamp-rp-2024"
FILE_NAME = "custom-time.txt"															  


			   
				  

app = Flask(__name__)


@app.route("/")
def hello() -> str:
    # Use basic logging with custom fields
    logger.info(logField="custom-entry", arbitraryField="custom-entry")

    # https://cloud.google.com/run/docs/logging#correlate-logs
    logger.info("Child logger with trace Id.")


														
																		 

    return "Hello, World!"

  # Read content from encrypted file
  try:
    file_content = read_encrypted_file_content(BUCKET_NAME, FILE_NAME)
    message = f"\nContent of custom-time.txt:\n{file_content}"
  except Exception as e:
    message = f"\nError reading file: {e}"

def read_encrypted_file_content(bucket_name, file_name):
  """Reads the content of an encrypted file from the specified bucket."""
  client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)
  bucket = client.get_bucket(bucket_name)
  blob = bucket.blob(file_name)

  # Decrypt the content using KMS
  kms_client = kms.KeyManagementServiceClient.from_service_account_json(SERVICE_ACCOUNT_FILE)
  keyring_name = f"projects/{PROJECT_ID}/locations/{KEYRING_LOCATION}/keyRings/{KEY_NAME}"
  ciphertext = blob.download_as_string()
  plaintext = kms_client.decrypt(name=keyring_name, ciphertext=ciphertext).plaintext
  return plaintext.decode("utf-8")

	
def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")
   

																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																			 

    from utils.logging import flush
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																			 
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																			 
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																			 
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																			 
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																			 

    flush()

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
