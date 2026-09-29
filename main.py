import logging
from email_fetcher import process_all_emails
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Reduce verbosity of Google API client logging
logging.getLogger('googleapiclient').setLevel(logging.WARNING)
logging.getLogger('google_auth_oauthlib').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

start_time = time.time()  # Start measuring time

if __name__ == "__main__":
    process_all_emails()

end_time = time.time()  # End measuring time
print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
