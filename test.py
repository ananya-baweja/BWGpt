import ollama

try:
    response = ollama.chat(
        model='qwen3:8b',
        messages=[
            {'role': 'user', 'content': 'Say hello'}
        ]
    )

    print("✅ LLM Running")
    print(response['message']['content'])

except Exception as e:
    print("❌ LLM Not Running")
    print(e)