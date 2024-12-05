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

import base64
import json
import os
from pathlib import Path
from textwrap import dedent
from typing import List

import params
from absl import app, flags, logging
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

os.environ["OPENAI_API_KEY"] = params.OPENAI_API_KEY


FLAGS = flags.FLAGS
flags.DEFINE_string("mpd_dir", "./var/rendered", "MPD directory")
flags.DEFINE_string(
    "output_file",
    "./var/descriptions.json",
    "JSON file for writing descriptions",
)


# Define the Datum class
class Datum(BaseModel):
    description: str = Field(
        description="A detailed description of the build."
    )
    queries: List[str] = Field(
        description="A list of user queries relevant to the build."
    )


def generate_data():
    # Paths to rendered MPDs and PNGs
    mpd_files = list(Path(FLAGS.mpd_dir).glob("*.mpd"))

    # Initialized data
    data = {}

    for mpd_file in mpd_files:
        # Predict the PNG path based on the MPD stem
        png_file = mpd_file.with_suffix(".png")

        # Check if the PNG exists (optional, downstream could handle this)
        if png_file.exists():
            data[str(mpd_file)] = str(png_file)
        else:
            logging.error(f"PNG for {mpd_file.name} not found!")

    return data


def image_to_base64(png_file: str) -> str:
    with open(png_file, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


dune_buggy_datum = Datum(
    description=(
        dedent(
            """\
            This build is a dynamic off-road vehicle featuring
            a striking red body with a contrasting blue seat. Designed for
            adventurous terrains, it includes large, robust tires for enhanced
            traction and stability. The model is equipped with functional
            steering, allowing for realistic maneuverability. A sturdy roll bar
            adds an element of safety and adventure to the design. Front
            headlights and a tall rear antenna complete the rugged look, making
            it ideal for imaginative play in outdoor settings.
            """
        )
    ),
    queries=[
        "Build a red and blue dune buggy.",
        "Create a off-road car for wild terrains.",
        "Design a rugged vehicle for adventure scenes.",
        "Make a buggy for exploring rough trails.",
        "Craft a concept for outdoor expeditions.",
    ],
)


def prepare_prompt(example_datum: Datum) -> ChatPromptTemplate:
    parser = PydanticOutputParser(pydantic_object=Datum)
    system_message = SystemMessagePromptTemplate.from_template(
        dedent(
            """\
            You are a Model Analyst tasked with analyzing build
            concepts and generating inspiring, standalone user
            queries.

            Your task is to:

              1. Provide a detailed description of the build concept.
              2. Generate five simple, holistic user queries that
                reflect the essence of the build and encourage
                enthusiasts to create imaginative scenes or concepts.

            For example:

            {example}

            {format_instructions}
            """
        )
    )
    human_message = HumanMessagePromptTemplate(
        prompt=[
            PromptTemplate(
                template=(
                    dedent(
                        """
                        Analyze the build concept shown in the
                        attached image and generate:

                          1. A detailed description of the build.

                          2. Five simple, holistic user queries that
                             inspire the user to create this type of
                             concept.
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

    return (
        parser,
        ChatPromptTemplate.from_messages(
            [system_message, human_message]
        ).partial(
            format_instructions=parser.get_format_instructions(),
            example=example_datum.model_dump_json(),
        ),
    )


def load_descriptions(output_file: str) -> dict:
    if Path(output_file).exists():
        with open(output_file, "r") as file:
            return {
                key: Datum(**value) for key, value in json.load(file).items()
            }
    return {}


def save_descriptions(results: dict, output_file: str):
    with open(output_file, "w") as file:
        json.dump(
            {key: value.model_dump() for key, value in results.items()},
            file,
            indent=2,
        )


def main(argv):
    data = generate_data()
    descriptions = load_descriptions(FLAGS.output_file)
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.8,
        top_p=0.9,
        frequency_penalty=0.25,
        presence_penalty=0.4,
    )
    parser, prompt = prepare_prompt(dune_buggy_datum)
    for mpd, png in data.items():
        if mpd in descriptions:
            logging.info(f"{mpd} exists, not describing")
            continue
        logging.info(f"Describing {mpd=} ({png=})")
        chain = {"image_data": RunnablePassthrough()} | prompt | model | parser
        datum = chain.invoke(image_to_base64(png))
        descriptions[mpd] = datum
        logging.info(f"{mpd} → {datum}")
        save_descriptions(descriptions, FLAGS.output_file)


if __name__ == "__main__":
    app.run(main)
