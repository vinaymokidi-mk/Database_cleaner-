"""
LLM Wrapper - Automatically detects and uses available API
"""
import os

def call_llm(prompt: str) -> str:
    """
    Call LLM using auto-detected API provider.
    Tries: Google Gemini → OpenAI → Anthropic
    """
    # Try Google Gemini first
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={"temperature": 0.3}
            )
            return response.text
        except Exception as e:
            print(f"⚠️ Gemini failed: {e}")
    
    # Try OpenAI
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ OpenAI failed: {e}")
    
    # Try Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if anthropic_key:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"⚠️ Anthropic failed: {e}")
    
    # No API available - return error
    raise ValueError(
        "❌ No LLM API configured!\n"
        "Please set one of:\n"
        "  - GEMINI_API_KEY\n"
        "  - OPENAI_API_KEY\n"
        "  - ANTHROPIC_API_KEY\n"
        "\nExample: export GEMINI_API_KEY=your_key_here"
    )


def check_api_available():
    """Check if any LLM API is configured"""
    keys = {
        "Gemini": os.getenv("GEMINI_API_KEY", ""),
        "OpenAI": os.getenv("OPENAI_API_KEY", ""),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY", "")
    }
    
    available = [name for name, key in keys.items() if key]
    
    if available:
        print(f"✅ LLM API available: {', '.join(available)}")
        return True
    else:
        print("⚠️ No LLM API configured!")
        print("Set one of: GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY")
        return False


if __name__ == "__main__":
    # Test the LLM
    if check_api_available():
        response = call_llm("Say 'Hello! API working!' in 5 words max")
        print(f"Response: {response}")



