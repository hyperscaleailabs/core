"""Deterministic JAX train/validation smoke workload."""

from __future__ import annotations

import json

import jax
import jax.numpy as jnp


def loss(weight: jax.Array, inputs: jax.Array, labels: jax.Array) -> jax.Array:
    predictions = inputs * weight
    return jnp.mean((predictions - labels) ** 2)


def main() -> None:
    inputs = jnp.arange(1, 9, dtype=jnp.float32)
    labels = inputs * 3.0
    train_inputs, validation_inputs = inputs[:6], inputs[6:]
    train_labels, validation_labels = labels[:6], labels[6:]
    weight = jnp.array(0.0)
    initial_validation = loss(weight, validation_inputs, validation_labels)
    gradient = jax.jit(jax.grad(loss))
    for _ in range(100):
        weight -= 0.01 * gradient(weight, train_inputs, train_labels)
    final_train = loss(weight, train_inputs, train_labels)
    final_validation = loss(weight, validation_inputs, validation_labels)
    result = {
        "device_count": jax.device_count(),
        "evidence_tier": "simulation demo",
        "final_train_loss": float(final_train),
        "final_validation_loss": float(final_validation),
        "initial_validation_loss": float(initial_validation),
        "backend": jax.default_backend(),
        "validation_improved": bool(final_validation < initial_validation),
    }
    print(json.dumps(result, sort_keys=True))
    if not result["validation_improved"]:
        raise SystemExit("validation loss did not improve")


if __name__ == "__main__":
    main()
