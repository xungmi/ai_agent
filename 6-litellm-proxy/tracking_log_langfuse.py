# langfuse_demo.py

import os
import litellm
from litellm import completion
from dotenv import load_dotenv
from langfuse.client import Langfuse

# Load environment variables
load_dotenv()

# ==== Langfuse setup ====
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")  # default to cloud
)

# === Create trace & span ===
trace = langfuse.trace(name="Gemini Completion", user_id="xung")
span = trace.span(name="call-gemini")

# === Optional: If you want to trace through LiteLLM ===
metadata = {"trace_id": trace.id, "span_id": span.id}

# === Call Gemini model ===
response = completion(
    model="gemini/gemini-1.5-flash",
    messages=[{"role": "user", "content": "Hello!"}],
    metadata=metadata  # for LiteLLM to propagate to Langfuse
)

# === End span & trace ===
try:
    content = response["choices"][0]["message"]["content"]
    span.end(output=content)
    print(content)
except Exception as e:
    span.end(output=str(e), level="ERROR")
    print(response)

trace.end()
