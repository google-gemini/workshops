import google.generativeai as genai
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

    # TODO(danenberg): This became necessary at some point, for some
    # reason! No longer covered by `google_api_key` below. Regression?
    genai.configure(api_key=params.GOOGLE_API_KEY)

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=params.GOOGLE_API_KEY,
        temperature=1.0,
    ).bind(safety_settings=safety_settings)
