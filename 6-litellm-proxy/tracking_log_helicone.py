# https://us.helicone.ai/dashboard

import os
import litellm
from litellm import completion
from dotenv import load_dotenv
load_dotenv()

# Ensure Lunary callbacks are enabled for both success and failure
litellm.success_callback = ["helicone"]
litellm.failure_callback = ["helicone"]

# Optional: rely on environment variable LUNARY_PUBLIC_KEY being set
# If not set in your environment, uncomment and set it here (not recommended for prod)
# os.environ.setdefault("LUNARY_PUBLIC_KEY", "<your-lunary-public-key>")
os.environ.setdefault("LUNARY_PUBLIC_KEY", "4dc2fd9e-d55a-4560-a033-d2a6729e6f19")
response = completion(
    model="gemini/gemini-1.5-flash",
    messages=[{"role": "user", "content": "Hello!"}]
)

try:
    print(response["choices"][0]["message"]["content"])
except Exception:
    print(response)