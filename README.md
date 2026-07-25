# Local RAG AI Asistanı

Microsoft Foundry Local ile tamamen offline çalışan, RAG (Retrieval-Augmented Generation) tabanlı bir soru-cevap asistanı.

> Staj programı: Microsoft "Summer School Foundry Local". Detaylı faz-faz proje planı için bkz. [PROJECT_PLAN.md](./PROJECT_PLAN.md).

## Durum

✅ MVP tamamlandı (Faz 1.6) — çalışan, offline, local bir RAG chatbot. Geliştirme devam ediyor, detaylar için [PROJECT_PLAN.md](./PROJECT_PLAN.md).

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
└── interfaces/    # Paylaşılan veri tipleri (ör. Chunk) -- paketler arası ortak sözleşme
```

## Kurulum

```powershell
# Sanal ortami olustur (bir kez)
python -m venv .venv

# Sanal ortami aktif et
.venv\Scripts\Activate.ps1

# Bagimliliklari kur
pip install -r requirements.txt
```

## Kullanım

```powershell
# Foundry Local sunucusunun calistigindan ve modellerin yuklu oldugundan emin ol
foundry server start
foundry model load phi-3.5-mini
foundry model load qwen3-embedding-0.6b

# Bilgi tabanini olustur (ilk kurulumda bir kez)
.venv\Scripts\python.exe scripts\collect_sources.py
.venv\Scripts\python.exe scripts\build_vector_db.py

# Asistani baslat
.venv\Scripts\python.exe main.py
```

Terminalde açılan `Soru:` istemine sorunu yaz, çıkmak için `exit` yaz.
