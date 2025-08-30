https://platform.openai.com/docs/overview
https://ai.google.dev/gemini-api/docs
https://aistudio.google.com/apikey


# Debug Emoji Cheatsheet

Use the following emojis in `print()` or logs to make debugging output easier to read:

| Emoji | Meaning              | When to use                              |
|-------|----------------------|-------------------------------------------|
| 🚀    | Start task/workflow  | When starting a function or job           |
| ⏳    | Processing/Loading   | While waiting for a model/API response    |
| 🔵    | Info                 | Print current status or general info      |
| ⚪    | Debug (Raw data)     | Print raw data, e.g. response JSON        |
| 📦    | Data (Input/Output)  | Print prompts sent or outputs received    |
| 🟢    | Success              | Step executed successfully, no errors     |
| 🟡    | Warning              | Minor issue, not critical                 |
| 🔴    | Error                | When encountering exceptions/API errors   |
| 🔑    | Key / Config         | When loading API keys or configurations   |
| ✅    | Done / Completed     | Workflow or job finished successfully     |

---

### 💡 Example

```python
print("🚀 Starting workflow...")
print("🔵 Sending request to Gemini API...")
print("⏳ Waiting for response...")
print("🟢 Response received successfully!")
print("📦 Output:", response.text)
print("✅ Workflow completed!")
