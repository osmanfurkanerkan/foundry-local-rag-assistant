# Faz 5.2 -- Degerlendirme Raporu

Toplam soru: 20 (14 cevaplanabilir, 6 cevaplanamaz)

## Ozet Metrikler

- **Retrieval hit rate** (dogru kaynak top-3'ta bulundu mu): 93%
- **Faithfulness** (cevap sadece context'e mi dayaniyor): 93%
- **Answer relevancy** (cevap soruyu cevapliyor mu): 93%
- **Correct refusal rate** (cevaplanamaz sorularda dogru 'bulamadim' oranı): 100%

## Cevaplanabilir Sorular

| id | soru | beklenen kaynak | bulunan kaynaklar | hit | faithful | relevant |
|---|---|---|---|---|---|---|
| 1 | What is Foundry Local? | what-is-foundry-local | what-is-foundry-local | OK | YES | YES |
| 2 | Does Foundry Local send any data to Microsoft? | what-is-foundry-local | foundry-local-architecture, what-is-foundry-local | OK | YES | YES |
| 3 | How do I install and run Foundry Local for the first time? | get-started | get-started, reference-cli | OK | YES | YES |
| 4 | What are the prerequisites for getting started with Foundry Local? | get-started | get-started | OK | YES | YES |
| 5 | How does Foundry Local's architecture work internally? | foundry-local-architecture | foundry-local-architecture | OK | YES | YES |
| 6 | What CLI commands does Foundry Local provide? | reference-cli | reference-cli | OK | YES | YES |
| 7 | How do I load a model using the Foundry Local CLI? | reference-cli | (yok) | MISS | NO | NO |
| 8 | What is Retrieval-Augmented Generation (RAG)? | retrieval-augmented-generation | retrieval-augmented-generation, retrieval-augmented-generation-overview | OK | YES | YES |
| 9 | What are the steps involved in a RAG pipeline? | retrieval-augmented-generation | rag-solution-design-and-evaluation-guide, retrieval-augmented-generation | OK | YES | YES |
| 10 | What should I consider when designing and evaluating a RAG solution? | rag-solution-design-and-evaluation-guide | rag-solution-design-and-evaluation-guide | OK | YES | YES |
| 11 | What is an embedding in the context of machine learning? | understand-embeddings | embeddings, understand-embeddings | OK | YES | YES |
| 12 | How is cosine similarity used with embeddings? | understand-embeddings | understand-embeddings | OK | YES | YES |
| 13 | How do I generate embeddings using Azure OpenAI? | embeddings | embeddings | OK | YES | YES |
| 14 | How can I generate embeddings for vector search? | vector-search-how-to-generate-embeddings | vector-search-how-to-generate-embeddings | OK | YES | YES |

## Cevaplanamaz Sorular

| id | soru | bulunan kaynaklar | dogru 'bulamadim' mi |
|---|---|---|---|
| 15 | What is the capital of France? | (yok) | OK |
| 16 | How do I train a custom neural network from scratch using PyTorch? | (yok) | OK |
| 17 | What's the weather forecast for tomorrow? | (yok) | OK |
| 18 | How much does a Tesla Model 3 cost? | (yok) | OK |
| 19 | What is the population of Japan? | (yok) | OK |
| 20 | Can you recommend a good recipe for lasagna? | (yok) | OK |
