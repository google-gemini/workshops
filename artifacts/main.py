#!/usr/bin/env python3
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

import logging
from textwrap import dedent

from absl import app
from crewai import Agent, Crew, Task

from utils.model import make_gemini
from utils.parsing import extract_fenced_code


def main(argv):
    artifactor = Agent(
        role="Web Developer/Designer",
        goal=(
            dedent(
                """
                Create self-contained, interactive HTML documents that
                embed all necessary resources, such as JavaScript,
                CSS, and images, within a single file. These documents
                should be optimized for performance, accessibility,
                and should be responsive across all devices.
                """
            )
        ),
        backstory=(
            dedent(
                """
                Developed to meet the growing demand for portable and
                self-contained web presentations and educational
                modules that can be easily distributed and used
                offline. Drawing inspiration from skilled web
                developers and designers, this agent uses its deep
                understanding of web technologies to build engaging,
                highly functional, and aesthetically pleasing web
                documents that maintain high standards of design and
                functionality while being fully self-contained. The
                agent is equipped with advanced knowledge in HTML5,
                CSS3, JavaScript, image optimization, and
                accessibility standards to ensure that each artifact
                it creates is of the highest quality.
                """
            )
        ),
        llm=make_gemini(),
    )

    artifactandum = Task(
        description=(
            dedent(
                """
                Create a fully self-contained HTML document focused on
                "{query}". The document should include all necessary
                resources embedded within the single HTML file,
                including inline CSS for styling, embedded JavaScript
                for interactivity related to "{query}", and any images
                encoded as Base64 data URIs. The artifact should
                function offline without external dependencies,
                correctly across different browsers, be responsive,
                accessible, and optimized for performance. Incorporate
                elements like interactive forms or simulations to
                demonstrate dynamic content handling relevant to
                "{query}".
                """
            )
        ),
        expected_output=(
            dedent(
                """
                A single HTML file that, when opened in any modern
                browser, displays a styled page with "{query}"-related
                interactive elements and embedded images. Ensure the
                page renders correctly on both desktop and mobile
                devices. The JavaScript should manage interactions
                specific to "{query}", such as validating inputs and
                responding to user interactions. The HTML and embedded
                resources must adhere to web standards for
                accessibility and performance.
                """
            )
        ),
        agent=artifactor,
    )

    crew = Crew(
        agents=[artifactor],
        tasks=[artifactandum],
        verbose=True,
        memory=True,
        embedder={
            "provider": "google",
            "config": {
                "model": "models/embedding-001",
                "task_type": "retrieval_document",
                "title": "Embeddings for Embedchain",
            },
        },
    )

    artifact = crew.kickoff(
        inputs={
            "query": dedent(
                """
                two-pendulum physics simulation with controls for
                length 1, length 2, mass 1, mass 2; and a button to
                reset the simulation
                """
            )
        }
    )

    logging.info(extract_fenced_code(artifact))

    artifact = crew.kickoff(
        inputs={
            "query": dedent(
                """
                same thing, but mass and length are sliders (not text
                inputs)
                """
            )
        }
    )

    logging.info(extract_fenced_code(artifact))


if __name__ == "__main__":
    app.run(main)
