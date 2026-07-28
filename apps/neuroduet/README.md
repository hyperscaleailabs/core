---
document: Project Direction
project: NeuroDuet
version: 0.1.0
status: Proposed Golden Application
date: 2026-07-28
---

# NeuroDuet

## Open Language-Aligned BCI Simulation and Evaluation Lab

NeuroDuet is the second application direction of [HSAILabs core](../../README.md);
see [MISSION.md](../../MISSION.md) for the lab mission and
[DIRECTION.md](../../docs/strategic/DIRECTION.md) for the horizons this sits on
(mid: the second application that tests whether core contracts generalize). The
market research behind it lives in
[docs/strategic/20260728-neuroduet/](../../docs/strategic/20260728-neuroduet/).

The compression is to make **the live two-person conversation itself the
benchmark**. The first release visualizes **model-predicted virtual brain
activity**, not the participants’ measured brains.

# 1. Project mission

NeuroDuet is an open scientific application for studying how language can be encoded into, represented within, and reconstructed from learned brain-activity models.

Its first experience is visually simple:

> Two people speak through a LiveKit Meet room while two virtual brain models visualize the predicted cortical response to each utterance.

For every conversational turn, NeuroDuet:

1. Captures the speaker’s audio.
2. Produces a timed transcript.
3. Predicts the listener’s language-related brain activity.
4. Visualizes the predicted cortical response.
5. Reconstructs the semantic content through a brain-latent bottleneck.
6. Compares the reconstruction with the original utterance.
7. Repeats the loop when the participants change roles.

The application is built on HSAILabs/core and creates practical requirements for:

* PyTorch model training.
* JAX numerical simulation.
* Ray-distributed evaluation.
* vLLM and multimodal model serving.
* LiveKit real-time media.
* Experiment provenance.
* Visualization.
* Replay.
* Human-supervised scientific experimentation.

Its long-term objective is:

> Develop open infrastructure for language-aligned brain models, adaptive BCIs, multimodal neural interfaces, and scientific-agent-driven neurotechnology research.

---

# 2. Golden problem

The durable scientific and engineering problem is:

> How can a brain–computer interface preserve semantic information across different people, sessions, devices, and changing neural signals without requiring prohibitively expensive recalibration?

Modern BCI systems face substantial variation across:

* Individuals.
* Recording sessions.
* Sensors.
* Electrode placement.
* Signal quality.
* Tasks.
* Hardware.
* Biological state.

NeuroDuet begins with a simpler, measurable version:

> Can a language-to-brain encoding model preserve enough semantic information that an inverse model can reconstruct the meaning of an utterance after it passes through a participant-specific brain latent?

This creates a visible closed loop:

```text
spoken utterance
      ↓
timed transcript and audio features
      ↓
predicted listener brain activity
      ↓
participant-specific brain latent
      ↓
semantic reconstruction
      ↓
comparison with original utterance
```

---

# 3. Golden application

## Live Two-Brain Dialogue Twin

Two participants join an HSAILabs Meet room.

When Participant A speaks:

```text
Participant A utterance
        ↓
predicted listening response for Virtual Brain B
        ↓
brain activation visualization
        ↓
semantic reconstruction
        ↓
Participant B replies
```

When Participant B replies:

```text
Participant B utterance
        ↓
predicted listening response for Virtual Brain A
        ↓
brain activation visualization
        ↓
semantic reconstruction
        ↓
Participant A replies
```

The conversation continues as a closed loop.

The system displays:

* The current speaker.
* The current listener.
* Timed transcript.
* Predicted cortical activation.
* Reconstructed semantic text.
* Semantic information retained or lost.
* Model confidence.
* Processing latency.
* Subject-model identity.
* Experiment and model versions.

---

# 4. Golden task

> Given a timed conversational utterance, predict the virtual listener’s cortical language response, reconstruct the utterance’s meaning from the predicted brain representation, and visualize the complete process in real time.

The task is evaluated using:

* Encoding accuracy against held-out fMRI.
* Semantic reconstruction similarity.
* Cross-subject generalization.
* Temporal alignment.
* Uncertainty calibration.
* End-to-end latency.
* Reproducibility.

---

# 5. Scientific integrity boundary

The first release does **not** read the live participants’ brains.

The displayed brain activity is:

> A model-predicted response generated from language and audio features using encoding models trained on public neuroimaging data.

NeuroDuet must always distinguish between two operating modes.

## 5.1 Scientific Replay Mode

Uses paired public data:

```text
audio or transcript
        +
measured fMRI/EEG
```

This mode has neural ground truth.

It is used for:

