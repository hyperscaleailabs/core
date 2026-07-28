"""ASC-023: trajectory artifact stores (in-memory + S3 with a fake client)."""

from __future__ import annotations

import json

from asc_telemetry import InMemoryArtifactStore, NullArtifactStore, S3ArtifactStore


def test_null_store_discards_and_returns_empty_ref():
    store = NullArtifactStore()
    assert store.put_trajectory("run-1", "traj-1", {"outcome": "failed"}) == ""


def test_in_memory_store_roundtrip():
    store = InMemoryArtifactStore()
    ref = store.put_trajectory("run-1", "traj-1", {"outcome": "failed", "secret": "kept-here"})
    assert ref == "memory://run-1/traj-1.json"
    assert store.get(ref)["outcome"] == "failed"


class FakeS3:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], bytes] = {}

    def put_object(self, *, Bucket, Key, Body, ContentType):  # noqa: N803 - boto3 kwarg names
        self.objects[(Bucket, Key)] = Body


def test_s3_store_writes_and_returns_ref():
    client = FakeS3()
    store = S3ArtifactStore(client, bucket="asc-trajectories")
    ref = store.put_trajectory("run-9", "traj-9", {"outcome": "recovered"})
    assert ref == "s3://asc-trajectories/trajectories/run-9/traj-9.json"
    (bucket, key), body = next(iter(client.objects.items()))
    assert bucket == "asc-trajectories"
    assert json.loads(body.decode())["outcome"] == "recovered"
