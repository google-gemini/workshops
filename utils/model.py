from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)

from . import params


def make_gemini(model: str = "gemini-1.5-pro") -> ChatGoogleGenerativeAI:
    """Makes a Gemini model.

    Returns:
      Gemini model.
    """
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: (
            HarmBlockThreshold.BLOCK_NONE
        ),
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: (
            HarmBlockThreshold.BLOCK_NONE
        ),
    }

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=params.GOOGLE_API_KEY,
        temperature=1.0,
    ).bind(safety_settings=safety_settings)