* Training.
* Validation.
* Model comparison.
* Subject adaptation.
* Scientific evaluation.

## 5.2 Live Dialogue Mode

Uses:

```text
live audio
        +
timed transcript
        +
trained encoding model
```

This mode does not have measured brain ground truth.

It demonstrates:

* Real-time inference.
* Virtual-subject simulation.
* Brain visualization.
* Semantic reconstruction.
* Infrastructure.
* Human interaction.

The interface must label results as:

```text
MODEL-PREDICTED VIRTUAL BRAIN ACTIVITY
```

It must not label them as:

```text
PARTICIPANT BRAIN ACTIVITY
```

---

# 6. Open-data foundation

## Initial dataset: natural-language listening fMRI

The strongest initial foundation is the Huth Lab natural-language fMRI dataset. It contains approximately six hours of natural story-listening data for each of eight participants, along with cortical surfaces and code for fitting semantic encoding models. ([Nature][1])

The initial release should use:

* One participant.
* One training-story subset.
* One held-out story.
* A reduced cortical parcellation.
* Precomputed language-model features where practical.

This is enough to establish the complete pipeline without initially processing the entire dataset.

## Scale-out dataset: Narratives

The Narratives collection contains 345 subjects, 891 functional scans, and 27 natural spoken stories totaling approximately 4.6 hours of unique stimuli. It also includes transcript timing information useful for language-aligned modeling. ([Nature][2])

Narratives becomes useful for:

* Ray-distributed subject evaluation.
* Cross-story generalization.
* Cross-site variation.
* Larger virtual-subject populations.

## Multilingual extension

The Le Petit Prince corpus provides multilingual naturalistic fMRI collected while English, Mandarin, and French speakers listened to the same story. This provides a later path toward testing whether the learned brain-language representation transfers across languages. ([Nature][3])

## Future EEG and MEG direction

Brain2Qwerty provides an open implementation for decoding typed sentences from non-invasive EEG and MEG using a convolutional encoder, transformer, and language model. It offers a later path from simulated language-to-brain encoding toward experiments using actual electrophysiological input. ([Nature][4])

---

# 7. Initial model design

## 7.1 Stimulus encoder

Inputs:

* Timed transcript.
* Word or token timestamps.
* Audio embeddings.
* Speaker identity.
* Conversation context.

Possible feature encoders:

* Small open language model.
* Whisper audio representations.
* Sentence-transformer features.
* Hidden states from an open transformer.

The initial model should not require training an LLM from scratch.

## 7.2 Brain encoding model

A PyTorch model maps language and audio features into predicted cortical activity.

Initial output should use approximately 50–200 cortical regions rather than hundreds of thousands of voxels.

```text
language/audio features
        ↓
temporal PyTorch encoder
        ↓
subject adapter
        ↓
cortical parcel activity over time
```

The first baseline may be:

* Ridge regression.
* Linear temporal-response model.
* Small MLP.
* Temporal convolutional network.

The PyTorch version can then be compared with classical encoding baselines.

## 7.3 Virtual-subject adapter

Each public-data participant receives a small learned adapter:

```text
shared language encoder
        +
subject-specific low-rank adapter
```

During the live demonstration, participants choose or are assigned virtual-subject profiles.

For example:

```text
Live Participant A → Virtual Subject 03
Live Participant B → Virtual Subject 07
```

This does not personalize the model to their actual brains.

It demonstrates how subject-specific adaptation could work when paired neural data is available.

## 7.4 Brain-latent decoder

The predicted cortical activity is compressed into a semantic brain latent.

The inverse model reconstructs:

* Semantic embedding.
* Top concepts.
* Intended topic.
* Constrained paraphrase.

```text
predicted cortical parcels
        ↓
PyTorch inverse encoder
        ↓
semantic latent
        ↓
constrained text reconstruction
```

vLLM can serve the final reconstruction model, but it must receive only the predicted semantic evidence and must be instructed to preserve uncertainty rather than invent missing information.

## 7.5 Brain foundation-model comparator

BrainLM is an available open foundation model trained on approximately 6,700 hours of fMRI recordings, with downloadable pretrained weights. It should be evaluated later as a brain-representation comparator rather than made a dependency of the first release. ([Hugging Face][5])

---

# 8. Role of the core technology stack

## PyTorch

PyTorch is the primary learned-model framework.

It owns:

* Language-to-brain encoding.
* Subject adapters.
* Brain-latent reconstruction.
* Fine-tuning.
* Model checkpoints.
* Uncertainty models.
* Optional transformer experiments.

## JAX

JAX owns the fast numerical-simulation layer.

It is used for:

