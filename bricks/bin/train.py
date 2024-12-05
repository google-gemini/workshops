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

import time

import params
import vertexai
from absl import app, flags, logging
from google.cloud import storage
from google.cloud.aiplatform_v1.types import JobState
from vertexai.tuning import sft

# Define command-line flags
FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", params.PROJECT_ID, "GCP project ID")
flags.DEFINE_string(
    "location", params.LOCATION, "Region for the Vertex AI job"
)
flags.DEFINE_string(
    "bucket_region", params.BUCKET_REGION, "Region for the bucket"
)
flags.DEFINE_string("bucket_name", params.BUCKET_NAME, "Name of the bucket")
flags.DEFINE_string("examples", "./var/examples.jsonl", "Examples file")
flags.DEFINE_string("gcs_path", "examples.jsonl", "Path to training file")
flags.DEFINE_string("source_model", "gemini-1.5-pro-002", "Model to fine-tune")
flags.DEFINE_string("model", "brick-model-analyst", "Fine-tuned model name")
flags.DEFINE_bool("list", False, "List all supervised tuning jobs")
flags.DEFINE_string(
    "poll", None, "Poll a specific supervised tuning job by ID"
)
flags.DEFINE_bool("upload", False, "Upload the dataset for training")
flags.DEFINE_bool("train", False, "Kick off a supervised tuning job")

EPOCHS = 5
ADAPTER_SIZE = 4
LEARNING_RATE_MULTIPLIER = 0.8
POLL_INTERVAL = 30


def list_tuning_jobs(project_id, location):
    """Lists all supervised tuning jobs in the specified project and
    location."""
    vertexai.init(project=project_id, location=location)
    logging.info("Fetching list of supervised tuning jobs...")
    jobs = sft.SupervisedTuningJob.list()
    for job in jobs:
        logging.info(f"Resource name: {job.resource_name}")
        logging.info(f"State: {job.state}")
        logging.info(f"Created: {job.create_time}")
        logging.info("")


TERMINAL_STATES = {
    JobState.JOB_STATE_SUCCEEDED,
    JobState.JOB_STATE_FAILED,
    JobState.JOB_STATE_CANCELLED,
    JobState.JOB_STATE_EXPIRED,
    JobState.JOB_STATE_PARTIALLY_SUCCEEDED,
}


def poll_tuning_job(project_id, location, tuning_job_id):
    """Polls the state of a supervised tuning job and prints statistics."""
    vertexai.init(project=project_id, location=location)
    tuning_job = sft.SupervisedTuningJob(
        f"projects/{project_id}/locations/{location}/tuningJobs/{tuning_job_id}"
    )
    monitoring_url = (
        f"https://console.cloud.google.com/vertex-ai/generative/"
        f"language/locations/{location}/tuning/tuningJob/{tuning_job_id}"
    )
    logging.info(f"Polling SFT tuning job: {tuning_job.resource_name}")
    logging.info(f"Endpoint: {tuning_job.tuned_model_endpoint_name}")
    logging.info(f"Model name: {tuning_job.tuned_model_name}")
    logging.info(f"Monitor the job at: {monitoring_url}\n")

    while True:
        tuning_job.refresh()
        state = tuning_job.state
        state_name = JobState(state).name
        logging.info(f"Current job state: {state_name} ({state})")

        if tuning_job.tuning_data_statistics.supervised_tuning_data_stats:
            stats = (
                tuning_job.tuning_data_statistics.supervised_tuning_data_stats
            )

            # Core stats
            logging.info(
                f"  Total Examples in Dataset: {stats.tuning_dataset_example_count}"
            )
            logging.info(
                f"  Total Tuning Characters: {stats.total_tuning_character_count}"
            )
            logging.info(
                f"  Total Billable Characters: {stats.total_billable_character_count}"
            )
            logging.info(
                f"  Total Billable Tokens: {stats.total_billable_token_count}"
            )
            logging.info(f"  Total Tuning Steps: {stats.tuning_step_count}")
            logging.info(
                f"  Total Truncated Examples: {stats.total_truncated_example_count}"
            )

            # Input token distribution
            if stats.user_input_token_distribution:
                input_dist = stats.user_input_token_distribution
                logging.info("  Input Token Distribution:")
                logging.info(f"    Min: {input_dist.min_}")
                logging.info(f"    Max: {input_dist.max_}")
                logging.info(f"    Mean: {input_dist.mean}")
                logging.info(f"    P95: {input_dist.p95}")

            # Output token distribution
            if stats.user_output_token_distribution:
                output_dist = stats.user_output_token_distribution
                logging.info("  Output Token Distribution:")
                logging.info(f"    Min: {output_dist.min_}")
                logging.info(f"    Max: {output_dist.max_}")
                logging.info(f"    Mean: {output_dist.mean}")
                logging.info(f"    P95: {output_dist.p95}")

            # Messages per example distribution
            if stats.user_message_per_example_distribution:
                message_dist = stats.user_message_per_example_distribution
                logging.info("  Messages Per Example Distribution:")
                logging.info(f"    Min: {message_dist.min_}")
                logging.info(f"    Max: {message_dist.max_}")
                logging.info(f"    Mean: {message_dist.mean}")
                logging.info(f"    P95: {message_dist.p95}")

            # Sample user messages
            if stats.user_dataset_examples:
                logging.info("  Sample User Dataset Examples:")
                for i, example in enumerate(stats.user_dataset_examples[:5]):
                    logging.info(f"    Example {i + 1}: {example}")

        # Check if job has completed
        if state in TERMINAL_STATES:
            logging.info(f"Job finished with state: {state_name}")
            if state == JobState.JOB_STATE_SUCCEEDED:
                logging.info("Job completed successfully!")
            elif state == JobState.JOB_STATE_FAILED:
                logging.error(f"Error details: {tuning_job.error}")
            break

        time.sleep(POLL_INTERVAL)


def gs_uri(bucket_name: str, destination: str) -> str:
    return f"gs://{bucket_name}/{destination}"


def upload(bucket_name, source, destination) -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination)

    blob.upload_from_filename(source)
    logging.info(f"File {source} uploaded to {destination} in {bucket_name}.")

    return gs_uri(bucket_name, destination)


def train(bucket, gcs_path, source_model, model) -> sft.SupervisedTuningJob:
    uri = gs_uri(bucket, gcs_path, source_model, model)
    job = sft.train(
        source_model=source_model,
        train_dataset=uri,
        epochs=EPOCHS,
        adapter_size=ADAPTER_SIZE,
        learning_rate_multiplier=LEARNING_RATE_MULTIPLIER,
        tuned_model_display_name=model,
    )

    return job


def main(argv):
    """Main entry point for the script."""
    if FLAGS.project_id is None:
        raise ValueError("The --project_id flag is required.")

    if FLAGS.list:
        list_tuning_jobs(FLAGS.project_id, FLAGS.location)
    elif FLAGS.poll:
        poll_tuning_job(FLAGS.project_id, FLAGS.location, FLAGS.poll)
    elif FLAGS.upload:
        upload(FLAGS.bucket, FLAGS.examples, FLAGS.gcs_path)
    elif FLAGS.train:
        train(FLAGS.bucket, FLAGS.gcs_path, FLAGS.source_model, FLAGS.model)
    else:
        logging.error(
            "No valid command provided. Use --list, --poll, --upload, or --train."
        )


if __name__ == "__main__":
    app.run(main)
