import litellm
from litellm import completion

# Custom callback: track cost
def track_cost_callback(
    kwargs,                 # input kwargs to completion()
    completion_response,    # raw response object
    start_time, end_time    # timestamps
):
    try:
        response_cost = kwargs.get("response_cost", 0)
        model = kwargs.get("model", "unknown")
        duration = end_time - start_time

        print("\n=== Callback Info ===")
        print(f"Model       : {model}")
        print(f"Cost (USD)  : {response_cost:.6f}")
        print(f"Duration    : {duration:.2f} sec")
        print("=====================")
    except Exception as e:
        print("Callback error:", e)

# Gắn callback vào LiteLLM
litellm.success_callback = [track_cost_callback]

# Gọi completion với stream
response = completion(
    model="gemini/gemini-1.5-flash",   # đổi sang model khác nếu cần
    messages=[
        {"role": "user", "content": "Hello!"}
    ],
    stream=True
)

# In từng chunk streaming
print("=== Streaming Output ===")
for chunk in response:
    if hasattr(chunk, "choices"):
        delta = chunk.choices[0].delta
        if "content" in delta:
            print(delta["content"], end="", flush=True)
print("\n=== End of Stream ===")
