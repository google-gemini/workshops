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
import tempfile
from datetime import datetime
from functools import partial
from textwrap import dedent

import discord
import params
import pyparsing
import requests
from absl import app
from crewai import Agent, Crew, Task
from crewai_tools import tool
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)


def make_gemini() -> ChatGoogleGenerativeAI:
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
        model="gemini-1.5-pro",
        google_api_key=params.GOOGLE_API_KEY,
        temperature=1.0,
    ).bind(safety_settings=safety_settings)


def get_utc_offset(place_id: str) -> float:
    # Define the API endpoint
    url = "https://maps.googleapis.com/maps/api/place/details/json"

    # Define the query parameters
    data = {
        "fields": "utc_offset",
        "place_id": place_id,
        "key": params.MAPS_API_KEY,
    }

    # Make the GET request
    response = requests.get(url, params=data)

    return response.json()["result"]["utc_offset"] / 60.0


def get_lat_long_tz(place: str) -> tuple[float, float, float]:
    # Define the API endpoint
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

    # Define the query parameters
    data = {
        "fields": "place_id,geometry",
        "input": place,
        "inputtype": "textquery",
        "key": params.MAPS_API_KEY,
    }

    # Make the GET request
    response = requests.get(url, params=data)

    candidate = response.json()["candidates"][0]

    return (
        candidate["geometry"]["location"]["lat"],
        candidate["geometry"]["location"]["lng"],
        get_utc_offset(candidate["place_id"]),
    )


def get_kundali(
    name: str, birth_date: str, birth_time: str, birth_place: str, gender: str
) -> str:
    """Gets the Kundali from name, birth date, birth time, birth place, gender.

    Args:
      name (str): Name of person
      birth_date (str): Birth date of person in YYYY-MM-DD
      birth_time (str): Birth time of person in HH:MM
      birth_place (str): Birth place of person
      gender (str): Gender

    Returns:
      Kundali as JSON"""

    url = "https://astroapi-3.divineapi.com/indian-api/v2/basic-astro-details"

    headers = {"Authorization": f"Bearer {params.DIVINE_TOKEN}"}

    date = datetime.strptime(birth_date, "%Y-%m-%d")

    time = datetime.strptime(birth_time, "%H:%M")

    lat, long, tz = get_lat_long_tz(birth_place)

    data = {
        "api_key": params.DIVINE_KEY,
        "full_name": name,
        "date": birth_date,
        "year": date.year,
        "month": date.month,
        "day": date.day,
        "hour": time.hour,
        "min": time.minute,
        "sec": time.second,
        "gender": gender,
        "place": birth_place,
        "lat": lat,
        "lon": long,
        "tzone": tz,
    }

    response = requests.post(url, headers=headers, data=data)

    return response.json()["data"]


@tool("Get husband's Kundali")
def get_husband_kundali(
    name: str, birth_date: str, birth_time: str, birth_place: str
) -> str:
    """Gets the husband's Kundali given name, birth date, birth time and
    birth place.

    Args:
      name (str): Name of person
      birth_date (str): Birth date of person in YYYY-MM-DD
      birth_time (str): Birth time of person in HH:MM
      birth_place (str): Birth place of person

    Returns:
      Kundali as JSON"""

    return partial(get_kundali, gender="male")(
        name, birth_date, birth_time, birth_place
    )


@tool("Get wife's Kundali")
def get_wife_kundali(
    name: str, birth_date: str, birth_time: str, birth_place: str
) -> str:
    """Gets the wife's Kundali given name, birth date, birth time and
    birth place.

    Args:
      name (str): Name of person
      birth_date (str): Birth date of person in YYYY-MM-DD
      birth_time (str): Birth time of person in HH:MM
      birth_place (str): Birth place of person

    Returns:
      Kundali as JSON"""

    return partial(get_kundali, gender="female")(
        name, birth_date, birth_time, birth_place
    )