* Hemodynamic-response convolution.
* Temporal alignment.
* Vectorized virtual-subject simulation.
* Noise and signal-drift simulation.
* Parameter sweeps.
* Differentiable subject adaptation.
* Later reinforcement-learning environments.

JAX transformations such as `jit` and `vmap` can be composed to compile and vectorize numerical simulation across many subjects and parameter profiles. ([JAX Documentation][6])

## Ray

Ray owns the distributed training and evaluation control plane.

Evaluation dimensions include:

```text
model checkpoint
× public-data subject
× story
× transcript window
× virtual-subject profile
× noise profile
× random seed
```

Ray supports distributed training workers and provides a natural execution layer for scaling independent subject, story, and experiment workloads. ([Ray][7])

## vLLM

vLLM serves:

* Semantic reconstruction.
* Conversation-context analysis.
* Structured scientific reports.
* Experiment-planning agents.
* Later multimodal language-and-vision models.

vLLM supports serving supported multimodal models and structured inference workflows, allowing the serving layer to expand from text toward audio, images, and video. ([vLLM][8])

## LiveKit Meet

LiveKit provides:

* Two-person audio and video.
* Timed transcriptions.
* Agent participants.
* Brain-visualization tracks.
* Experiment-control data.
* Voice explanations.
* Replay media.

LiveKit supports real-time audio, video, text, and data streams, and programmable agents can participate in rooms alongside human users. ([LiveKit Docs][9])

## Nilearn and visualization

Nilearn provides volume and cortical-surface visualization for neuroimaging data. ([NiLearn][10])

The initial display may be:

* Left and right cortical surfaces.
* Region-level activation.
* Time-series animation.
* Confidence opacity.
* Speaker/listener role overlays.

A later 3D renderer may publish the animated brain as:

* A browser WebGL view.
* A LiveKit video track.
* A UE Pixel Streaming scene.

---

# 9. Ground truth and evaluation

NeuroDuet has two distinct ground-truth layers.

## 9.1 Brain-encoding ground truth

In Scientific Replay Mode:

```text
predicted fMRI activity
        versus
measured held-out fMRI activity
```

Metrics:

* Correlation by cortical region.
* Explained variance.
* Temporal correlation.
* Subject-level generalization.
* Region coverage.
* Calibration.

Voxelwise encoding models are an established approach for predicting fMRI activity from stimulus features, and open tutorials and data exist for implementing them. ([PubMed Central (PMC)][11])

## 9.2 Semantic-loop ground truth

In both replay and live modes:

```text
original utterance
        versus
reconstructed semantic output
```

Metrics:

* Semantic similarity.
* Keyword retention.
* Entity retention.
* Intent retention.
* Contradiction rate.
* Unsupported-detail rate.
* Reconstruction uncertainty.

The goal is not exact transcript recovery in the first release.

The goal is:

> Preserve and reconstruct the core meaning after passing through a learned brain-activity bottleneck.

---

# 10. Minimal Golden demonstration

The first demonstration should last approximately three minutes.

## Step 1: Participants join

Participant A and Participant B enter a NeuroDuet Meet room.

Two virtual brains appear.

## Step 2: Participant A speaks

Example:

> “The rover should inspect the battery before crossing the ridge.”

The system:

* Produces a timed transcript.
* Extracts language and audio features.
* Predicts Virtual Brain B’s response.
* Animates language-related cortical parcels.
* Reconstructs:

> “Inspect the battery before the rover moves through difficult terrain.”

The original and reconstructed meanings are compared.

## Step 3: Participant B replies

Example:

> “Agreed, but it should preserve enough energy to return.”

Virtual Brain A activates.

The reconstructed meaning appears:

> “Preserve a safe return-energy reserve.”

## Step 4: The loop continues

The system shows:

* Which concepts survived.
* Which concepts were lost.
* Differences between Virtual Subject A and B.
* Confidence.
* Processing latency.

## Step 5: Scientific replay

The operator switches to a held-out public fMRI story segment.

The system displays:

* Measured cortical activity.
* Predicted activity.
* Prediction error.
* Reconstruction.
* Model metrics.

This step makes the scientific basis visible and prevents the live simulation from being mistaken for measured BCI data.

---

# 11. Deliverable within days

## Days 1–2: Scientific replay baseline

Deliver:

* One Huth Lab participant.
* One training segment.
* One held-out segment.
* Timed transcript alignment.
* Language embeddings.
* Cortical-region target extraction.
* Linear encoding baseline.
* Static cortical visualization.

Definition of done:

* Transcript segments align with measured fMRI.
* The model predicts held-out cortical activity.
* Metrics are reproducible.
* One command regenerates the result.

