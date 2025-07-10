"""
Test script to check available Gemini models
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
import google.generativeai as genai

# Configure with your API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("Please set GOOGLE_API_KEY environment variable")
    exit(1)

genai.configure(api_key=api_key)

print("Available Gemini models:")
print("-" * 50)

# List all available models
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"Model: {model.name}")
        print(f"  Display name: {model.display_name}")
        print(f"  Description: {model.description}")
        print()

print("-" * 50)
print("\nTesting different model names with LangChain...")

# Test different model variations
test_models = [
    "gemini-pro",
    "gemini-1.0-pro", 
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro"
]

for model_name in test_models:
    try:
        print(f"\nTrying {model_name}...", end=" ")
        chat = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7
        )
        response = chat.invoke("Say 'Hello' in one word")
        print(f"✓ Success! Response: {response.content}")
    except Exception as e:
        print(f"✗ Failed: {str(e)[:100]}...")

print("\n\nRecommendation: Use one of the successful model names above in your code.")