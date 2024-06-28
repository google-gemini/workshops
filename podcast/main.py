#!/usr/bin/env python

from pathlib import Path
from pytube import YouTube
import tempfile
from googleapiclient.discovery import build
from datetime import date
import io
import json
import logging
import math
import random
from textwrap import dedent
from typing import Callable
from absl import app
from crewai import Agent, Crew, Task
from crewai_tools import tool
from google.cloud import texttospeech
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
import params
from pydub import AudioSegment
from pyparsing import (
    ParseException,
    Suppress,
    Word,
    alphanums,
    alphas,
    restOfLine,
    ZeroOrMore,
    OneOrMore,
    Optional,
)


def make_gemini() -> ChatGoogleGenerativeAI:
    """Makes a Gemini model.

    Returns:
      Gemini model.
    """
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: (HarmBlockThreshold.BLOCK_NONE),
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: (HarmBlockThreshold.BLOCK_NONE),
    }

    return ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=params.GOOGLE_API_KEY,
        temperature=1.0,
    ).bind(safety_settings=safety_settings)


def make_segment(producer: Agent) -> Task:
    """Makes a podcast segment.

    Args:
      podcaster (Agent): podcaster

    Returns:
      Podcast task
    """
    return Task(
        description=dedent(
            """\
      Given the following headlines, produce a short (2 minute) segment as a dialog between the podcasters. The dialog should be spicy and information dense, with the occasional joke.

      {article}
      """
        ),
        expected_output="Podcast segment",
        agent=producer,
    )


@tool("Get mp3 file")
def get_mp3(title: str) -> str:
    """Searches for music and returns a path to an mp3 file.

    Args:
      title (str): Song to search for

    Returns:
      Path to the mp3 file"""

    yt = YouTube(search_youtube(title)[0])
    filename = Path(tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name)
    return yt.streams.filter(only_audio=True).first().download(filename=filename)


def make_music(producer: Agent) -> Task:
    """Makes a podcast segment.

    Args:
      podcaster (Agent): podcaster

    Returns:
      Podcast task
    """
    return Task(
        description=dedent(
            """\
      We're going to record a podcast on the following headlines; can you recommend some upbeat intro music?

      {article}
      """
        ),
        expected_output="Path to mp3 with intro music",
        tools=[get_mp3],
        agent=producer,
    )


def make_intro(producer: Agent) -> Task:
    """Makes a podcast task.

    Args:
      podcaster (Agent): podcaster

    Returns:
      Podcast task
    """
    return Task(
        description=dedent(
            """\
      Make a quick round of intros between your podcasters; structure it as a light and playful dialog where they mention:

      1. Their names.
      2. The name of the podcast (something related to {topic}).
      3. That the podcast was recorded especially for {recipient}.
      4. That the podcast was recorded on {date}.

      {recipient} should feel special, like this podcast is just for them.
      """
        ),
        expected_output="Introduction",
        agent=producer,
    )


def make_dialog(dialog: list) -> str:
    return "\n".join([f"{who}: {what}" for who, what in dialog])


def db(volume: float) -> float:
    return 20 * math.log10(volume)


def random_silence(min_ms: int = 500, max_ms: int = 1000) -> AudioSegment:
    return AudioSegment.silent(duration=random.randint(min_ms, max_ms))


def parse_line(line: str) -> tuple | None:
    asterisks = Suppress(ZeroOrMore("**"))
    name = Word(alphas + " ").setResultsName("name")
    colon = Suppress(":")
    space = Suppress(ZeroOrMore(" "))
    quote = restOfLine.setResultsName("quote")

    grammar = asterisks + name + asterisks + colon + asterisks + space + quote

    try:
        parse = grammar.parseString(line)
        return parse.name, parse.quote
    except ParseException:
        return None


def record_line(voice: str, quote: str) -> AudioSegment:
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=quote)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", name=voice)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    logging.info(f'Recording "{quote}" in {voice}')

    return AudioSegment.from_file(io.BytesIO(response.audio_content), format="mp3")


def sec(seconds: int) -> int:
    return seconds * 1000


def mix_intro(intro, music):
    full_intro = music[: sec(5)]
    fade_to_low = music[sec(5) : sec(7)].fade(to_gain=db(0.1), duration=sec(2), start=0)
    low = music[sec(7) : sec(7) + len(intro)] + db(0.1)
    fade_to_full = music[sec(7) + len(intro) : sec(9) + len(intro)].fade(
        from_gain=db(0.1), duration=sec(2), start=0
    )
    full_outro = music[sec(9) + len(intro) : sec(14) + len(intro)]
    outro_fade = music[sec(14) + len(intro) : sec(16) + len(intro)].fade_out(sec(2))

    return (
        full_intro
        + fade_to_low
        + low.overlay(intro)
        + fade_to_full
        + full_outro
        + outro_fade
    )


def record_dialog(dialog):
    voices = {
        "elena": "en-US-Journey-F",
        "marcus": "en-US-Journey-D",
    }

    recording = AudioSegment.silent(duration=0)

    for line in dialog.splitlines():
        if parse := parse_line(line):
            name, quote = parse
            name = name.lower()
            if name in voices:
                recording += record_line(voices[name], quote)
                recording += random_silence()

    return recording


