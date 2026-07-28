---
document: Project Direction
project: SignalMatter
version: 0.1.0
status: Deferred
depends_on: NeuroDuet
date: 2026-07-28
---

# SignalMatter

## Open Neural-Interface Reliability and Scientific Experiment Lab

## 1. Project mission

SignalMatter is an open scientific application lab for studying how neural-signal models behave as recording conditions, interface properties, and biological signals change over time.

It begins with open EEG datasets and simulated interface-degradation profiles. It provides a complete environment for:

* Training neural decoders.
* Simulating signal drift and interface degradation.
* Running distributed evaluations.
* Comparing adaptation strategies.
* Designing follow-up experiments.
* Reviewing results collaboratively.
* Preserving experiment provenance and replay.
* Progressively connecting neural decoding with materials, nanotechnology, bioelectronics, and autonomous laboratories.

Its long-term objective is:

> Build open scientific-agent runtime and laboratory-orchestration infrastructure for the co-design of neural interfaces, materials, signal-processing systems, and adaptive AI models.

SignalMatter is an application built on HSAILabs/core. It creates practical requirements for the core while keeping its domain models, experiments, assumptions, and user experience inside the application.

---

# 2. Golden problem

The durable problem is:

> Neural decoders lose accuracy when signal distributions, sensor quality, electrode contact, noise, or user physiology change over time.

This creates operational problems across both non-invasive and implantable interfaces:

* Frequent recalibration.
* Unstable control.
* Poor transfer between sessions.
* Difficult comparison of decoder architectures.
* Difficulty separating model failure from signal-quality failure.
* Limited reproducibility.
* Expensive longitudinal testing.
* Uncertainty about which adaptation method should be used.

The initial project does not attempt to solve implant biocompatibility or predict real clinical device lifetime.

It creates the infrastructure needed to ask a narrower and measurable question:

> Which decoder and adaptation strategy remains most reliable under a declared set of simulated interface-degradation and neural-signal-drift conditions?

---

# 3. Golden use case

## Preserve Motor-Imagery Decoder Reliability

A user joins a SignalMatter room through HSAILabs Meet and asks:

> Compare the current neural decoder under three interface-degradation profiles. Determine which model and adaptation strategy best preserves left-versus-right motor-imagery accuracy.

The application:

1. Loads an open motor-imagery EEG dataset.
2. Selects one or more trained decoders.
3. Applies declared signal and interface-degradation profiles.
4. Executes a distributed evaluation across subjects, sessions, profiles, and random seeds.
5. Compares the baseline and adapted models.
6. Identifies common failure patterns.
7. Recommends the next experiment.
8. Presents the results through a visual dashboard and voice agent.
9. Preserves the complete experiment for replay.

The human sees:

* EEG traces.
* Channel topography.
* Signal-quality indicators.
* Accuracy and calibration curves.
* Degradation over simulated time.
* Confusion matrices.
* Failure groups.
* Model latency.
* Infrastructure throughput.
* The evidence supporting the agent’s conclusions.

---

# 4. Why this is the right compression

## Broad enough to be directional

SignalMatter has a credible path toward:

* Neural decoding.
* Longitudinal BCI reliability.
* Neural-data infrastructure.
* Nanomaterials and electrode profiles.
* Soft bioelectronics.
* Closed-loop adaptation.
* Scientific experiment planning.
* Autonomous materials laboratories.
* Implant and device co-design.

## Small enough to implement

The first version requires no:

* Wet laboratory.
* Human-subject recruitment.
* Implantable hardware.
* Medical-device claims.
* Custom neural-interface fabrication.
* Clinical data.
* High-fidelity biological simulation.
* Physical robotics.

## Demonstrable

The application has a clear visual narrative:

```text
clean neural signal
        ↓
progressively degraded signal
        ↓
decoder performance decreases
        ↓
adaptation strategy is applied
        ↓
performance partially recovers
        ↓
agent recommends the next experiment
```

## Useful as a scientific application lab

Contributors can replace:

* The dataset.
* Decoder.
* Degradation model.
* Adaptation policy.
* Optimization algorithm.
* Evaluation metric.
* Experiment-planning agent.
* Serving backend.

This provides multiple entry points without fragmenting the project into unrelated demonstrations.

