---
tags: [rag, moc, index]
---

# RAG System — Mapa dokumentacji

## Architektury RAG

| Architektura | Opis | Status |
|---|---|---|
| [[01-baseline-rag\|Baseline Sequential RAG]] | Pojedyncze zapytanie wektorowe, brak kroków pośrednich | zaimplementowana |
| [[02-multi-query-rag\|Multi-Query RAG]] | LLM generuje n wariantów zapytania, wyniki deduplikowane | zaimplementowana |
| [[03-multi-step-rag\|Multi-Step RAG]] | Dekompozycja zapytania, sekwencyjny retrieval kaskadowy | planowana |
| [[04-agentic-rag\|Agentic RAG]] | Agent ReAct iteracyjnie planuje i wykonuje retrieval | planowana |

## Ewaluacja

- [[metryki]] — Recall@k, Precision@k, FPR, Coverage, LLM judge, latency, koszt, stabilność
- [[dataset]] — Dataset TechNova, typologia pytań, rozkład, ground truth
- [[metodologia]] — Projekt eksperymentu, izolacja zmiennej, uzasadnienie metodologiczne

## System

- [[architektura-systemu]] — Komponenty, DI container, warstwy
- [[pipeline]] — Przepływ danych przez każdą architekturę
