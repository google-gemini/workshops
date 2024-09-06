#!/usr/bin/env python3

import logging
from datetime import datetime
from textwrap import dedent

from absl import app
from crewai import Agent, Crew, Task

from utils.model import make_gemini
from utils.news import search_news


def main(argv):
    news_summarizer = Agent(
        role="News Summarizer",
        goal=(
            dedent(
                """\
                Summarize current news articles and headlines into clear,
                concise paragraphs that provide an accurate and
                comprehensive overview of events. The summaries should
                be objective, well-structured, and highlight the most
                important information from multiple sources on a given
                topic."""
            )
        ),
        backstory=(
            dedent(
                """\
                Designed to process large volumes of news data, this
                agent was built in response to the growing demand for
                quick, reliable news summaries. Drawing from a wide
                range of reputable news sources, the agent uses its
                expertise in language processing and summarization to
                distill key facts and narratives from headlines and
                articles. It has a deep understanding of journalistic
                integrity and strives to present information that is
                balanced, accurate, and easy to read. Equipped with
                advanced natural language understanding, the agent
                ensures that every summary is both informative and
                engaging, keeping readers well-informed about current
                events in a fraction of the time."""
            )
        ),
        llm=make_gemini(),
    )

    citation_generator = Agent(
        role="Citation Manager",
        goal=(
            dedent(
                """\
                Generate accurate and properly formatted citations for
                news summaries, linking specific sentences to their
                corresponding source articles. The citations should
                follow a standardized format and include all necessary
                information, such as article title, author, publication
                date, and source URL, ensuring the summary is properly
                referenced."""
            )
        ),
        backstory=(
            dedent(
                """\
                Developed in response to the need for reliable and
                transparent sourcing of information, this agent is
                adept at tracking news articles used in a summary and
                generating corresponding citations. Drawing from
                practices in academic writing and journalism, the
                agent ensures that each summary is accompanied by
                clear and accurate references. With expertise in
                citation formats (APA, MLA, Chicago, etc.) and a deep
                understanding of web sources, the agent guarantees
                that readers can easily trace the information back to
                its original source, fostering trust and credibility
                in the summarized content."""
            )
        ),
        llm=make_gemini(),
    )

    redactor = Agent(
        role="Content Redactor",
        goal=(
            dedent(
                """\
                Redact any sentences in the summary that lack citations,
                ensuring that only well-sourced information remains.
                The agent should scan the summary for citation links,
                verify their presence, and remove any uncited content
                while maintaining the overall coherence and readability
                of the summary."""
            )
        ),
        backstory=(
            dedent(
                """\
                Created to uphold the highest standards of information
                integrity, this agent ensures that only verifiable and
                properly cited content is retained in the final
                summaries. By meticulously reviewing each sentence and
                cross-referencing it with the generated citations, the
                redactor agent removes any statements that lack clear
                sourcing. With its focus on transparency and accuracy,
                the agent contributes to creating a trustworthy and
                responsible final product, where readers can confidently
                rely on the presented information."""
            )
        ),
        llm=make_gemini(),
    )

    summarize_news = Task(
        description=(
            dedent(
                """\
                Summarize the key points from the provided news articles
                below. The summary should be concise and combine relevant
                information from all the articles, highlighting the most
                important details. Ensure that the tone is neutral, and the
                summary is well-structured, presenting the most significant
                facts clearly. Focus on delivering a few paragraphs that
                provide an accurate and informative overview of the topic.

                The articles to be summarized are included at the end
                of this prompt.  Please ensure that the summary
                reflects the facts and important themes from all
                articles without introducing personal opinions.

                --- START OF ARTICLES ---
                {articles}
                --- END OF ARTICLES ---
                """
            )
        ),
        expected_output=(
            dedent(
                """\
                A summary of a few paragraphs that captures the main points
                and facts from the provided articles. The summary should be
                clear, concise, and well-organized, combining overlapping
                information and presenting a cohesive narrative. It should
                remain neutral and avoid editorializing, focusing solely on
                the factual content from the articles.
                """
            )
        ),
        agent=news_summarizer,
    )

    generate_citations = Task(
        description=(
            dedent(
                """\
                Add citations to the provided summary by linking
                relevant sentences to their corresponding news
                articles. For each factual statement in the summary,
                identify the source article and append a properly
                formatted citation. The citation should include key
                information such as article title, author, publication
                date, source URL, and the provided access date.

                Ensure that each citation is linked to the correct
                portion of the summary and that the citations are
                placed unobtrusively, maintaining readability while
                making it clear which information comes from which
                article. The access date for the citations is provided
                below.

                The summary to be annotated, the articles to be
                referenced, and the access date are provided below.

                --- START OF SUMMARY ---
                {summary}
                --- END OF SUMMARY ---

                --- START OF ARTICLES ---
                {articles}
                --- END OF ARTICLES ---

                --- ACCESS DATE ---
                {access_date}
                """
            )
        ),
        expected_output=(
            dedent(
                """\
                A summary annotated with citations for each relevant
                factual statement. Each citation should be formatted
                with the article title, author, publication date,
                source URL, and the provided access date.  The
                citations should be linked to the correct portion of
                the summary, making it easy for the reader to trace
                statements back to their original sources while
                maintaining clarity and readability.
                """
            )
        ),
        agent=citation_generator,
    )

    redact_uncited_content = Task(
        description=(
            dedent(
                """\
                Review the provided summary and remove any sentences
                or sections that do not have corresponding
                citations. Ensure that the redacted version retains
                coherence and clarity, only eliminating content that
                lacks a citation reference.  The final output should
                be a concise, well-structured summary containing only
                the well-cited information.

                The summary with citations is provided below.

                --- START OF SUMMARY WITH CITATIONS ---
                {summary_with_citations}
                --- END OF SUMMARY WITH CITATIONS ---
                """
            )
        ),
        expected_output=(
            dedent(
                """\
                A redacted version of the summary that contains only the
                sentences or sections with citations. The redacted summary
                should be clear, concise, and maintain logical flow. Any
                uncited content should be removed, ensuring that only
                verifiable, properly sourced information remains.
                """
            )
        ),
        agent=redactor,
    )

    news = search_news("Rings of Power")

    summary = Crew(
        agents=[news_summarizer],
        tasks=[summarize_news],
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
    ).kickoff(inputs={"articles": news})

    logging.info(summary)

    citations = Crew(
        agents=[citation_generator],
        tasks=[generate_citations],
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
    ).kickoff(
        inputs={
            "summary": summary.raw,
            "articles": news,
            "access_date": datetime.today().date().isoformat(),
        }
    )

    logging.info(citations)

    redactions = Crew(
        agents=[redactor],
        tasks=[redact_uncited_content],
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
    ).kickoff(inputs={"summary_with_citations": citations.raw})

    logging.info(redactions)


if __name__ == "__main__":
    app.run(main)