---

# 5. Open data foundation

## Initial neural dataset

Use motor-imagery EEG through MOABB and MNE.

MOABB currently exposes approximately 160 open EEG datasets across motor imagery, P300, SSVEP, c-VEP, and other paradigms. It standardizes the relationship among datasets, paradigms, evaluation procedures, and model pipelines.

The first release should use either:

* The PhysioNet EEG Motor Movement/Imagery dataset through MNE.
* A compact MOABB motor-imagery dataset.
* A multi-session MOABB dataset when evaluating longitudinal drift.

MNE provides the preprocessing and EEG-analysis layer, while Braindecode provides PyTorch-native models and training workflows for EEG, ECoG, and MEG decoding. Braindecode includes examples for loading MOABB datasets and training standard neural decoders.

## Initial materials and nanotechnology data

Materials Project should provide general computed-material properties and structure metadata. Its supported `mp-api` Python client gives programmatic access to public materials records. Matbench provides standardized property-prediction tasks and benchmark splits.

eNanoMapper should provide nanomaterial characterization, biological-response, and toxicological metadata. Its public database supports search and download of engineered-nanomaterial information in standard formats.

These sources do not directly map a material to BCI performance.

In the first version, they are used for:

* Dataset-adapter development.
* Materials profile cards.
* Search and research demonstrations.
* Parameter provenance.
* Future experiment hypotheses.

They must not be used to claim that a material is biocompatible, implant-safe, or superior for a neural device.

---

# 6. Initial interface-degradation model

SignalMatter v0.1 uses explicitly simulated profiles.

## Profile A: Stable interface

* Low channel noise.
* No channel loss.
* Small session drift.
* Stable amplitude.
* Stable frequency response.

## Profile B: Gradual degradation

* Increasing impedance proxy.
* Increasing broadband noise.
* Slow amplitude attenuation.
* Channel-specific drift.
* Occasional transient artifacts.

## Profile C: Unstable interface

* Channel dropout.
* Correlated noise.
* Larger distribution shift.
* Electrode bridging proxy.
* Non-stationary artifacts.

The profiles alter the neural observations, not the dataset labels.

Example transforms:

```text
amplitude attenuation
frequency-dependent attenuation
Gaussian and colored noise
channel dropout
channel bridging
temporal drift
baseline shift
sampling jitter
artifact bursts
session-specific affine transformation
```

The degradation simulator must record:

* Mathematical transformation.
* Parameters.
* Random seed.
* Channels affected.
* Time interval.
* Severity.
* Rationale.
* Evidence category.

Every profile is labeled:

```text
SYNTHETIC_INTERFACE_PROFILE
```

It is not labeled as a physiological or clinical model.

---

# 7. Two connected learning loops

## Loop A: Neural-decoder reliability

```text
open EEG dataset
    ↓
preprocessing
    ↓
PyTorch neural decoder
    ↓
JAX degradation simulation
    ↓
Ray distributed evaluation
    ↓
failure analysis
    ↓
adaptation or retraining
    ↓
repeat evaluation
```

This is the primary first-release loop.

## Loop B: Scientific experiment planning

```text
experiment history
    ↓
scientific agent proposes candidates
    ↓
human reviews constraints
    ↓
Ray executes experiment matrix
    ↓
results and uncertainty are measured
    ↓
Bayesian optimization selects next candidate
    ↓
human approves the next experiment
```

BoTorch provides a PyTorch-based Bayesian-optimization framework for sequentially optimizing costly black-box objectives, including constrained and cost-aware optimization. It is a suitable future engine for selecting decoder, degradation, and materials-profile experiments.

---

# 8. Technology roles

The project should use the existing HSAILabs stack selectively. It should not force every technology into the first demonstration.

## PyTorch

Primary uses:

* EEGNet, ShallowFBCSPNet, or compact transformer decoder.
* Fine-tuning.
* Calibration models.
* Drift detectors.
* Model packaging.
* Optional materials-property surrogate.
* DPO training.

Braindecode models are ordinary PyTorch modules, which keeps the application compatible with standard distributed-training, checkpointing, and serving workflows.

## JAX

Primary uses:

* Vectorized degradation simulation.
* Large parameter sweeps.
* Differentiable signal transforms.
* Online adaptation experiments.
* Fast synthetic trajectory generation.
* Later constrained RL environments.

