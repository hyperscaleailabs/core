---
title: "AWS Labs GraphRAG Toolkit"
name: "GraphRAG Toolkit"
description: "An open-source toolkit for building graph-based RAG - constructing a knowledge graph from documents and querying it to ground agents with structured context."
level: advanced
readingTime: 6
category: rag
language: [python]
repo: "https://github.com/awslabs/graphrag-toolkit"
homepage: "https://github.com/awslabs/graphrag-toolkit"
docs: "https://github.com/awslabs/graphrag-toolkit"
codeLicense: "Apache-2.0"
maturity: beta
maintainer: "AWS Labs"
supportsMcp: false
supportsMultiAgent: false
updated: 2026-06-30
tags: [rag, graphrag, retrieval, knowledge-graph, aws]
sources:
  - title: "GraphRAG Toolkit (GitHub)"
    url: "https://github.com/awslabs/graphrag-toolkit"
    publisher: "AWS Labs"
    license: "Apache-2.0"
    accessed: "2026-06-30"
  - title: "Introducing the GraphRAG Toolkit"
    url: "https://aws.amazon.com/blogs/database/introducing-the-graphrag-toolkit/"
    publisher: "AWS"
    accessed: "2026-06-30"
---

The **GraphRAG Toolkit** from AWS Labs is an open-source (Apache-2.0) framework
for building **graph-based retrieval-augmented generation**. Instead of retrieving
loose text chunks by vector similarity alone, GraphRAG constructs a **knowledge
graph** - entities and their relationships - from your corpus, then queries that
structure to assemble grounded, connected context for a model.

## Why graphs over chunks

Classic vector RAG retrieves passages that are individually similar to a query but
can miss information that only emerges from **relationships across documents**
("which components depend on the service that failed?"). GraphRAG captures that
structure explicitly:

- **Construction** - extract entities/relations from documents into a graph
  (optionally paired with a vector store for hybrid retrieval).
- **Retrieval** - traverse the graph to gather multi-hop, connected context, not
  just top-k similar chunks.
- **Grounding** - feed that structured context to the model for more complete,
  less hallucination-prone answers.

## What the toolkit provides

- Pipelines for **graph construction** from documents.
- **Storage integrations** for graph and vector backends (commonly AWS services
  such as Neptune and OpenSearch, per the toolkit's design).
- **Query/retrieval** components to combine graph traversal with semantic search.

The [launch blog](https://aws.amazon.com/blogs/database/introducing-the-graphrag-toolkit/)
walks through the architecture and a build.

## When to reach for it

- Your knowledge base has rich cross-document relationships (systems, entities,
  dependencies, org data).
- Vector-only RAG returns plausible-but-incomplete answers on multi-hop questions.
- You're on AWS and want managed graph/vector backends.

## Tradeoffs

- **Build cost.** Graph construction and maintenance are heavier than dropping
  chunks into a vector store; justified when relationships matter.
- **Infrastructure.** Adds graph and search services to operate and secure.
- **Not always needed.** For simple lookup-style retrieval, plain vector RAG is
  cheaper and simpler - choose based on the query shape.

## See also

- [RAG & GraphRAG patterns](/patterns/graphrag) - the concepts behind the toolkit.
- [Framework comparison matrix](/comparisons/framework-matrix)
