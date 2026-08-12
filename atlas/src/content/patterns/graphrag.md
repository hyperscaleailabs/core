---
title: "RAG and GraphRAG: Grounding Agents in Real Knowledge"
description: "Retrieval-augmented generation from vector search to knowledge graphs - how each grounds an agent, when GraphRAG's multi-hop structure is worth the build cost."
level: advanced
readingTime: 9
problem: "Agents need current, private, or domain-specific knowledge the base model doesn't have - and answers grounded in sources, not hallucinated."
alsoKnownAs: [retrieval-augmented-generation, knowledge-graph-rag]
updated: 2026-06-30
tags: [rag, graphrag, retrieval, knowledge-graph, grounding]
sources:
  - title: "Introducing the GraphRAG Toolkit"
    url: "https://aws.amazon.com/blogs/database/introducing-the-graphrag-toolkit/"
    publisher: "AWS"
    accessed: "2026-06-30"
  - title: "GraphRAG Toolkit (GitHub)"
    url: "https://github.com/awslabs/graphrag-toolkit"
    publisher: "AWS Labs"
    license: "Apache-2.0"
    accessed: "2026-06-30"
  - title: "LangChain Documentation"
    url: "https://docs.langchain.com/"
    publisher: "LangChain"
    accessed: "2026-06-30"
---

An agent is only as grounded as the knowledge you put in front of it.
**Retrieval-Augmented Generation (RAG)** fetches relevant external information at
query time and injects it into the context, so the model answers from *your* data
rather than its parametric memory. It's the standard antidote to stale knowledge
and hallucination - and a core [context-engineering](/patterns/context-engineering)
technique.

## Vector RAG: the baseline

The common pipeline:

1. **Ingest** - split documents into chunks.
2. **Embed** - turn chunks into vectors and store them in a vector DB.
3. **Retrieve** - embed the query, fetch the top-k most similar chunks.
4. **Generate** - put those chunks in context and let the model answer, citing
   them.

Frameworks like [LangChain](/frameworks/langchain) provide loaders, splitters,
embeddings, and retrievers for exactly this. Vector RAG is cheap, simple, and the
right default for lookup-style questions.

### Where vector RAG falls short
It retrieves chunks that are *individually* similar to the query but can miss
answers that only emerge from **relationships across documents** - multi-hop
questions like "which services depend on the database that this incident took
down?" No single chunk contains the answer; the connection does.

## GraphRAG: adding structure

**GraphRAG** builds a **knowledge graph** - entities and their relationships -
over the corpus, then retrieves by traversing that structure, optionally combined
with vector search (hybrid retrieval):

1. **Construct** - extract entities and relations from documents into a graph.
2. **Traverse** - follow relationships to gather connected, multi-hop context.
3. **Ground** - feed that structured context to the model.

AWS Labs' [GraphRAG Toolkit](/frameworks/graphrag-toolkit) (Apache-2.0)
operationalizes this, with graph + vector backends and construction/retrieval
pipelines; its [launch
post](https://aws.amazon.com/blogs/database/introducing-the-graphrag-toolkit/)
details the architecture.

## Choosing between them

| Question shape | Prefer |
| --- | --- |
| Fact lookup, "what does the doc say about X" | Vector RAG |
| Multi-hop, "how does X relate to Y across docs" | GraphRAG |
| Rich entity/dependency structure in the corpus | GraphRAG |
| Small/simple corpus, cost-sensitive | Vector RAG |
| Need explainable retrieval paths | GraphRAG |

## Tradeoffs

- **Build & maintenance cost.** Graph construction and upkeep are heavier than
  chunking into a vector store. Justify it with query shape.
- **Infrastructure.** GraphRAG adds graph + search services to run and secure.
- **Quality still depends on ingestion.** Garbage in, garbage retrieved - both
  approaches live or die on chunking/extraction quality.
- **Retrieval is context.** Whatever you retrieve competes for the window; return
  the connected *slice*, not the whole subgraph
  ([context engineering](/patterns/context-engineering)).

## For agents specifically

Expose retrieval as a **tool** the agent calls when it needs grounding, rather
than always front-loading documents. Combined with
[reflection](/patterns/reflection) ("does my answer cite retrieved sources?"),
retrieval-as-a-tool keeps the context lean and answers grounded.

## Next

- [Context engineering](/patterns/context-engineering) - retrieval as one lever.
- [GraphRAG Toolkit](/frameworks/graphrag-toolkit) - a concrete implementation.