## Days 3–4: PyTorch closed loop

Deliver:

* PyTorch encoding model.
* Virtual-subject adapter.
* Brain-latent compression.
* Semantic reconstruction baseline.
* Original-versus-reconstructed comparison.
* Model and dataset manifests.

Definition of done:

* One transcript segment passes through the complete loop.
* Brain activity is visualized.
* Semantic output is reconstructed.
* Artifacts and metrics are preserved through HSAILabs/core.

## Days 5–7: Live Meet demonstration

Deliver:

* Two-person LiveKit room.
* Timed transcript.
* Alternating listener brain visualizations.
* Reconstruction text.
* Experiment timeline.
* Explicit simulated-activity label.
* Replay.

Definition of done:

* Each participant’s utterance activates the other virtual brain.
* The system responds within an acceptable demonstration latency.
* A complete conversation can be replayed.
* The application works with a prerecorded conversation if LiveKit is unavailable.

---

# 12. One-to-two-week technical deliverable

By the end of two weeks:

* PyTorch language-to-brain encoder.
* PyTorch brain-to-semantic decoder.
* JAX hemodynamic and virtual-subject simulation.
* Ray evaluation across multiple subjects and transcript windows.
* vLLM-served constrained reconstruction.
* LiveKit two-person experience.
* Nilearn or browser brain visualization.
* PostgreSQL experiment metadata.
* MinIO artifacts.
* ClickHouse or local analytical results.
* OpenTelemetry metrics.
* Grafana evaluation dashboard.
* Reproducible local k3d deployment.

Suggested evaluation matrix:

```text
2 encoding models
× 4 public subjects
× 3 held-out story segments
× 2 virtual-subject adapters
× 3 noise profiles
× 3 seeds
```

This produces 432 evaluation units, enough to demonstrate distributed evaluation without creating artificial scale.

---

# 13. Six-week direction

By week six, NeuroDuet should support:

## Scientific capabilities

* Multiple public fMRI subjects.
* Narratives dataset adapter.
* Huth dataset adapter.
* Cross-subject transfer.
* Subject-specific low-rank adapters.
* Encoding-model comparison.
* BrainLM representation comparison.
* Uncertainty calibration.
* Signal-drift simulation.
* Model and dataset cards.

## Interactive capabilities

* Two-person live dialogue.
* Voice and video.
* Animated brain surfaces.
* Conversation replay.
* Virtual-subject selection.
* Scientific replay mode.
* Collaborative experiment review.

## Infrastructure capabilities

* Ray-distributed evaluation.
* PyTorch distributed-training option.
* JAX vectorized simulation.
* vLLM inference.
* Kafka event profile.
* ClickHouse metrics.
* Grafana and Superset reports.
* Kubernetes deployment.

## Learning capabilities

* RL policy for deciding when a subject adapter should recalibrate.
* DPO for preferring faithful, uncertain semantic reconstructions over fluent but unsupported ones.
* Scientific agent that proposes the next subject, story, or perturbation experiment.
* Inspectable experiment-planning graph rather than hidden reasoning.

---

# 14. Three-month direction

## Actual neural-input replay

Add:

* EEG and MEG datasets.
* Braindecode or Brain2Qwerty-compatible model adapters.
* Brain-to-text replay.
* Comparison among fMRI, EEG, and MEG representations.
* Temporal-resolution and spatial-resolution tradeoff analysis.

Brain2Qwerty’s open implementation provides a concrete later benchmark for non-invasive sentence decoding from EEG and MEG. ([Nature][4])

## Multimodal dialogue

Add participant video:

```text
speech
+
facial expression
+
objects and visual context
        ↓
multimodal cortical prediction
```

Research has shown that multimodal transformer representations can support brain-encoding models that transfer between language and visual stimuli, providing a reasonable scientific direction for the vision extension. ([PubMed Central (PMC)][12])

## Optional EEG hardware

Add an explicit experimental adapter for:

* OpenBCI.
* BrainFlow.
* Lab Streaming Layer.

Live neural data must be opt-in, locally controlled, and clearly separated from simulated activity.

---

# 15. Six-month direction

NeuroDuet evolves into a neural-interface reliability and adaptation laboratory.

Capabilities:

* Cross-session neural drift.
* Channel loss and noise.
* Participant recalibration.
* Online adaptation.
* Confidence-based abstention.
* Longitudinal virtual subjects.
* Actual EEG replay.
* Real-time EEG development mode.
* Multimodal language, vision, and action tasks.
* Distributed benchmark publication.
* BIDS or NWB-compatible artifacts.

The Golden application remains the same:

