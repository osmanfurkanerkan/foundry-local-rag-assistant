# Local RAG AI Asistanı

Microsoft Foundry Local ile tamamen offline çalışan, RAG (Retrieval-Augmented Generation) tabanlı bir soru-cevap asistanı.

> Staj programı: Microsoft "Summer School Foundry Local". Detaylı faz-faz proje planı için bkz. [PROJECT_PLAN.md](./PROJECT_PLAN.md).

## Durum

🚧 Geliştirme aşamasında — Faz 0.1 (proje iskeleti) tamamlandı.

## Mimari

Proje, SOLID prensiplerine uygun, modüler bir `src-layout` ile organize edilmiştir. Her alt paket tek bir sorumluluğu üstlenir ve birbirine somut sınıflar yerine soyut arayüzler (abstract interface) üzerinden bağlanır — böylece örneğin vektör veritabanı (Chroma → FAISS) veya LLM sağlayıcısı değiştirildiğinde diğer modüller etkilenmez.

```
src/rag_engine/
├── ingestion/     # Doküman okuma, temizleme, chunking
├── embeddings/    # Embedding sağlayıcı arayüzü + implementasyonlar
├── vectorstore/   # Vektör veritabanı arayüzü + implementasyonlar
├── llm/           # LLM sağlayıcı arayüzü + implementasyonlar
├── retrieval/     # Retrieval stratejileri (saf, hybrid, reranked)
├── pipeline/      # Yukarıdakileri birleştiren orkestrasyon katmanı
└── interfaces/    # Dışa açılan kapılar: CLI, (ileride) API
```

## Kurulum

_(Faz 0.2'de eklenecek)_

## Kullanım

_(Faz 1.6'da eklenecek)_
