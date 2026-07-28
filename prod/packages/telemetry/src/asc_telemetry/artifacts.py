"""Trajectory artifact storage (ASC-023).

Raw/sanitized trajectory artifacts are written to object storage (MinIO/S3) and referenced from the
event stream by ``rawOutputRef`` — the raw payload never rides the Kafka stream (SYSTEM_DESIGN §14).
The S3 client is lazily imported so the package imports/tests without boto3 or a bucket.
"""

from __future__ import annotations

import json
from typing import Protocol


class ArtifactStore(Protocol):
    def put_trajectory(self, run_id: str, trajectory_id: str, payload: dict) -> str:
        """Persist a trajectory artifact and return a stable reference (used as rawOutputRef)."""
        ...


class NullArtifactStore:
    """Discards artifacts (deployed fallback when no object store is configured). Returns an empty
    ref so nothing accumulates in RAM; the durable run result is unaffected."""

    def put_trajectory(self, run_id: str, trajectory_id: str, payload: dict) -> str:
        return ""


class InMemoryArtifactStore:
    """Test/in-process double: keeps artifacts in a dict, returns a memory:// ref."""

    def __init__(self) -> None:
        self.objects: dict[str, dict] = {}

    def put_trajectory(self, run_id: str, trajectory_id: str, payload: dict) -> str:
        key = f"{run_id}/{trajectory_id}.json"
        self.objects[key] = payload
        return f"memory://{key}"

    def get(self, ref: str) -> dict:
        return self.objects[ref.removeprefix("memory://")]


class S3ArtifactStore:
    """Writes artifacts to an S3-compatible bucket (MinIO). ``client`` is injected or built from env."""

    def __init__(
        self, client, bucket: str = "asc-trajectories", prefix: str = "trajectories"
    ) -> None:
        self._client = client
        self._bucket = bucket
        self._prefix = prefix

    @classmethod
    def from_env(
        cls, endpoint_url: str, access_key: str, secret_key: str, bucket: str = "asc-trajectories"
    ) -> S3ArtifactStore:
        try:
            import boto3  # runtime dep; provided in the service image
        except ImportError as exc:  # pragma: no cover - only without boto3 installed
            raise RuntimeError("boto3 is required for S3ArtifactStore.from_env") from exc
        client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        return cls(client, bucket)

    def put_trajectory(self, run_id: str, trajectory_id: str, payload: dict) -> str:
        key = f"{self._prefix}/{run_id}/{trajectory_id}.json"
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=json.dumps(payload).encode(),
            ContentType="application/json",
        )
        return f"s3://{self._bucket}/{key}"