> Two participants communicate while the system models, visualizes, reconstructs, and evaluates the neural representation of their dialogue.

The underlying models become more realistic over time.

---

# 16. Twelve-month direction

NeuroDuet develops toward:

* Personalized neural foundation models.
* Language-aligned multimodal BCI.
* Cross-device adaptation.
* Closed-loop assistive communication.
* Neural-interface degradation simulation.
* Device and signal co-design.
* Scientific-agent experiment planning.
* Autonomous neural-interface laboratory orchestration.
* Materials and electrode-profile integration.
* Robotic experiment execution.

The long-term scientific loop becomes:

```text
interface or materials profile
        ↓
signal-generation model
        ↓
language or multimodal brain representation
        ↓
decoder performance
        ↓
adaptation requirement
        ↓
scientific experiment proposal
        ↓
simulated or physical experiment
        ↓
updated device and model profile
```

---

# 17. Core/application boundary

## NeuroDuet owns

* Dialogue experience.
* Brain-language task definitions.
* Virtual-subject profiles.
* Semantic reconstruction metrics.
* Neuroimaging-specific visualization.
* Dataset adapters.
* Scientific assumptions.
* Application UI.

## HSAILabs/core owns

* Dataset and model manifests.
* Training runtime.
* JAX experiment adapter.
* Ray execution.
* vLLM serving.
* LiveKit agent and operator contracts.
* Experiment records.
* Artifact storage.
* Evaluation.
* Replay.
* Observability.
* Release gates.
* Scientific-agent orchestration contracts.

NeuroDuet creates practical requirements.

Core turns repeated requirements into reusable platform capabilities.

---

# 18. Final formulation

## Product

**NeuroDuet**

## Golden application

**Live Two-Brain Dialogue Twin**

## Golden task

> Predict and visualize a virtual listener’s cortical language response to each conversational utterance, reconstruct the meaning through a learned brain latent, and compare the reconstruction with the original speech.

## Immediate technical objective

> Build a reproducible PyTorch, JAX, Ray, vLLM, neuroimaging-visualization, and LiveKit loop using open transcript-aligned fMRI data and demonstrate it through a two-person Meet conversation.

## Six-week objective

> Deliver an open benchmark for language-to-brain encoding, participant-specific adaptation, semantic reconstruction, distributed evaluation, and collaborative scientific replay.

## Long-term objective

> Develop open infrastructure for personalized multimodal BCIs, neural-interface reliability, scientific-agent experiment planning, and autonomous neurotechnology laboratories.

## Guiding statement

> NeuroDuet begins with a model-predicted two-brain conversation that is visually understandable within seconds, scientifically testable against open neuroimaging data, and technically extensible toward real EEG, MEG, multimodal BCIs, neural-interface materials, and closed-loop assistive communication.

The most important first implementation decision is to use **one public fMRI participant and one held-out story segment**, prove the transcript → predicted brain → reconstructed meaning loop, and only then connect it to LiveKit.

[1]: https://www.nature.com/articles/s41597-023-02437-z?utm_source=chatgpt.com "A natural language fMRI dataset for voxelwise encoding ..."
[2]: https://www.nature.com/articles/s41597-021-01033-3?utm_source=chatgpt.com "The “Narratives” fMRI dataset for evaluating models of ..."
[3]: https://www.nature.com/articles/s41597-022-01625-7?utm_source=chatgpt.com "Le Petit Prince multilingual naturalistic fMRI corpus"
[4]: https://www.nature.com/articles/s41593-026-02303-2?utm_source=chatgpt.com "Noninvasive decoding of typed sentences from human ..."
[5]: https://huggingface.co/vandijklab/brainlm?utm_source=chatgpt.com "vandijklab/brainlm · Hugging Face"
[6]: https://docs.jax.dev/en/latest/quickstart.html?utm_source=chatgpt.com "Quickstart: How to think in JAX - JAX documentation"
[7]: https://docs.ray.io/en/latest/train/overview.html?utm_source=chatgpt.com "Ray Train Overview - Ray 2.56.0"
[8]: https://docs.vllm.ai/en/latest/features/multimodal_inputs/?utm_source=chatgpt.com "Multimodal Inputs - vLLM"
[9]: https://docs.livekit.io/frontends/build/media-data/?utm_source=chatgpt.com "Realtime media and data | LiveKit Documentation"
[10]: https://nilearn.github.io/?utm_source=chatgpt.com "Nilearn"
[11]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12319962/?utm_source=chatgpt.com "The Voxelwise Encoding Model framework: A tutorial ... - PMC"
[12]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11250991/?utm_source=chatgpt.com "Brain encoding models based on multimodal transformers can ..."