def report_match(query: str) -> str:
    gemini = make_gemini()

    jyotishi = Agent(
        role="Jyotish Guru (Vedic Astrologer)",
        goal=dedent(
            """\
            The Jyotish Guru aims to provide precise and insightful
            astrological guidance to individuals seeking advice on
            various life aspects. This includes helping clients find
            auspicious times for important events, understanding their
            personal and professional life paths, and offering
            remedies for astrological challenges."""
        ),
        backstory=dedent(
            """\
            Guru Devang Sharma is a highly revered Jyotish Guru with
            over 30 years of experience in Vedic astrology. Born into
            a family of renowned astrologers in Varanasi, India,
            Devang showed a keen interest in astrology from a young
            age. His grandfather, a celebrated astrologer himself,
            noticed Devang's aptitude and began mentoring him in the
            ancient art of Jyotish Shastra.

            Devang pursued formal education in Sanskrit and Vedic
            sciences, earning degrees from prestigious
            institutions. Over the years, he studied under various
            respected gurus, enhancing his knowledge and honing his
            skills. His deep understanding of the Vedas, Upanishads,
            and Puranas, combined with his practical experience, has
            made him a sought-after astrologer.

            As a Jyotish Guru, Devang has helped countless individuals
            navigate life's complexities by providing them with clear
            and actionable astrological advice. He is known for his
            compassionate approach, profound insights, and unwavering
            commitment to his clients' well-being. Devang's expertise
            covers all aspects of astrology, including natal chart
            analysis, compatibility matching (Gun Milan), Muhurat
            selection, and remedial measures.

            Now, as part of CrewAI, Guru Devang Sharma brings his vast
            knowledge and experience to a global audience. His goal is
            to help users understand their astrological charts, make
            informed decisions, and lead fulfilling lives. Whether
            it's starting a new business, planning a marriage, or
            seeking personal growth, Guru Devang is dedicated to
            guiding users with wisdom and accuracy.""",
        ),
        verbose=True,
        llm=gemini,
    )

    husband_kundali_task = Task(
        description=dedent(
            """\
            The Jyotish Guru will extract the potential husband's
            birth details from the provided information. This includes
            the potential husband's name, date of birth (in YYYY-MM-DD
            format), exact time of birth (in HH:MM format), and place
            of birth. Using this information, the Jyotish Guru will
            call the `get_kundali` tool to generate the potential
            husband's Kundali (birth chart). The expected output is a
            JSON object representing the potential husband's Kundali,
            ready for compatibility analysis.

            {query}"""
        ),
        expected_output=(
            "The expected output is a JSON object "
            "containing the potential husband's Kundali."
        ),
        agent=jyotishi,
        tools=[get_husband_kundali],
        human_input=False,
    )

    wife_kundali_task = Task(
        description=dedent(
            """\
            The Jyotish Guru will extract the potential wife's birth
            details from the provided information. This includes the
            potential wife's name, date of birth (in YYYY-MM-DD
            format), exact time of birth (in HH:MM format), and place
            of birth. Using this information, the Jyotish Guru will
            call the `get_kundali` tool to generate the potential
            wife's Kundali (birth chart). The expected output is a
            JSON object representing the potential wife's Kundali,
            ready for compatibility analysis.

            {query}"""
        ),
        expected_output=(
            "The expected output is a JSON object containing "
            "the potential wife's Kundali."
        ),
        agent=jyotishi,
        tools=[get_wife_kundali],
        human_input=False,
    )

    husband_kundali = Crew(
        agents=[jyotishi],
        tasks=[husband_kundali_task],
        verbose=2,
        memory=True,
        embedder={
            "provider": "google",
            "config": {
                "model": "models/embedding-001",
                "task_type": "retrieval_document",
                "title": "Embeddings for Embedchain",
            },
        },
    ).kickoff(inputs={"query": query})

    wife_kundali = Crew(
        agents=[jyotishi],
        tasks=[wife_kundali_task],
        verbose=2,
        memory=True,
        embedder={
            "provider": "google",
            "config": {
                "model": "models/embedding-001",
                "task_type": "retrieval_document",
                "title": "Embeddings for Embedchain",
            },
        },
    ).kickoff(inputs={"query": query})

    guna_milan = Task(
        description=dedent(
            """\
            The Jyotish Guru will take the husband's and wife's
            Kundali (birth charts) in JSON format and compute the Guna
            Milan score to determine the compatibility between the two
            individuals. Guna Milan is a traditional method in Vedic
            astrology used to match horoscopes for marriage. The task
            will process the Kundali objects and return a detailed
            compatibility result in the form of a markdown table with
            an explanation.

            Husband's Kundali:

            {husband_kundali}

            Wife's Kundali:

            {wife_kundali}"""
        ),
        expected_output=(
            "The expected output is a document containing the Guna Milan "
            "tables and extensive explanations about the compatibility."
        ),
        agent=jyotishi,
        human_input=False,
    )

    return (
        Crew(
            agents=[jyotishi],
            tasks=[guna_milan],
            verbose=2,
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
        .kickoff(
            inputs={
                "husband_kundali": husband_kundali.raw,
                "wife_kundali": wife_kundali.raw,
            }
        )
        .raw
    )


def purge_mentions(message: str):
    mentions = (
        pyparsing.Suppress("<@")
        + pyparsing.SkipTo(">", include=True).suppress()
    )
    return mentions.transform_string(message)


def main(_) -> None:
    # Define the intents
    intents = discord.Intents.default()

    # Initialize Client
    client = discord.Client(intents=intents, heartbeat_timeout=120)

    # Event listener for when the client has switched from offline to online
    @client.event
    async def on_ready():
        logging.info(f"Logged in as {client.user}")

    @client.event
    async def on_message(message):
        # Don't let the client respond to its own messages
        if message.author == client.user:
            return

        purged_content = purge_mentions(message.content)

        # Check if the client was mentioned in the message
        if (
            client.user.mentioned_in(message)
            and message.mention_everyone is False
        ):
            logging.info(purged_content)

            await message.channel.send(
                f"{message.author.mention}, ok! Generating report."
            )

            report = tempfile.NamedTemporaryFile(
                suffix=".md", mode="w", delete=False
            )

            report.write(report_match(purged_content))
            report.close()

            # Send a direct message to the author
            await message.channel.send(
                file=discord.File(report.name),
                content=f"{message.author.mention}, here's your report!",
            )

    client.run(params.DISCORD_TOKEN)


if __name__ == "__main__":
    app.run(main)
