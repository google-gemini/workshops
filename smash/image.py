# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
from textwrap import dedent
from typing import Optional

import pytesseract
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from PIL import Image
from pydantic import BaseModel


def preprocess_screenshot(screenshot_path: str) -> dict:
    """
    Perform OCR on the screenshot and prepare inputs for the LLM.

    Args:
        screenshot_path (str): Path to the screenshot file.

    Returns:
        dict: A dictionary containing extracted text and base64 image data.
    """
    # Extract text using OCR
    image = Image.open(screenshot_path)
    extracted_text = pytesseract.image_to_string(image)

    # Encode image as base64
    with open(screenshot_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    return {"extracted_text": extracted_text, "image_data": image_data}


class ScreenshotOutput(BaseModel):
    description: str  # Text description or analysis
    screenshot_path: Optional[str] = None  # Path to the saved screenshot
    image_data: Optional[bytes] = None  # Raw image data (optional for inline embedding)


def process_image(query: str, screenshot_path: str, additional_context: str = "") -> str:
    """
    Process an image and optionally combine it with additional context to generate a description.

    Args:
        query (str): The user's original query.
        screenshot_path (str): Path to the screenshot.
        additional_context (str): Optional additional text context (e.g., extracted webpage text).

    Returns:
        str: A description of the image, optionally enriched with additional context.
    """
    # Preprocess screenshot to extract text and encode the image
    screenshot_data = preprocess_screenshot(screenshot_path)

    # Prepare the prompt templates
    system_message = SystemMessagePromptTemplate.from_template(
        dedent(
            """\
            You are an AI tasked with analyzing images and optional context
            to answer user queries effectively.

            Your role is to:
            1. Analyze the provided image for relevant details.
            2. Combine any additional provided context to enhance your response.
            3. Answer the user's query based on all available data.
            """
        )
    )

    human_message = HumanMessagePromptTemplate(
        prompt=[
            PromptTemplate(
                template=(
                    dedent(
                        """\
                The user's query is: "{query}".

                {additional_context}

                You are provided with an image representing the current state.

                Based on this information:
                1. Describe the content of the image.
                2. Respond specifically to the query using any relevant details.
                """
                    )
                )
            ),
            ImagePromptTemplate(
                input_variables=["image_data"],
                template={"url": "data:image/png;base64,{image_data}"},
            ),
        ]
    )

    # Instantiate the multi-modal model
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.8,
        top_p=0.9,
        frequency_penalty=0.25,
        presence_penalty=0.4,
    )

    # Prepare the chain
    prompt = ChatPromptTemplate.from_messages([system_message, human_message]).partial(
        query=query, additional_context=additional_context
    )
    chain = {"image_data": RunnablePassthrough()} | prompt | model
    return chain.invoke(screenshot_data["image_data"]).content
