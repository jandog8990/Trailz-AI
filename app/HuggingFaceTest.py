from huggingface_hub import InferenceClient
import os

# setup hf client
api_key = os.environ["HUGGING_FACE_TOKEN"]
llama_model_id = os.environ["LLAMA_MODEL_ID"]
print("API key = " + str(api_key))
print("Llama Model id = " + str(llama_model_id))
client = InferenceClient(token=api_key)
messages = [
    {
        "role": "user",
        "content": "Why do wars exist?"
    }
]

#model="google/gemma-2-2b-it",
#model="meta-llama/Llama-3.1-8B-Instruct",
#model="meta-llama/Meta-Llama-3-8B-Instruct", 
stream = client.chat.completions.create(
    model=llama_model_id,
    messages=messages,
    max_tokens=500,
    stream=True
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    print(content, end="")