JAX provides composable JIT compilation, automatic vectorization, and gradient transformations that are suitable for large batches of numerical simulations.

## Ray

Primary uses:

* Distributed model training.
* Subject-level evaluation workers.
* Session and degradation-profile matrices.
* Hyperparameter search.
* Failure recovery.
* Experiment scheduling.
* Aggregation.

Ray Train supports scaling existing PyTorch training functions, while Ray workers provide a natural unit for independent dataset-subject and experiment episodes.

## vLLM

Primary uses:

* Scientific experiment-planning agent.
* Structured hypothesis generation.
* Report generation.
* Dataset and experiment question answering.
* Model-card and dataset-card assistance.
* Optional multimodal review of charts.

vLLM supports text and supported multimodal generative models. It should not calculate metrics or replace the neural decoder.

## LiveKit Meet

Primary uses:

* Voice experiment request.
* Shared dashboard.
* Agent participation.
* Collaborative review.
* Approval of experiment plans.
* Audio explanation of results.

LiveKit agents can participate in rooms as real-time Python or Node.js programs and can consume and publish audio, video, and data tracks.

## RL

The initial RL problem should be:

> Select when and how to adapt the neural decoder while minimizing recalibration cost and preserving performance.

Possible actions:

```text
continue_without_change
recalibrate_normalization
adapt_classifier_head
fine_tune_recent_windows
disable_unstable_channel
request_human_review
rollback_model
```

Possible reward:

```text
+ decoding accuracy
+ calibration stability
+ restored performance
- retraining cost
- latency
- excessive model changes
- unsafe confidence
- unnecessary human interruption
```

This should begin in a simulated offline environment. It is not a medical treatment or stimulation-control policy.

## DPO

DPO should be applied to high-level scientific decisions or reports.

Example preference pairs:

* Clear plan versus vague plan.
* Evidence-grounded conclusion versus unsupported conclusion.
* Low-cost discriminating experiment versus expensive redundant experiment.
* Conservative uncertainty statement versus overconfident claim.

DPO should not be used to directly optimize neural predictions.

## Transformers and omni models

Use transformers for:

* Neural time-series decoding.
* Cross-session adaptation.
* Scientific literature or metadata retrieval.
* Multimodal interaction.
* Voice and visual review.

Omni or realtime models can provide the conversational interface, but all scientific outputs must refer to recorded metrics and artifacts.

## Tree-of-Thought-style planning

A structured scientific-agent planning loop can explore:

1. Competing hypotheses.
2. Candidate experiments.
3. Expected information gain.
4. Cost and compute.
5. Confounding factors.
6. Selection of the next experiment.

This should be implemented as an inspectable planning graph rather than relying on hidden model reasoning.

---

# 9. Data and infrastructure layers

## Canonical storage

### PostgreSQL

Store:

* Projects.
* Experiments.
* Models.
* Datasets.
* Profiles.
* User decisions.
* Experiment plans.

### MinIO

Store:

* Raw and processed datasets.
* Model checkpoints.
* EEG windows.
* Reports.
* Plots.
* Replay artifacts.

### ClickHouse

Store:

* Per-window predictions.
* Evaluation metrics.
* Drift events.
* Model latency.
* Distributed-worker metrics.
* Experiment time series.

### Kafka

Topics:

```text
dataset.loaded
model.training.started
model.checkpoint.created
simulation.profile.applied
evaluation.window.completed
drift.detected
adaptation.proposed
operator.approved
experiment.completed
report.published
```

Kafka is not required for the first local demonstration. The initial implementation may emit the same events into a local file or PostgreSQL.

### OpenTelemetry, Prometheus, and Grafana

Observe:

* Data-loading latency.
* GPU utilization.
* Ray-worker health.
* Training throughput.
* vLLM request latency.
* Evaluation throughput.
* Artifact completeness.
* Model drift.
* Decoder accuracy.
* Adaptation frequency.

### Superset

Use for longer-term experiment exploration and comparison across datasets, subjects, models, and profiles.

---

# 10. Application structure

