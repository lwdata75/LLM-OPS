"""
Automatically undeploy Vertex AI endpoint models after they have been
deployed for a configurable amount of time.

Usage:
    python scripts/auto_undeploy.py [--max-age-minutes 10] [--poll-interval 60]
"""
import argparse
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from dotenv import load_dotenv
from google.api_core import exceptions
from google.cloud import aiplatform
from google.cloud.aiplatform_v1.types import DeployedModel

load_dotenv()

# Environment driven defaults
DEFAULT_MAX_AGE_MINUTES = int(os.getenv("AUTO_UNDEPLOY_MAX_AGE_MINUTES", "10"))
DEFAULT_POLL_SECONDS = int(os.getenv("AUTO_UNDEPLOY_POLL_SECONDS", "60"))

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "aerobic-polygon-460910-v9")
PROJECT_NUMBER = os.getenv("GCP_PROJECT_NUMBER", "432566588992")
REGION = os.getenv("GCP_REGION", "europe-west2")
ENDPOINT_ID = os.getenv("GCP_ENDPOINT_ID", "5724492940806455296")

ENDPOINT_RESOURCE_NAME = (
    f"projects/{PROJECT_NUMBER}/locations/{REGION}/endpoints/{ENDPOINT_ID}"
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Automatically undeploy models after a time limit."
    )
    parser.add_argument(
        "--max-age-minutes",
        type=int,
        default=DEFAULT_MAX_AGE_MINUTES,
        help="Maximum allowed deployment age before undeploying (default: %(default)s).",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=DEFAULT_POLL_SECONDS,
        help=(
            "Polling interval in seconds when waiting for models to reach the "
            "maximum age (default: %(default)s)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not undeploy, only report what would happen.",
    )
    parser.add_argument(
        "--exit-if-empty",
        action="store_true",
        help=(
            "Exit immediately if the endpoint has no deployed models instead of waiting."
        ),
    )
    return parser.parse_args()


def init_vertex_ai() -> None:
    """Initialise the Vertex AI client."""
    aiplatform.init(project=PROJECT_ID, location=REGION)


def get_endpoint() -> aiplatform.Endpoint:
    """Return a fresh handle to the Vertex AI endpoint."""
    return aiplatform.Endpoint(endpoint_name=ENDPOINT_RESOURCE_NAME)


def to_datetime(value) -> Optional[datetime]:
    """Convert a timestamp-like value to a timezone aware datetime."""
    if value is None:
        return None
    try:
        # Protobuf Timestamp has ToDatetime method.
        return value.ToDatetime(tzinfo=timezone.utc)
    except AttributeError:
        pass
    if isinstance(value, str):
        # Ensure RFC3339 strings become timezone aware.
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
                timezone.utc
            )
        except ValueError:
            return None
    return None


def format_timedelta(delta: timedelta) -> str:
    """Return a human-friendly string for a timedelta."""
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes or hours:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def fetch_deployed_models(endpoint: aiplatform.Endpoint) -> List[DeployedModel]:
    """Return the list of deployed models for the endpoint."""
    return list(endpoint.gca_resource.deployed_models or [])


def main() -> None:
    args = parse_args()
    max_age = timedelta(minutes=args.max_age_minutes)
    poll = max(args.poll_interval, 10)

    try:
        init_vertex_ai()
        endpoint = get_endpoint()
    except exceptions.GoogleAPICallError as error:
        print(f"Failed to initialise endpoint: {error}")
        sys.exit(1)

    print("=" * 70)
    print("Auto-undeploy monitor started")
    print(f"Project: {PROJECT_ID}")
    print(f"Endpoint ID: {ENDPOINT_ID}")
    print(f"Maximum age: {args.max_age_minutes} minutes")
    if args.dry_run:
        print("Running in dry-run mode (no undeploy calls will be made)")
    print("=" * 70)

    try:
        while True:
            try:
                endpoint = get_endpoint()
            except exceptions.GoogleAPICallError as error:
                print(f"Failed to fetch endpoint state: {error}")
                print(f"Retrying in {poll} seconds...")
                time.sleep(poll)
                continue

            deployed_models = fetch_deployed_models(endpoint)

            if not deployed_models:
                print("No models currently deployed.")
                if args.exit_if_empty:
                    break
                print(f"Waiting {poll} seconds before checking again...")
                time.sleep(poll)
                continue

            now = datetime.now(timezone.utc)
            overdue_models = []
            next_due_in: Optional[timedelta] = None

            for model in deployed_models:
                created_at = to_datetime(model.create_time)
                if created_at is None:
                    print(f"Skipping model {model.id}: missing create_time.")
                    continue
                age = now - created_at

                status_line = (
                    f"Model {model.display_name or model.id} "
                    f"(deployed {format_timedelta(age)} ago)"
                )

                if age >= max_age:
                    print(f"{status_line} exceeds limit -> scheduling undeploy")
                    overdue_models.append(model)
                else:
                    remaining = max_age - age
                    print(f"{status_line} - {format_timedelta(remaining)} remaining")
                    if next_due_in is None or remaining < next_due_in:
                        next_due_in = remaining

            if overdue_models:
                for model in overdue_models:
                    print(f"Undeploying model {model.display_name or model.id}...")
                    if args.dry_run:
                        print("Dry-run: skipping call.")
                        continue
                    try:
                        endpoint.undeploy(deployed_model_id=model.id)
                        print("Undeployed successfully.")
                    except exceptions.GoogleAPICallError as error:
                        print(f"Failed to undeploy {model.id}: {error}")

                # Allow time for Vertex AI to update state before next check.
                time.sleep(15)
                continue

            if next_due_in is None:
                # No valid timestamps encountered.
                print(f"Waiting {poll} seconds before next check...")
                time.sleep(poll)
                continue

            sleep_for = min(next_due_in.total_seconds(), poll)
            if sleep_for <= 0:
                # A model should already be due, loop will catch it next iteration.
                continue

            print(f"Waiting {int(sleep_for)} seconds for the next check...")
            time.sleep(sleep_for)

    except KeyboardInterrupt:
        print("\nStopping auto-undeploy monitor.")


if __name__ == "__main__":
    main()
