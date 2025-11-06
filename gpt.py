import json
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint="https://job-recruiting-bot.openai.azure.com/",
    api_version="2024-02-15-preview"
)

def parse_resume_with_ai(resume_text: str):
    """
    Uses Azure GPT-5-mini to extract structured resume information.
    Returns a dictionary with: name, role, phone, email, linkedin_url, address.
    """

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty. Cannot parse.")

    prompt = f"""
    Extract the following information from the provided resume text and return ONLY valid JSON:
    - name
    - role (job title/designation)
    - phone
    - email
    - linkedin_url
    - address

    Resume Text:
    {resume_text}

    Rules:
    - Return strictly in JSON format, no extra text or explanation.
    - If any field is missing, return it with an empty string.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise and reliable resume parser. "
                        "Always return a valid JSON object with keys: "
                        "name, role, phone, email, linkedin_url, address."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        # Extract content safely
        message_content = response.choices[0].message.content if response.choices else None

        if not message_content:
            raise ValueError("No content returned from model.")

        # Try parsing JSON
        parsed_data = json.loads(message_content)

        # Ensure all keys exist
        for key in ["name", "role", "phone", "email", "linkedin_url", "address"]:
            parsed_data[key] = parsed_data.get(key, "").strip() if parsed_data.get(key) else ""

        return parsed_data

    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned invalid JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Error during resume parsing: {e}")



