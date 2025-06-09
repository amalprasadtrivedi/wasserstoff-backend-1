import os
from openai import OpenAI
from typing import List


from dotenv import load_dotenv
load_dotenv()


# Load API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError("Please set the GROQ_API_KEY environment variable.")

# Initialize Groq-compatible client
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"  # Groq's OpenAI-compatible endpoint
)

LLM_MODEL = "llama3-8b-8192"  # or try "llama2-70b-4096"

def generate_answer(question: str, context: str) -> str:
    """Uses Groq LLM to generate an answer for a document chunk."""
    prompt = f"""
You are a helpful AI assistant. Given the following context, answer the user's question.
Context:
\"\"\"
{context}
\"\"\"

Question: {question}
Answer:
    """
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error during LLM answer generation: {e}]"


def summarize_themes(question: str, all_answers: List[str]) -> str:
    """Combines answers and uses Groq to summarize themes."""
    combined = "\n\n".join([f"- {a}" for a in all_answers])

    prompt = f"""
You are a summarization assistant. Your task is to identify common themes from the following answers to a user question.

User Question: {question}

Answers:
{combined}

Please provide a concise theme-based summary:
    """
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error during theme summarization: {e}]"