```text
apps/
└── signalmatter/
    ├── app.yaml
    ├── README.md
    ├── datasets/
    │   ├── moabb/
    │   ├── eegbci/
    │   ├── materials-project/
    │   └── enanomapper/
    ├── profiles/
    │   ├── stable.yaml
    │   ├── gradual-degradation.yaml
    │   └── unstable.yaml
    ├── models/
    │   ├── eegnet/
    │   ├── shallow-fbcsp/
    │   ├── eeg-transformer/
    │   └── drift-detector/
    ├── simulation/
    │   ├── degradation/
    │   ├── session-drift/
    │   └── adaptation-env/
    ├── experiments/
    │   ├── baseline.yaml
    │   ├── degradation-matrix.yaml
    │   └── adaptation.yaml
    ├── agents/
    │   ├── experiment-planner/
    │   ├── evidence-reviewer/
    │   └── report-agent/
    ├── meet/
    ├── ui/
    └── docs/
```

---

# 11. HSAILabs/core capabilities consumed

## Required

```text
models.dataset-manifest
models.training
models.checkpoint
models.inference
prod.experiment-runtime
prod.evaluation
prod.replay
dtwins.simulation
infra.local-runtime
```

## Optional in the first release

```text
infra.ray-runtime
meet.operator-room
agents.scientific-planner
models.vllm-serving
models.preference-training
prod.kafka-events
prod.clickhouse-analytics
atlas.research-index
```

SignalMatter should test an important generalization of `dtwins/`:

> A digital twin does not need to be a 3D physical world. It may represent a signal-generating system, sensor interface, degradation process, biological process, or scientific instrument.

---

# 12. What not to use initially

## MuJoCo and Isaac Gym

Neither MuJoCo nor Isaac Gym is a natural simulator for electrode electrochemistry, neural signal generation, or tissue-device interactions.

They should not be forced into SignalMatter v0.1 merely to demonstrate stack breadth.

They become relevant later for:

* Robotic sample handling.
* Automated laboratory workcells.
* Instrument loading.
* Physical experiment orchestration.
* Wearable-device mechanical interaction.
* Robot-assisted electrode testing.

For future electro-mechanical and neural simulation, more appropriate open systems include:

* FEniCSx for finite-element simulations.
* NEURON for biologically realistic neuron and neural-network simulation.

FEniCSx is an open finite-element library, while NEURON is designed for electrical and chemical simulation of neurons and neural networks.

---

# 13. Deliverable in one to two weeks

## Working demonstration

The first demonstration answers:

> Which decoder remains most reliable under three synthetic interface-degradation profiles?

## Required implementation

### Data

* One MOABB or EEGBCI motor-imagery dataset.
* Reproducible download.
* Subject-level train/test split.
* Dataset card.
* Preprocessing manifest.

### Models

* Classical CSP/LDA baseline.
* One PyTorch Braindecode model.
* Optional compact EEG transformer.

### Simulation

* Three JAX degradation profiles.
* Vectorized transform application.
* Deterministic seeds.
* Severity progression.

### Distributed evaluation

Evaluate:

```text
2 decoders
× 3 degradation profiles
× 3 severity levels
× 5–10 subjects
× 3 seeds
```

This produces 270–540 evaluation units, enough to demonstrate Ray distribution without manufacturing unnecessary scale.

### User experience

Through Meet, the operator says:

> Evaluate the current decoder against gradual and unstable interface profiles.

The application:

* Generates the experiment manifest.
* Shows the evaluation progress.
* Presents degradation curves.
* Identifies the most robust decoder.
* Produces a structured report.
* Links to failed windows and subject-level results.

### Infrastructure

* Local k3d profile.
* Ray local cluster.
* PostgreSQL.
* MinIO.
* Grafana.
* Optional vLLM service.
* Docker images and Helm or Kustomize configuration.

## One-to-two-week acceptance criteria

* One command starts the local stack.
* One command downloads and prepares the dataset.
* Both decoder baselines train reproducibly.
* Each degradation transform has automated tests.
* Ray executes the evaluation matrix.
* Every result links to model, dataset, subject, profile, severity, and seed.
* Meet can initiate an evaluation.
* The agent’s conclusions are generated from stored metrics.
* A complete report and replay are available.
* No clinical or materials-performance claims are made.

---

# 14. Six-week deliverable