def denewline(line: str) -> str:
    return line.replace("\n", "")


def search_google(engine, query):
    service = build("customsearch", "v1", developerKey=params.SEARCH_API_KEY)

    return (
        service.cse()
        .list(
            q=query,
            cx=engine,
            num=10,
        )
        .execute()
    )


def search_music(query):
    return [item["link"] for item in search_google(params.SEARCH_MUSIC, query)["items"]]


def search_youtube(query):
    # Initialize the YouTube API client
    youtube = build("youtube", "v3", developerKey=params.SEARCH_API_KEY)

    # Perform a search query for music videos
    search_response = (
        youtube.search()
        .list(
            q=query,
            part="snippet",
            type="video",
            videoCategoryId="10",  # Category ID for Music
            maxResults=5,
        )
        .execute()
    )

    logging.info(search_response)

    return [
        f'https://youtube.com/watch?v={item["id"]["videoId"]}'
        for item in search_response["items"]
    ]


def search_news(query):
    from newsapi import NewsApiClient

    api = NewsApiClient(api_key=params.NEWS_API_KEY)
    results = api.get_everything(q=query)

    return "\n".join(
        [
            f'- {denewline(article["title"])}: {denewline(article["description"])}'
            for article in results["articles"]
            if article["title"]
            and article["description"]
            and article["title"] != "[Removed]"
        ][:10]
    )


def make_elena(gemini) -> Agent:
    """Makes a podcaster.

    Args:
      gemini (ChatGoogleGenerativeAI): Gemini model

    Returns:
      Podcaster
    """
    return Agent(
        role="Investigative Journalist and Tech Enthusiast",
        goal=(
            "To uncover the truth behind tech trends and innovations, presenting"
            " clear, well-researched information to the audience while"
            " challenging assumptions and pushing for transparency."
        ),
        backstory=(
            "Elena graduated with a degree in journalism from a top university"
            " and spent several years working for a major newspaper where she"
            " specialized in technology and innovation. She developed a"
            " reputation for her in-depth investigative pieces that not only"
            " reported the news but also explored the implications of"
            " technological advancements on society. Her passion for technology"
            " and commitment to truth led her to co-host the podcast, aiming to"
            " bridge the gap between tech experts and the general public."
        ),
        llm=gemini,
        verbose=True,
    )


def make_marcus(gemini) -> Agent:
    """Makes a podcaster.

    Args:
      gemini (ChatGoogleGenerativeAI): Gemini model

    Returns:
      Podcaster
    """
    return Agent(
        role="Charismatic Tech Optimist and Startup Advisor",
        goal=(
            "To inspire and educate listeners about the potential of new"
            " technologies and startups, bringing a positive spin to tech"
            " developments and encouraging entrepreneurial thinking."
        ),
        backstory=(
            "Marcus started as a software developer and quickly moved into the"
            " startup world, where he co-founded a successful app that"
            " transformed online interactions. After his startup was acquired, he"
            " became a sought-after advisor for new tech ventures. His"
            " experiences have made him a fervent advocate for tech's potential"
            " to solve real-world problems. Co-hosting the podcast allows him to"
            " share his optimism and practical insights with a broader audience."
        ),
        llm=gemini,
        verbose=True,
    )


def agent_to_string(name: str, agent: Agent) -> str:
    return dedent(
        f"""\
        Name: {name}
        Role: {agent.role}
        Goal: {agent.goal}
        Backstory: {agent.backstory}"""
    )


def make_producer(gemini):
    return Agent(
        role="Podcaster producer",
        goal="Produce a podcast by eliciting responses from your podcasters",
        backstory=(
            dedent(
                """\
          You are an expect podcast producer; you know how to elicit dialog from your podcasters on a topic.

          Here are your podcasters:

          {elena}

          {marcus}"""
            )
        ),
        llm=gemini,
        verbose=True,
    )


def main(_) -> None:
    topic = "LLMs"

    gemini = make_gemini()

    producer = make_producer(gemini)
    marcus = agent_to_string("Marcus", make_marcus(gemini))
    elena = agent_to_string("Elena", make_elena(gemini))

    headlines = search_news(topic)

    intro = Crew(agents=[producer], tasks=[make_intro(producer)], verbose=2).kickoff(
        inputs={
            "elena": elena,
            "marcus": marcus,
            "recipient": "Peter Danenberg",
            "date": date.today().strftime("%Y-%m-%d"),
            "topic": topic,
        }
    )

    segment = Crew(
        agents=[producer], tasks=[make_segment(producer)], verbose=2
    ).kickoff(
        inputs={
            "article": headlines,
            "elena": elena,
            "marcus": marcus,
        }
    )

    music = Crew(agents=[producer], tasks=[make_music(producer)], verbose=2).kickoff(
        inputs={
            "article": headlines,
            "elena": elena,
            "marcus": marcus,
        }
    )

    (
        mix_intro(record_dialog(intro), AudioSegment.from_file(music))
        + record_dialog(segment)
    ).export("podcast.mp3")


if __name__ == "__main__":
    app.run(main)
