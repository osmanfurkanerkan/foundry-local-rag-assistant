# Local RAG AI Asistanı

[![Tests](https://github.com/osmanfurkanerkan/foundry-local-rag-assistant/actions/workflows/test.yml/badge.svg)](https://github.com/osmanfurkanerkan/foundry-local-rag-assistant/actions/workflows/test.yml)

Microsoft **Foundry Local** ile tamamen offline çalışan, hybrid search + reranking + LangGraph tabanlı corrective retrieval kullanan bir RAG (Retrieval-Augmented Generation) soru-cevap asistanı. Bilgi tabanı, Foundry Local / RAG / embedding konularındaki resmi Microsoft Learn dokümantasyonu -- yani "RAG öğrenirken, öğrendiğini öğreten bir RAG asistanı".

> Staj programı: Microsoft "Summer School Foundry Local". Projenin nasıl adım adım (8 fazda) geliştirildiği, karşılaşılan gerçek sorunlar ve alınan mühendislik kararları için bkz. [PROJECT_PLAN.md](./PROJECT_PLAN.md) -- bu README sonucu, o dosya süreci anlatır.

## Öne Çıkan Özellikler

- **Hybrid retrieval**: embedding (anlamsal) + BM25 (anahtar kelime) araması, Reciprocal Rank Fusion ile birleştiriliyor
- **Cross-encoder reranking**: geniş bir aday kümesini daha isabetli bir modelle dar bir top-k'ya süzüyor
- **Akıllı (markdown-aware) chunking**: sabit kelime sayısı yerine başlık/paragraf sınırlarına göre bölüyor
- **Çoklu tur (multi-turn) hafıza**: takip sorularını ("peki ya bu?") geçmişe bakarak bağımsız bir sorguya çeviriyor
- **Kaynak gösterme + dürüst "bilmiyorum"**: her cevap hangi dokümandan geldiğini gösteriyor, bağlam yetersizse halüsinasyon üretmek yerine bunu itiraf ediyor
- **Streaming yanıt**: CLI'da cevap kelime kelime, canlı yazılıyor
- **LangChain/LangGraph tabanlı orkestrasyon**: LLM ve retrieval, LangChain'in standart arayüzleri üzerinden çalışıyor
- **Corrective RAG**: retrieval sonucunu kendi kendine değerlendirip (self-grading) yetersizse farklı bir stratejiyle tekrar deniyor
- **Ölçülmüş kalite**: özel bir LLM-judge değerlendirmesinde %93 retrieval/faithfulness/relevancy, %100 doğru "bulamadım" oranı ([rapor](./data/eval/eval_report.md))
- **FastAPI backend + web arayüzü**: tarayıcıdan kullanılabilen bir sohbet arayüzü
- **pytest regresyon testleri**: her push'ta GitHub Actions ile otomatik çalışıyor

## Mimari

```
Kullanıcı
   │
   ├── CLI (main.py) ──────────────┐
   └── Tarayıcı (static/index.html) ─→ FastAPI (api.py) ─┐
                                                          ▼
                                                   RagPipeline
                                    (rewrite → retrieve → prompt → generate)
                                                          │
                        ┌─────────────────────────────────┼─────────────────────────┐
                        ▼                                 ▼                         ▼
              Hybrid + Rerank Retrieval              Foundry Local LLM        Corrective RAG
        (embedding + BM25, cross-encoder)          (LangChain ChatOpenAI)   (LangGraph, self-grading)
                        │
                        ▼
                    ChromaDB
```

Kod, SOLID prensiplerine uygun, modüler bir `src-layout` ile organize edilmiştir. Her alt paket tek bir sorumluluğu üstlenir ve birbirine somut sınıflar yerine soyut arayüzler (abstract interface) üzerinden bağlanır -- bu sayede örneğin retrieval'ı LangChain'in `BaseRetriever`'ına sarmak ya da LLM'i LangChain'in `ChatOpenAI`'ına taşımak (Faz 4.1), pipeline katmanında tek satır değişiklik gerektirmedi.

```
src/rag_engine/
├── ingestion/     # Doküman okuma, temizleme, chunking (sabit boyut + markdown-aware)
├── embeddings/    # Embedding sağlayıcı arayüzü + implementasyon
├── vectorstore/   # Vektör veritabanı arayüzü + Chroma implementasyonu
├── llm/           # LLM sağlayıcı arayüzü + Foundry Local / LangChain implementasyonları
├── retrieval/     # Retrieval stratejileri (saf embedding, BM25, hybrid, reranked, LangChain adapter)
├── pipeline/      # Orkestrasyon: RagPipeline, CorrectiveRagPipeline, prompt/query rewriting/expansion
└── interfaces/    # Paylaşılan veri tipleri (Chunk, ConversationTurn, RagAnswer)

api.py           # FastAPI backend (POST /ask), web arayüzünü de servis ediyor
main.py          # CLI giriş noktası
static/index.html # Tek dosyalık web sohbet arayüzü
tests/           # pytest paketi (offline birim testler + auto-skip eden entegrasyon testleri)
scripts/         # Veri toplama, DB kurma, benchmark ve değerlendirme scriptleri
```

## Kurulum

**Ön koşul:** [Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/) bilgisayarına kurulu olmalı.

```powershell
# Sanal ortami olustur ve aktif et
python -m venv .venv
.venv\Scripts\Activate.ps1

# Bagimliliklari kur
pip install -r requirements.txt

# Foundry Local sunucusunu baslat, modelleri yukle
foundry server start
foundry model load phi-3.5-mini
foundry model load qwen3-embedding-0.6b

# Bilgi tabanini olustur (ilk kurulumda bir kez)
.venv\Scripts\python.exe scripts\collect_sources.py
.venv\Scripts\python.exe scripts\build_vector_db.py
```

`foundry server status` her başlatmada farklı bir port seçebilir -- gerekirse `FOUNDRY_BASE_URL` ortam değişkeniyle override edilebilir (bkz. `src/rag_engine/config.py`).

## Kullanım

### CLI

```powershell
.venv\Scripts\python.exe main.py
```

Terminalde açılan `Soru:` istemine sorunu yaz, çıkmak için `exit` yaz.

### Web API + tarayıcı arayüzü

```powershell
.venv\Scripts\uvicorn.exe api:app --reload
```

Tarayıcıda `http://127.0.0.1:8000` adresini aç, ya da doğrudan API'yi çağır:

```powershell
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d "{\"question\": \"What is Foundry Local?\"}"
```

### Testler

```powershell
.venv\Scripts\pytest.exe -v
```

Testlerin çoğu (21/24) sahte (fake) LLM/retriever ile sunucu gerektirmeden çalışır; kalan 3'ü gerçek Foundry Local sunucusuna ihtiyaç duyar ve sunucu kapalıysa otomatik atlanır -- bu sayede aynı paket hem yerelde hem CI'da (GitHub Actions) sorunsuz çalışır.

### Değerlendirme

```powershell
.venv\Scripts\python.exe scripts\run_evaluation.py
```

20 soruluk bir sette otomatik metrikler hesaplayıp `data/eval/eval_report.md`'ye yazar.

## Docker

```powershell
docker compose up --build
```

`Dockerfile`/`docker-compose.yml` yazıldı; Foundry Local Windows/Mac'e özgü yerel bir runtime olduğu için container'ın içine paketlenmedi -- container, host'ta çalışan Foundry Local'e ağ üzerinden bağlanır. ⚠️ Bu adım geliştirme ortamında Docker kurulu olmadığı için `build`/`run` ile fiilen doğrulanamadı; detay için [PROJECT_PLAN.md, Faz 6.3](./PROJECT_PLAN.md).

## Proje Hikayesi

Bu proje "her şey ilk seferde çalıştı" hikayesi değil, gerçek sorunların kök nedenine inilip bilinçli kararlar verildiği bir süreç. Birkaç örnek:

- Küçük/quantized yerel modelin (`phi-3.5-mini`) Türkçe girdide tutarsızlaşması -- CLI'nin İngilizce'ye sabitlenmesinden, corrective RAG'ın query expansion adımında "Foundry"yi döküm/inşaat anlamında yorumlamasına kadar dört ayrı yerde tekrar eden bir örüntü
- Chunk boyutu/top-k benchmark'ında dört farklı konfigürasyonun **hepsinin aynı sonucu vermesi** -- sezgiyle değil veriyle karar vermenin somut bir örneği
- RAGAS'ın modern LangChain 1.x yığınıyla bağımlılık çakışması yüzünden kendi LLM-judge değerlendirmesine pivot edilmesi

Tüm bu kararların gerekçesi, her fazın altındaki **Not:** bölümlerinde [PROJECT_PLAN.md](./PROJECT_PLAN.md)'de tutuluyor.

## Lisans

[MIT](./LICENSE)