By week six, SignalMatter should become a reusable neural-interface reliability benchmark.

## Capabilities

* Three or more open EEG datasets.
* Within-session and cross-session evaluation.
* EEGNet, ShallowFBCSPNet, and transformer comparison.
* Calibration and uncertainty metrics.
* Drift detection.
* JAX online-adaptation environment.
* Rule-based and RL adaptation policies.
* Ray-distributed experiment campaigns.
* Materials Project and eNanoMapper adapters.
* Scientific-agent experiment proposals.
* BoTorch next-experiment selection.
* DPO experiment for evidence-grounded planning.
* NWB-compatible export.
* LiveKit collaborative review.
* Kafka/ClickHouse telemetry profile.
* Public benchmark report.

NWB provides a common standard for storing and reusing neurophysiology data, while DANDI provides a versioned public archive for electrophysiology, optophysiology, behavioral time-series, and related neurophysiology datasets.

## Golden six-week demonstration

1. Operator selects a dataset and decoder.
2. Scientific agent proposes a degradation and adaptation experiment.
3. Operator reviews cost and assumptions.
4. Ray executes the experiment matrix.
5. RL policy chooses whether to adapt or continue.
6. Dashboard compares accuracy, uncertainty, stability, latency, and adaptation cost.
7. Agent recommends the next experiment.
8. BoTorch identifies a higher-information candidate.
9. Full lineage and replay are published.

---

# 15. Three-month direction

## Reliability benchmark suite

* Multiple EEG paradigms.
* Multiple sessions.
* Cross-subject transfer.
* Dataset-shift benchmarks.
* Channel-loss benchmarks.
* Sensor-placement perturbations.
* Calibration-cost measurement.
* Confidence and abstention.

## Neural-data standards

* NWB import and export.
* DANDI adapter.
* Dataset licenses and provenance.
* Subject and session privacy boundaries.
* Synthetic-versus-real evidence labels.

## Device-profile abstraction

Create a reusable profile contract:

```yaml
profile:
  identity: candidate-a
  evidenceTier: synthetic
  electrical:
    attenuation: ...
    noise: ...
    drift: ...
  mechanical:
    flexibilityProxy: ...
  biological:
    toxicityDataReferences: []
  provenance:
    sources: []
    assumptions: []
```

## Scientific agent

The agent should:

* Search registered datasets.
* Form hypotheses.
* Propose experiment matrices.
* Estimate compute cost.
* Identify confounders.
* Request human approval.
* Interpret measured results.
* Suggest the next experiment.

---

# 16. Six-month direction

## Longitudinal neural-interface digital twin

Introduce:

* Session-to-session signal evolution.
* Device-profile state.
* Decoder state.
* User adaptation.
* Calibration history.
* Confidence history.
* Failure and intervention history.

## More realistic simulation

Add:

* NEURON-based synthetic neural signals.
* FEniCSx proof-of-concept for electrode or field models.
* Measured impedance datasets when openly available.
* Better drift models from published evidence.
* Explicit uncertainty distributions.

## Optional physical data path

Add:

* BrainFlow-compatible acquisition.
* Lab Streaming Layer synchronization.
* OpenBCI development-device adapter.
* Consent and local-only recording workflow.

This remains an optional research mode and must not silently collect biosignals.

## Autonomous-laboratory simulation

Use MuJoCo or Isaac-based laboratory robotics for:

* Selecting a test coupon.
* Moving it to a simulated measurement station.
* Running a simulated impedance measurement.
* Recording the result.
* Choosing the next test.

The scientific result may remain simulated, but the orchestration and provenance workflow become real platform capabilities.

---

# 17. Twelve-month direction

## Scientific agent runtime for neural-interface co-design

The platform should connect:

```text
materials and nanotechnology data
        ↓
candidate interface profiles
        ↓
electrical/mechanical/biological simulations
        ↓
neural-signal generation and degradation
        ↓
decoder training and adaptation
        ↓
distributed evaluation
        ↓
experiment selection
        ↓
robotic or instrument execution
        ↓
evidence and provenance
        ↓
next candidate
```

## Target capabilities

