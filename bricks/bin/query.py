# Copyright 2024 Google LLC
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

import params
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_vertexai import ChatVertexAI

# Initialize ChatVertexAI with your tuned model
llm = ChatVertexAI(
    model_name=params.MODEL,
    tuned_model_name=f"projects/{params.PROJECT_ID}/locations/"
    f"{params.LOCATION}/models/{params.TUNED_MODEL}",
    temperature=0.5,  # Adjust temperature based on your needs
    max_output_tokens=500,  # Adjust token limits as needed
    project=params.PROJECT_ID,
    location=params.LOCATION,  # e.g., "us-central1"
    max_retries=5,  # Retry attempts for API calls
)

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is the capital of France?"),
]

response = llm.invoke(messages)
print(response.content)
