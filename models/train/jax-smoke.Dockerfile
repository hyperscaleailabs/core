FROM python:3.11.9-slim

RUN pip install --no-cache-dir "jax[cpu]==0.5.3"

COPY train/jax_train_validation_smoke.py /opt/models/jax_train_validation_smoke.py

USER 65532:65532
ENTRYPOINT ["python", "/opt/models/jax_train_validation_smoke.py"]