* Multi-objective materials and decoder optimization.
* Instrument adapters.
* Physical or partner-lab experiment ingestion.
* Constrained Bayesian optimization.
* Autonomous experiment queues.
* Human approval gates.
* Replication experiments.
* Dataset and result publication.
* Longitudinal neural-decoder benchmarks.
* Neural-interface profile registry.
* Collaborative scientific review.
* Cross-application support through HSAILabs/core.

## Long-term north star

> SignalMatter becomes an open reference application for scientific-agent runtime and autonomous-laboratory orchestration applied to neural interfaces, bioelectronics, and advanced materials.

---

# 18. Stable technical foundation

The durable stack is not any single EEG model or language model.

The stable lifecycle is:

```text
open scientific data
        ↓
versioned preprocessing
        ↓
model training
        ↓
simulation
        ↓
distributed evaluation
        ↓
human review
        ↓
adaptation or experiment selection
        ↓
replay and provenance
        ↓
next experiment
```

This lifecycle uses the immediate HSAILabs expertise:

| Capability                       | Technology                         |
| -------------------------------- | ---------------------------------- |
| Neural models                    | PyTorch, Braindecode, transformers |
| Numerical simulation             | JAX                                |
| Distributed execution            | Ray                                |
| Scientific planning              | LLM/VLM through vLLM               |
| Preference alignment             | DPO                                |
| Experiment optimization          | BoTorch                            |
| Realtime collaboration           | LiveKit                            |
| Local infrastructure             | Debian, KVM, k3d                   |
| Cluster deployment               | Kubernetes, Helm, Kustomize        |
| Cloud deployment                 | Terraform, AWS, GCP, Azure         |
| Event and data plane             | Kafka, Flink, Spark                |
| Metadata                         | PostgreSQL                         |
| Artifacts                        | MinIO                              |
| Analytics                        | ClickHouse, Superset               |
| Observability                    | OpenTelemetry, Prometheus, Grafana |
| Retrieval                        | pgvector, FAISS, Chroma, or Milvus |
| Future biological simulation     | NEURON                             |
| Future finite-element simulation | FEniCSx                            |
| Future laboratory robotics       | MuJoCo or Isaac                    |

---

# 19. Scientific integrity boundaries

SignalMatter must state clearly:

* Open EEG is not equivalent to implantable BCI data.
* Synthetic degradation is not clinical device aging.
* Materials metadata does not establish biocompatibility.
* Model accuracy does not establish medical usefulness.
* Simulation results do not validate a physical implant.
* The application is not a medical device.
* Human-subject data collection is outside v0.1.
* Agent recommendations are experiment proposals, not scientific conclusions.
* Every result must expose assumptions and evidence tier.

Suggested evidence tiers:

```text
OPEN_DATA_BENCHMARK
SYNTHETIC_DEGRADATION_EXPERIMENT
COMPUTATIONAL_MATERIALS_EXPERIMENT
BIOPHYSICAL_SIMULATION
INSTRUMENT_SIMULATION
PHYSICAL_BENCH_EXPERIMENT
HUMAN_RESEARCH_DATA
CLINICAL_EVIDENCE
```

Only the first two are required initially.

---

# 20. Final project formulation

## Name

**SignalMatter**

## Category

**Open Neural-Interface Reliability and Scientific Experiment Lab**

## Golden use case

> Evaluate which neural decoder and adaptation strategy best preserves motor-imagery performance under simulated interface degradation.

## Immediate deliverable

> An interactive LiveKit application using open EEG data, PyTorch neural decoders, JAX degradation simulation, Ray-distributed evaluation, vLLM scientific assistance, and complete observability and replay.

## Six-week deliverable

> A reusable benchmark for neural-decoder drift, degradation, adaptation, and human-guided experiment planning.

## Long-term direction

> An open scientific-agent runtime connecting neural data, materials profiles, simulation, model adaptation, experiment optimization, laboratory instruments, and autonomous experimentation.

## Next proposed action

Create `apps/signalmatter/` and implement one vertical slice:

1. Load one MOABB motor-imagery dataset.
2. Train CSP/LDA and one Braindecode model.
3. Apply one JAX channel-degradation transform.
4. Run a local comparison.
5. Persist the experiment through HSAILabs/core.
6. Display the result in a minimal dashboard.

Do not implement Ray, vLLM, LiveKit, materials adapters, or RL until this single local experiment is reproducible and replayable.
