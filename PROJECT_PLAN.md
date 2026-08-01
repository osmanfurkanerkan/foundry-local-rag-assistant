# Local RAG AI Asistanı — Staj Proje Planı

**Program:** Microsoft "Summer School Foundry Local"
**Seviye:** Sıfırdan başlayan stajyer (3. sınıf Bilgisayar Mühendisliği öğrencisi)
**Hedef:** Sağlam bir temel RAG projesini bitirip, üstüne mühendislik derinliği katan ileri özelliklerle portfolyoda parlayacak bir proje çıkarmak
**Süre:** Esnek — önemli olan derinlik ve öğrenme, hız değil

---

## 0. Bu Doküman Nasıl Kullanılır?

Bu plan **çok küçük, tek tek anlaşılabilir fazlara** bölünmüştür. Her faz şu kalıpta:

- **Amaç:** Bu fazda ne başarıyoruz?
- **Neden önemli:** Bu adım olmadan ne eksik kalırdı? (Kavramı gerçekten anlaman için)
- **Yapılacaklar:** Somut adımlar
- **Teknoloji:** Kullanılacak araçlar
- **Çıktı / Milestone:** Fazın bitti sayılması için elde olması gereken şey

Fazları sırayla, birini bitirmeden diğerine geçmeden ilerle. Her faz bitince bir sonraki konuşmada "Faz X.Y bitti, sırada ne var" de — birlikte kod yazıp ilerleriz.

---

## 1. Proje Özeti (Hatırlatma)

**RAG (Retrieval-Augmented Generation):** Bir LLM'e soru sormadan önce, kendi doküman koleksiyonundan alakalı parçaları bulup (retrieve), bunları prompt'a ekleyip (augment), sonra modelin bu bağlamla cevap üretmesini (generate) sağlayan yöntem. Sonuç: daha doğru, kaynak gösterilebilir, halüsinasyon riski düşük cevaplar.

**Foundry Local:** Microsoft'un, modeli tamamen kullanıcının bilgisayarında (internet gerekmeden) çalıştıran yerel AI runtime'ı. Bu projede LLM ve embedding modeli buradan çalışacak.

**Senaryo (varsayılan, değiştirilebilir):** Asistanın bilgi tabanı = Foundry Local / RAG / Azure AI'ın resmi Microsoft Learn dokümantasyonu. Yani "RAG öğrenirken, öğrendiğini öğreten bir RAG asistanı" yapıyoruz. Faz 4'te ikinci bir kaynak (kendi ders notların) eklenip bir "router" ile genişletilebilir.

**Mimari (yüksek seviye):**
```
Kullanıcı Sorusu
     │
     ▼
[Retrieval] ──► Vektör DB'den en alakalı doküman parçalarını bul
     │
     ▼
[Augment] ──► Soruyu + bulunan parçaları tek bir prompt'a birleştir
     │
     ▼
[Generate] ──► Foundry Local LLM'i bu prompt'la cevap üretir
     │
     ▼
Kullanıcıya Cevap (+ kaynak gösterimi)
```

---

## FAZ 0 — Ortam Kurulumu ve Temel Kavramlar

### Faz 0.1 — Proje İskeleti ve Git

- **Amaç:** Düzenli, versiyon kontrollü bir proje klasörü kurmak.
- **Neden önemli:** Profesyonel her proje git ile başlar; staj sonunda kodun bir GitHub repo'su olarak sunulacak.
- **Yapılacaklar:**
  - `RAG_project` klasöründe `git init`
  - `.gitignore` oluştur (venv, __pycache__, .env, model dosyaları vb.)
  - `README.md` iskeleti (şimdilik boş başlık)
  - Klasör yapısı: `src/`, `data/`, `tests/`, `notebooks/` (deneyler için)
- **Teknoloji:** Git, klasör organizasyonu
- **Çıktı:** İlk commit atılmış, temiz bir proje iskeleti

### Faz 0.2 — Python Ortamı

- **Amaç:** İzole, tekrarlanabilir bir Python ortamı kurmak.
- **Neden önemli:** Farklı projelerin farklı kütüphane versiyonları çakışmasın; "benim bilgisayarımda çalışıyordu" sorununu önler.
- **Yapılacaklar:**
  - Python sanal ortamı oluştur (`venv`)
  - `requirements.txt` başlat
- **Teknoloji:** `venv` veya `conda`
- **Çıktı:** Aktif, izole bir Python ortamı

### Faz 0.3 — Foundry Local Kurulumu ve "Hello Model" Testi

- **Amaç:** Foundry Local'ı bilgisayarına kurup, ilk yerel model çıktısını almak.
- **Neden önemli:** Projenin can damarı bu runtime; en baştan çalıştığını doğrulamazsan sonraki her şey ona bağlı kalır.
- **Yapılacaklar:**
  - Foundry Local SDK kurulumu (`pip install foundry-local-sdk`)
  - Küçük bir modeli (örn. phi-3.5-mini) indirip yükle
  - Basit bir Python scriptiyle "Merhaba" gibi bir prompt'a cevap al
- **Teknoloji:** Foundry Local SDK
- **Çıktı:** Terminalde çalışan, yerel modelden gelen bir cevap

### Faz 0.4 — Embedding Kavramını Elle Keşfetme

- **Amaç:** Vektör DB'ye geçmeden önce, embedding ve benzerlik hesabının ne olduğunu saf Python ile anlamak.
- **Neden önemli:** Bir sonraki fazda kütüphaneler (Chroma vb.) bu işi senin yerine yapacak — ama "kaputun altında" ne olduğunu bilmeden kullanmak, hata ayıklamayı imkansız hale getirir.
- **Yapılacaklar:**
  - 5-6 örnek cümleyi Foundry Local'ın embedding modeliyle vektöre çevir
  - Bir soru cümlesini de vektöre çevir
  - Cosine similarity'yi elle (numpy ile) hesaplayıp en yakın cümleyi bul
- **Teknoloji:** Foundry Local embedding API, numpy
- **Çıktı:** Çalışan bir `mini_similarity_demo.py` — "en benzer cümle bu" diyebilen basit bir script

---

## FAZ 1 — Minimum Çalışan RAG (MVP)

### Faz 1.1 — Kaynak Dokümanları Toplama

- **Amaç:** Bilgi tabanını oluşturacak gerçek dokümanları toplamak.
- **Neden önemli:** RAG'ın kalitesi büyük ölçüde veri kalitesine bağlı; "garbage in, garbage out".
- **Yapılacaklar:**
  - Microsoft Learn'den 8-12 sayfa (Foundry Local, RAG kavramları, embedding, Azure AI temelleri) seç
  - Bunları markdown/text olarak `data/raw/` altına kaydet
- **Teknoloji:** Manuel toplama veya basit bir web scraping scripti
- **Çıktı:** `data/raw/` klasöründe 8-12 doküman

### Faz 1.2 — Doküman Temizleme ve Chunking

- **Amaç:** Ham metni, aramaya uygun küçük parçalara (chunk) bölmek.
- **Neden önemli:** Modele bütün bir dokümanı vermek hem pahalı hem gürültülü; küçük, anlamlı parçalar retrieval'ı çok iyileştirir.
- **Yapılacaklar:**
  - Metin temizleme (fazla boşluk, gereksiz karakterler)
  - Sabit boyutlu chunking (örn. ~300 kelime, biraz overlap ile) — basit başlangıç
- **Teknoloji:** Python string işlemleri, (opsiyonel) `langchain-text-splitters`
- **Çıktı:** Her biri kaynak dokümanı, chunk id'si ve metnini içeren bir chunk listesi

### Faz 1.3 — Embedding Üretimi ve Vektör DB'ye Yazma

- **Amaç:** Her chunk için embedding üretip kalıcı bir vektör veritabanına kaydetmek.
- **Neden önemli:** Faz 0.4'te elle yaptığımız işi artık ölçeklenebilir, kalıcı hale getiriyoruz.
- **Yapılacaklar:**
  - **Chroma** vektör veritabanını kur (dokümandaki SQLite + brute-force yerine, gerçek bir ANN index kullanan modern araç)
  - Her chunk'ı embed edip Chroma'ya yaz (metin + embedding + kaynak metadata'sı)
- **Teknoloji:** Foundry Local embedding API, ChromaDB
- **Çıktı:** Doldurulmuş bir Chroma koleksiyonu, `python check_db.py` ile kaç chunk olduğunu doğrulama

### Faz 1.4 — Retrieval Fonksiyonu

- **Amaç:** Bir kullanıcı sorusu için en alakalı chunk'ları bulan fonksiyonu yazmak.
- **Neden önemli:** Bu, RAG'ın "R" (Retrieve) kısmı — sistemin kalbi.
- **Yapılacaklar:**
  - `get_top_chunks(query: str, k: int) -> list[Chunk]` fonksiyonunu yaz
  - Birkaç örnek soru ile test et, dönen chunk'ların gerçekten alakalı olup olmadığını manuel kontrol et
- **Teknoloji:** ChromaDB query API
- **Çıktı:** Test edilmiş, mantıklı sonuçlar döndüren retrieval fonksiyonu

### Faz 1.5 — Prompt Şablonu ve Generate

- **Amaç:** Bulunan bağlamı ve soruyu birleştirip modele gönderecek prompt yapısını kurmak.
- **Neden önemli:** İyi bir sistem promptu olmadan model context'i yok sayabilir ya da halüsinasyon yapabilir.
- **Yapılacaklar:**
  - Sistem promptu yaz: "Sadece verilen bağlamı kullan, bilmiyorsan bilmediğini söyle"
  - `answer_query(question)` fonksiyonu: retrieval + prompt oluşturma + Foundry Local chat çağrısı
- **Teknoloji:** Foundry Local chat completion API
- **Çıktı:** Uçtan uca çalışan, bir soruya bağlamlı cevap veren fonksiyon
- **Not (model kısıtı):** `phi-3.5-mini`, Türkçe soru metnini ayrıştırırken tutarsız/hatalı davranıyor (bazen tamamen anlamsız çıktı, bazen alakalı bağlamı görmezden gelip "bulamadım" diyor). İngilizce soru + İngilizce cevapta tamamen güvenilir. Bu yüzden sistem promptu "her zaman İngilizce cevap ver" şeklinde sabitlendi; asistanın birincil çalışma dili İngilizce. İleride (Faz 2+) daha güçlü/çok dilli bir model denenebilir.

### Faz 1.6 — CLI Arayüzü ve İlk Uçtan Uca Test (MVP Milestone 🎉)

- **Amaç:** Terminalden soru sorup cevap alabilen basit bir arayüz.
- **Neden önemli:** Bu, projenin ilk "gerçekten çalışıyor" anı — buradan sonrası hep iyileştirme.
- **Yapılacaklar:**
  - `main.py` içinde `while True: input() -> answer_query() -> print()` döngüsü
  - 5-10 farklı soruyla dene, sonuçları gözlemle
- **Teknoloji:** Python
- **Çıktı:** **MVP tamamlandı** — çalışan, offline, local bir RAG chatbotu

---

## FAZ 2 — Retrieval Kalitesini Yükseltme

### Faz 2.1 — Hybrid Search (BM25 + Embedding)

- **Amaç:** Sadece anlamsal (embedding) değil, anahtar kelime bazlı (BM25) aramayı da birleştirmek.
- **Neden önemli:** Embedding aramaları bazen tam terim eşleşmelerini (özel isim, kod, kısaltma) kaçırabilir; BM25 bunu tamamlar. İkisinin birleşimi endüstri standardı.
- **Yapılacaklar:**
  - `rank_bm25` ile basit bir keyword index kur
  - BM25 ve embedding sonuçlarını birleştiren bir skorlama (örn. reciprocal rank fusion) yaz
- **Teknoloji:** `rank_bm25`
- **Çıktı:** Hybrid retrieval fonksiyonu, önceki saf embedding sonuçlarıyla karşılaştırma
- **Not:** `scripts/test_retrieval.py` ile 4 örnek soruda saf embedding vs hybrid (RRF) karşılaştırıldı. En net fark: "Foundry Local CLI ile bir modeli nasıl yüklerim?" sorusunda saf embedding genel sayfaları (`what-is-foundry-local`, `foundry-local-architecture`) öne çıkarırken, hybrid arama BM25'in "CLI" kelime eşleşmesi sayesinde doğrudan `reference-cli` sayfasını 1. sıraya taşıdı — embedding'in kaçırdığı tam terim eşleşmesini BM25'in tamamladığının somut kanıtı.

### Faz 2.2 — Reranking (Cross-Encoder)

- **Amaç:** İlk aramadan gelen top-N sonucu, daha güçlü ama daha yavaş bir modelle yeniden sıralamak.
- **Neden önemli:** Embedding araması hızlı ama kaba; cross-encoder daha yavaş ama çok daha isabetli. İkisini birleştirmek (geniş ara + dar süz) modern RAG sistemlerinin standart deseni.
- **Yapılacaklar:**
  - Yerel bir cross-encoder modeli (`sentence-transformers` reranker) entegre et
  - Top-10 sonucu al, rerank ile top-3'e indir
- **Teknoloji:** `sentence-transformers`
- **Çıktı:** Rerank öncesi/sonrası sonuçları karşılaştıran küçük bir test scripti
- **Not:** `scripts/test_retrieval.py`'ye üçüncü bir karşılaştırma sütunu eklendi (embedding / hybrid / hybrid+rerank). Sonuç karışık: bazı sorularda rerank belirgin şekilde iyileştirdi (örn. "cosine similarity" sorusunda tanımı içeren chunk'ı 1. sıraya taşıdı), bazılarında ise daha az alakalı bir chunk'ı öne çıkardı (CLI sorusu). Olası neden: `cross-encoder/ms-marco-MiniLM-L-6-v2` İngilizce MS MARCO verisiyle eğitilmiş; Türkçe soru + İngilizce doküman kombinasyonunda Faz 1.5'te LLM'de görülen cross-lingual zorlukla benzer bir sinyal olabilir. İleride İngilizce sorularla da test edilip karşılaştırılabilir.

### Faz 2.3 — Akıllı (Semantic) Chunking

- **Amaç:** Sabit boyut yerine, anlam sınırlarına göre chunk'lama.
- **Neden önemli:** Sabit boyut bazen bir cümleyi ya da fikri ortadan böler, retrieval kalitesini düşürür.
- **Yapılacaklar:**
  - Başlık/paragraf sınırlarına göre bölme stratejisi dene
  - Eski (sabit boyut) ve yeni chunking sonuçlarını karşılaştır
- **Teknoloji:** `langchain-text-splitters` (semantic/markdown splitter)
- **Çıktı:** Güncellenmiş, daha kaliteli chunk seti
- **Not:** `scripts/compare_chunking.py` ile eski (`FixedSizeChunker`, kelime bazlı) ve yeni (`MarkdownChunker`, başlık+paragraf bazlı) karşılaştırıldı: 55 chunk → 137 chunk. Artış beklenen bir sonuç -- markdown dokümanlarındaki her `###` alt-başlık artık kendi chunk'ı oluyor (örn. `reference-cli` 9→23, `get-started` 8→27), yani her chunk daha küçük ama daha net bir konu birimini temsil ediyor. Bilgi tabanı bu chunker ile yeniden inşa edildi (`chroma_db` silinip `build_vector_db.py` tekrar çalıştırıldı); uçtan uca pipeline testi sorunsuz, hatta daha zengin detaylı cevaplar üretti.

### Faz 2.4 — Mini Benchmark: Chunk Boyutu ve Top-K Deneyleri

- **Amaç:** Farklı chunk boyutu / top-k değerlerinin cevap kalitesine etkisini sistematik ölçmek.
- **Neden önemli:** "Sezgiyle" değil, veriyle karar vermeyi öğrenmek — gerçek mühendislik pratiği.
- **Yapılacaklar:**
  - 3-4 farklı konfigürasyon dene, aynı soru setiyle test et
  - Sonuçları basit bir tabloya/log dosyasına yaz
- **Teknoloji:** Python, basit loglama
- **Çıktı:** Hangi konfigürasyonun en iyi sonucu verdiğine dair kısa bir bulgu notu
- **Not:** `scripts/benchmark_chunk_topk.py` ile 9 soruluk elle etiketlenmiş bir eval seti (soru → beklenen kaynak doküman) üzerinden, 4 chunk_size/top-k konfigürasyonunda saf embedding retrieval hit rate'i ölçüldü. **Sonuç: tüm konfigürasyonlarda hit rate aynı (%89, 8/9)** — chunk boyutunu (800/1500/2500) veya k'yı (3/5) değiştirmenin bu küçük test setinde ölçülebilir bir etkisi olmadı. Sebep araştırıldı: sürekli kaçırılan tek soru ("Foundry Local'i nasıl kurar ve çalıştırırım?") `get-started` yerine hep `what-is-foundry-local`/`foundry-local-architecture`'ı buluyor — bu bir chunk boyutu sorunu değil, bu üç dokümanın konu olarak birbirine çok yakın olması (embedding uzayında ayrışmalarının zor olması). Bulgu: bu ölçekte (10 doküman, 137 chunk) chunk_size/k ayarı retrieval kalitesinin darboğazı değil; asıl kazanç zaten yapılmış olan hybrid search + reranking'den (Faz 2.1/2.2) geliyor. Daha büyük/çeşitli bir bilgi tabanında bu deneyin tekrarlanması farklı sonuç verebilir.

---

## FAZ 3 — Konuşma Deneyimi

### Faz 3.1 — Çoklu Tur (Multi-turn) Hafıza

- **Amaç:** Asistanın önceki soru-cevapları hatırlayıp bağlam içinde takip sorularını anlaması.
- **Neden önemli:** Gerçek kullanıcılar tek soru sormaz; "peki ya bu?" gibi takip soruları RAG'ın büyük bir zorluğudur (referans çözümleme).
- **Yapılacaklar:**
  - Konuşma geçmişini bir liste olarak tut
  - Takip sorularını, geçmişe bakarak yeniden ifade etme (query rewriting'in basit hali)
- **Teknoloji:** Python, Foundry Local chat API
- **Çıktı:** "Bu konuda daha fazla bilgi var mı?" gibi takip sorularını doğru işleyen asistan
- **Not:** `interfaces/models.py`'a `ConversationTurn(question, answer)` eklendi; `main.py` konuşma geçmişini bir listede tutup (son `HISTORY_LIMIT=5` tur) her `answer_query` çağrısına geçiyor. Yeni `pipeline/query_rewriter.py`, geçmiş varsa retrieval'dan önce LLM'e takip sorusunu ("peki ya X" gibi zamir/referans içeren) bağımsız bir arama sorgusuna çevirtiyor (basit query rewriting); geçmiş boşsa (ilk soru) bu adım atlanıp gereksiz bir LLM çağrısından kaçınılıyor. Ayrıca `prompt_builder.build_prompt` da geçmişi cevap üretim promptuna dahil ediyor, böylece model hem retrieval hem cevap aşamasında önceki turu görebiliyor. Uçtan uca test: "What is Foundry Local?" sonrası "How does its architecture work?" sorusu doğru şekilde Foundry Local'in mimarisiyle ilgili chunk'ları buldu ve isabetli cevap üretti — "its" zamiri geçmişten doğru çözümlendi.

### Faz 3.2 — Kaynak Gösterme ve "Bilmiyorum" Davranışı

- **Amaç:** Her cevapta hangi dokümandan geldiğini göstermek; bağlam yetersizse dürüstçe "bilmiyorum" demek.
- **Neden önemli:** RAG'ın en büyük avantajı budur — kaynağı belirsiz, halüsinasyonlu cevaplara karşı güven inşa eder.
- **Yapılacaklar:**
  - Her chunk'a kaynak/başlık metadata'sı ekle (Faz 1.3'te zaten kaydedilmişti, burada kullan)
  - Cevabın sonuna "Kaynak: ..." ekle
  - Prompt'a "bağlam yetersizse bilmediğini söyle" talimatını güçlendir, test et
- **Teknoloji:** Prompt engineering
- **Çıktı:** Kaynaklı cevaplar veren, bilmediğini itiraf edebilen asistan
- **Not:** `interfaces/models.py`'a `RagAnswer(text, sources)` eklendi; `RagPipeline.answer_query` artık ham string yerine bunu dönüyor. `prompt_builder.py`'da `NOT_FOUND_MESSAGE` sabit, tam kelimesi kelimesine bir cümle olarak tanımlandı ("I could not find this in the available documents.") ve sistem talimatı "context yetersizse SADECE bu cümleyle cevap ver" şeklinde güçlendirildi. `RagPipeline`, cevapta bu cümle geçiyorsa kaynak listesini boş bırakıyor (sahte kaynak göstermemek için), geçmiyorsa retrieval'da kullanılan chunk'ların kaynaklarını (`chunk.source`, tekilleştirilmiş) döndürüyor. Uçtan uca test: "What is Foundry Local?" → cevap + `Kaynak: what-is-foundry-local`; "What is the capital of France?" (bilgi tabanında hiç yok) → tam olarak "I could not find this in the available documents." ve kaynak satırı yok.

### Faz 3.3 — Streaming Yanıt

- **Amaç:** Cevabın kelime kelime, canlı şekilde ekrana yazılması.
- **Neden önemli:** Kullanıcı deneyimini büyük ölçüde iyileştirir (ChatGPT tarzı his); teknik olarak stream API kullanmayı öğretir.
- **Yapılacaklar:**
  - Foundry Local'ın streaming chat API'sini kullan
  - CLI'da kelime kelime yazdırma
- **Teknoloji:** Foundry Local streaming API
- **Çıktı:** Akıcı, canlı yazan bir CLI deneyimi
- **Not:** `LLMProvider`'a `generate_stream(prompt) -> Iterator[str]` soyut metodu eklendi; `FoundryLocalProvider` bunu `stream=True` ile OpenAI-uyumlu chat completions çağrısı üzerinden uyguluyor. `RagPipeline`'a `answer_query_stream` eklendi -- retrieval/prompt hazırlığını (`_prepare`) `answer_query` ile paylaşıyor, `(iterator, get_sources)` çifti döndürüyor; kaynak listesi ancak akış tamamen tüketilip tam metin toplandıktan sonra hesaplanabiliyor (NOT_FOUND_MESSAGE kontrolü tam cümleye ihtiyaç duyuyor). `main.py` artık `answer_query` yerine bunu kullanıp parçaları geldikçe basıyor. Test sırasında gerçek bir hata yakalandı: Foundry Local'in stream'indeki son chunk (usage bilgisiyle) boş bir `choices` listesi taşıyor, `chunk.choices[0]` bu yüzden `IndexError` veriyordu -- `if not chunk.choices: continue` ile düzeltildi.

---

## FAZ 4 — Agentic RAG

### Faz 4.1 — LangChain/LangGraph'e Geçiş

- **Amaç:** Şimdiye kadar elle yazdığımız pipeline'ı, endüstri standardı bir orkestrasyon kütüphanesine taşımak.
- **Neden önemli:** LangChain/LangGraph CV'lerde en çok aranan RAG araçlarından; kodun daha modüler, test edilebilir hale gelmesini sağlar.
- **Yapılacaklar:**
  - Retrieval + prompt + generate adımlarını LangChain "chain" yapısına taşı
  - Foundry Local'ı LangChain'in LLM arayüzüne bağla (custom wrapper gerekebilir)
- **Teknoloji:** LangChain
- **Çıktı:** Aynı davranışı gösteren, ama LangChain üzerinde çalışan pipeline
- **Not:** Beklenenin aksine custom bir LLM wrapper'a gerek kalmadı -- Foundry Local zaten OpenAI-uyumlu bir REST servisi olduğu için LangChain'in standart `ChatOpenAI`'ı (`langchain-openai`) `base_url` override edilerek doğrudan kullanılabildi. `llm/langchain_foundry_provider.py`: `LangchainFoundryProvider`, generate/prompt adımını bir LCEL zinciri (`prompt | llm | StrOutputParser()`) olarak kuruyor, `LLMProvider` arayüzünü koruyor. `retrieval/langchain_retriever_adapter.py`: `LangchainRetrieverAdapter`, Faz 2'nin hybrid+rerank yığınını (`RerankingRetriever`) hiç değiştirmeden LangChain'in `BaseRetriever` sınıfına sarıyor -- hem `get_top_chunks` (kendi `RetrievalStrategy` sözleşmemiz, RagPipeline bunu kullanıyor) hem `invoke()` (saf LangChain yolu) ile çalışabiliyor. `main.py` bu ikisini kullanacak şekilde güncellendi; Dependency Inversion sayesinde `RagPipeline`, `query_rewriter` gibi Faz 3 kodlarında hiçbir değişiklik gerekmedi. Uçtan uca test: multi-turn takip sorusu, kaynak gösterimi ve "bilmiyorum" davranışı LangChain üzerinden de birebir aynı çalıştı.

### Faz 4.2 — Query Rewriting

- **Amaç:** Kullanıcının kötü ifade edilmiş/belirsiz sorusunu, arama öncesi modelin kendisinin düzeltmesi.
- **Neden önemli:** Gerçek kullanıcı soruları nadiren "mükemmel arama sorgusu" gibi yazılır; bu adım retrieval kalitesini ciddi artırır.
- **Yapılacaklar:**
  - Aramadan önce küçük bir LLM çağrısıyla soruyu yeniden yaz/genişlet
  - Öncesi/sonrası retrieval sonuçlarını karşılaştır
- **Teknoloji:** LangChain, Foundry Local
- **Çıktı:** Query rewriting açık/kapalı iki modun karşılaştırmalı testi
- **Not:** `pipeline/query_expansion.py`'da `expand_query`, sorguyu (Faz 3.1'in takip-sorusu çözümlemesinden bağımsız olarak) LLM ile daha aramaya elverişli hale getirmeye çalışıyor. `RagPipeline`'a opt-in bir `use_query_expansion` bayrağı eklendi (varsayılan kapalı). `scripts/test_query_expansion.py` ile 4 kasıtlı belirsiz/gündelik sorguda (örn. "how do i get this thing running on my machine?", "whats RAG") açık/kapalı karşılaştırıldı: **sonuç karışık, bazen belirgin şekilde kötüleşti.** "how do i get this thing running on my machine?" ham haliyle doğru şekilde `get-started` sayfasını buluyorken, genişletilmiş hali ("install and configure the software application...") bunu tamamen kaçırdı -- model "this thing"i Foundry Local'e özgü bağlamdan koparıp genel bir ifadeye çevirmiş. Daha çarpıcısı: "whats RAG" sorgusu genişletilirken küçük model "RAG" kısaltmasını "Retrieval-Augmented Generation" yerine "Reactive Agent Granularity" diye **yanlış açtı** -- yine de retrieval sonuçları rastlantısal olarak hâlâ doğru kaynaklara isabet etti. Bu, Faz 1.5/2.2'de görülen "küçük/yerel modelin belirsiz görevlerde tutarsız davranması" örüntüsünün bir tekrarı. Bulgu: bu adımı varsayılan olarak kapalı bırakmak (opt-in) doğru tasarım kararıydı -- her sorguya ekstra bir LLM çağrısı eklemenin hem gecikme hem de bazen kalite maliyeti var, kazancı garanti değil.

### Faz 4.3 — Corrective RAG (Self-Grading Retrieval)

- **Amaç:** Sistemin, bulduğu chunk'ların soruyu cevaplamaya yeterli olup olmadığını kendi değerlendirmesi; yetersizse farklı bir strateji denemesi.
- **Neden önemli:** Bu, "akıllı" RAG ile "sabit boru hattı" RAG arasındaki farkı yaratan ileri seviye bir teknik (agentic davranış).
- **Yapılacaklar:**
  - Retrieval sonrası bir "grading" adımı ekle: model chunk'ların alakalı olup olmadığını puanlasın
  - Yetersizse: query rewriting'i tekrar dene veya top-k'yı artır
- **Teknoloji:** LangGraph (döngüsel/koşullu akışlar için)
- **Çıktı:** Zayıf sonuçlarda kendini düzelten bir retrieval döngüsü
- **Not:** `pipeline/corrective_rag_pipeline.py`: LangGraph ile `rewrite -> retrieve -> grade -> (yeterli: generate) | (yetersiz: bump_attempt -> rewrite)` akışı kuruldu. Grading, chunk'ların soruyu cevaplamaya yeterli olup olmadığını LLM'e YES/NO sordurarak yapılıyor; yetersizse Faz 4.2'nin `expand_query`'si "farklı strateji" olarak kullanılıp k artırılıyor (en fazla 2 deneme). `scripts/test_corrective_rag.py`, Faz 2.4'te bulunan zayıf noktayı (get-started/what-is-foundry-local/architecture konu örtüşmesi) bilinçli olarak k=1 ile tetikleyip `.stream()` ile adım adım gözlemliyor. **Gerçek test sonucu çok öğretici:** 1. denemede (k=1) bulunan tek chunk doğru şekilde "yetersiz" bulundu; retry'de `expand_query`, Türkçe soruyu ("Foundry Local'i nasıl kurar ve çalıştırırım?") **"Foundry"yi kelimenin düz anlamıyla (döküm/inşaat ustalığı) yorumlayıp** "Investigate the condition of Foundry Local's brickwork and masonry..." gibi tamamen alakasız bir sorguya çevirdi -- Faz 1.5/2.2'de görülen "küçük yerel modelin Türkçe girdide tutarsızlaşması" örüntüsünün belki de en çarpıcı tekrarı. Buna rağmen hybrid retrieval (BM25 katmanı sayesinde) yine de konuyla ilgili chunk'lar buldu, ama grading bunları da "yetersiz" olarak işaretledi (haklı olarak -- getirilen parçalar kurulum adımları değil, "related content" link listeleriydi). 2 deneme hakkı tükenince sistem **halüsinasyon üretmek yerine dürüstçe "I could not find this in the available documents." dedi** -- Faz 3.2'nin dürüstlük mekanizmasının tam da tasarlandığı gibi devreye girdiği, olumlu bir sonuç.

### Faz 4.4 — (Opsiyonel Stretch) Multi-Corpus Router

- **Amaç:** İkinci bir bilgi kaynağı (örn. kendi ders notların) ekleyip, sistemin hangi kaynağa bakacağına kendisinin karar vermesi.
- **Neden önemli:** Gerçek dünya sistemleri genelde tek kaynaklı değildir; bu, projenin kişisel dokunuşunu da katıyor (Senaryo B'yi buraya entegre ediyoruz).
- **Yapılacaklar:**
  - İkinci bir Chroma koleksiyonu oluştur (kişisel notlar)
  - Basit bir "router" promptu: soru hangi kaynağa daha yakın, oraya yönlendir
- **Teknoloji:** LangGraph
- **Çıktı:** İki farklı kaynak arasında akıllıca seçim yapabilen asistan
- **Not:** Opsiyonel/stretch olarak işaretlendiği için şimdilik ertelendi -- ikinci koleksiyon için gerçek bir içerik (kişisel ders notları/CV vb.) gerekiyor, sentetik bir placeholder yerine gerçek içerikle yapılması tercih edildi. Faz 5'e geçildi, buraya daha sonra dönülebilir.

---

## FAZ 5 — Değerlendirme (Evaluation)

### Faz 5.1 — Test Soru Seti Oluşturma

- **Amaç:** Sistemin kalitesini ölçmek için standart bir soru-cevap seti hazırlamak.
- **Neden önemli:** "Bence iyi çalışıyor" yerine ölçülebilir kanıt sunmak — staj değerlendirmesinde büyük fark yaratır.
- **Yapılacaklar:**
  - 15-20 soru hazırla: bir kısmı dokümanlardan kolayca cevaplanabilir, bir kısmı kasıtlı olarak cevaplanamaz
  - Her soru için "beklenen davranış" not et
- **Teknoloji:** Basit bir JSON/CSV dosyası
- **Çıktı:** `data/eval/test_questions.json`
- **Not:** 20 soru hazırlandı: `data/raw/`'daki 10 kaynak dokümanın her birinden 1-2 tane olmak üzere 14 cevaplanabilir soru (her biri `expected_source` ile etiketli) + 6 kasıtlı olarak bilgi tabanıyla alakasız soru (`expected_behavior: "unanswerable"`, örn. "What is the capital of France?", "How much does a Tesla Model 3 cost?"). Bazı sorular bilinçli olarak önceki fazlarda bulunan zayıf noktaları (Faz 2.4'ün get-started/what-is-foundry-local karışması, Faz 2.1'in CLI sorusu) tekrar test edecek şekilde seçildi.

### Faz 5.2 — RAGAS ile Otomatik Metrikler

- **Amaç:** Faithfulness (cevap bağlama sadık mı), answer relevancy, context precision gibi metrikleri otomatik hesaplamak.
- **Neden önemli:** Elle her cevabı okuyup değerlendirmek ölçeklenmez; otomatik metrikler ilerlemeni objektif olarak takip etmeni sağlar.
- **Yapılacaklar:**
  - RAGAS kütüphanesini kur, "judge" model olarak Foundry Local'daki modeli kullan
  - Test soru setini çalıştırıp metrikleri hesapla
- **Teknoloji:** RAGAS
- **Çıktı:** Bir metrik raporu (örn. `eval_report.md`)
- **Not:** RAGAS'tan vazgeçmek zorunda kalındı -- `ragas==0.4.3` kurulunca (`pip install ragas`), paket `langchain-community`'nin artık kaldırılmış bir alt modülüne (`chat_models.vertexai`) sabit bir import yapıyor; bunu çözmeye çalışmak `langchain-community`'yi eski bir sürüme (`0.3.27`) düşürdü, bu da Faz 4.1/4.3'ün üzerine kurulduğu modern LangChain 1.x yığınını (`langchain-core`, `langchain-openai`, `langgraph`) bozdu. Çalışan agentic RAG özelliklerini geriletmek kabul edilebilir olmadığı için RAGAS kaldırıldı, ortam eski haline döndürüldü (`langchain==1.3.14` vb. yeniden kuruldu, `LangchainFoundryProvider` ile doğrulandı). Bunun yerine `scripts/run_evaluation.py`, RAGAS'ın ölçtüğü aynı kavramları (faithfulness, answer relevancy, retrieval doğruluğu) kendi basit YES/NO "LLM-judge" promptlarıyla ölçüyor -- ayrıca küçük modelin (phi-3.5-mini) yapılı/JSON çıktıda daha önce (Faz 1.5, 4.2) tutarsız olduğu bilindiği için bu zaten RAGAS'ın beklediği karmaşık yapılı çıktılardan daha güvenilir bir seçim. 20 sorunun tamamı çalıştırıldı, sonuç `data/eval/eval_report.md`'ye yazıldı: **retrieval hit rate %93, faithfulness %93, answer relevancy %93, correct refusal rate %100** (6/6 cevaplanamaz soru doğru şekilde reddedildi). Tek gerçek başarısızlık: "How do I load a model using the Foundry Local CLI?" sorusu beklenmedik şekilde hiç kaynak bulamadı (model "bulamadım" dedi) -- oysa aynı konudaki komşu soru (id 6, "What CLI commands does Foundry Local provide?") sorunsuz cevaplandı; muhtemelen retrieval bu spesifik ifadeyi (chunk'ların "nasıl yüklerim" fiiliyle tam örtüşmemesi) yeterince alakalı bulamadı.

### Faz 5.3 — Regresyon Testi Altyapısı

- **Amaç:** Kod değişikliklerinin sistemi bozup bozmadığını otomatik kontrol eden testler yazmak.
- **Neden önemli:** İleri fazlarda (hybrid search, reranking, agentic akışlar) yeni değişiklikler eskiyi bozabilir; testler bunu erkenden yakalar.
- **Yapılacaklar:**
  - `pytest` ile temel testler: retrieval boş dönmüyor mu, cevap belirli anahtar kelimeleri içeriyor mu vb.
  - Eval setini periyodik çalıştıran bir script
- **Teknoloji:** pytest
- **Çıktı:** `tests/` klasöründe çalışan test paketi
- **Not:** Foundry Local, GitHub Actions gibi CI runner'larında çalışamayacağı için (Faz 6.4'te bu bir sorun olurdu) testlerin çoğu `tests/conftest.py`'daki `FakeLLM`/`FakeRetriever` (kendi `LLMProvider`/`RetrievalStrategy` arayüzlerimizi uygulayan test double'ları) ile **sunucu gerektirmeden** çalışacak şekilde tasarlandı: `test_prompt_builder.py`, `test_rag_pipeline.py`, `test_query_transforms.py`, `test_chunkers.py`, `test_hybrid_retriever.py`, `test_corrective_rag_pipeline.py` (21 test, hepsi saf mantık -- kaynak gösterme, "bilmiyorum" davranışı, rewrite/expansion çağrı sırası, RRF birleştirme, corrective RAG'ın retry/fallback akışı). Gerçek sunucuya ihtiyaç duyan 3 test (`test_integration_live_server.py`) `@pytest.mark.integration` ile işaretlendi ve `require_live_server` fixture'ı (basit bir socket bağlantı kontrolü) sunucu çalışmıyorsa otomatik `pytest.skip()` yapıyor -- doğrulandı: sunucu kapalıyken 3 test de hatasız SKIPPED oluyor, açıkken 24 testin tamamı geçiyor. Faz 5.2'deki `scripts/run_evaluation.py` zaten "eval setini periyodik çalıştıran script" ihtiyacını karşılıyor, ayrıca bir şey yazılmadı.

---

## FAZ 6 — Ürünleştirme

### Faz 6.1 — FastAPI Backend

- **Amaç:** RAG pipeline'ını bir HTTP API'sine dönüştürmek.
- **Neden önemli:** CLI'dan gerçek bir uygulamaya geçişin ilk adımı; herhangi bir frontend bu API'yi çağırabilir hale gelir.
- **Yapılacaklar:**
  - `/ask` endpoint'i: soru al, cevap + kaynakları döndür
  - Basit hata yönetimi
- **Teknoloji:** FastAPI
- **Çıktı:** `uvicorn` ile ayağa kalkan, Postman/curl ile test edilebilir bir API
- **Not:** `api.py`, `main.py`'daki `build_pipeline()`'ı yeniden kullanıyor (kod tekrarı yok) -- pipeline sunucu her istekte değil, `lifespan` context manager ile sadece bir kez ayağa kalkarken kuruluyor. `POST /ask`, `{question, history}` alıp `{answer, sources}` döndürüyor; `history` Faz 3.1'in çoklu-tur mantığını HTTP'nin durumsuz (stateless) doğasına uyacak şekilde her istekte istemciden geri gönderiliyor. Hata yönetimi: boş `question` → 400, pipeline'da beklenmeyen bir hata (örn. Foundry Local kapalıysa) → 503. Gerçek sunucuyla curl testleri: alakalı soru → cevap + doğru `sources`; boş soru → `400 {"detail": "question bos olamaz"}`; alakasız soru → `sources: []` ile "bulamadım"; geçmişli takip sorusu ("its architecture") → CLI'daki ile birebir aynı şekilde doğru çözümlendi.

### Faz 6.2 — Web Arayüzü

- **Amaç:** Tarayıcıdan kullanılabilir basit bir sohbet arayüzü.
- **Neden önemli:** Demo günü için CLI yerine görsel bir arayüz göstermek çok daha etkileyici.
- **Yapılacaklar:**
  - Streamlit ile hızlı bir arayüz **veya** basit bir HTML/JS + fetch ile FastAPI'ye bağlanan minimal bir sayfa
- **Teknoloji:** Streamlit (hızlı) veya HTML/JS (daha gösterişli)
- **Çıktı:** Tarayıcıda çalışan, soru sorup cevap alınabilen arayüz
- **Not:** HTML/JS seçildi -- ayrı bir süreç/port açan Streamlit yerine, Faz 6.1'de kurulan API'nin kendisinden servis edilen tek bir statik sayfa (`static/index.html`, build adımı yok, gömülü CSS/JS). `api.py`'a `/ask` rotasından SONRA `StaticFiles(directory="static", html=True)` mount edildi -- API rotaları önce eşleşiyor, geri kalan her yol statik dosyaya düşüyor. Sohbet geçmişi tarayıcıda (JS `history` dizisi) tutulup her istekte `/ask`'a geri gönderiliyor (Faz 6.1'in stateless tasarımıyla birebir uyumlu). Gerçek tarayıcıda (Chrome DevTools ile) test edildi: soru-cevap akışı, "Yazıyor..." göstergesi, kaynak gösterimi, takip sorusunda "its" zamirinin doğru çözümlenmesi ve alakasız soruda doğru "bulamadım" mesajı -- hepsi CLI/API ile birebir aynı davranışı gösterdi.

### Faz 6.3 — Docker Paketleme

- **Amaç:** Projeyi tek komutla, herhangi bir bilgisayarda ayağa kaldırılabilir hale getirmek.
- **Neden önemli:** "Bende çalışıyor" sorununu tamamen ortadan kaldırır; profesyonel projelerin standart teslim şekli.
- **Yapılacaklar:**
  - `Dockerfile` yaz
  - `docker build` + `docker run` ile test et
- **Teknoloji:** Docker
- **Çıktı:** Tek komutla çalışan bir container
- **Not:** ⚠️ `Dockerfile`, `.dockerignore` ve `docker-compose.yml` yazıldı ama **bu ortamda `docker build`/`docker run` ile doğrulanamadı** -- `docker --version` hem Bash hem PowerShell'de "command not found" verdi, Docker kurulu değil. Bunu gizlemek yerine olduğu gibi not ediyorum: bu, kendi makinende (Docker Desktop kuruluysa) `docker compose up --build` ile test edilmesi gereken bir adım. Tasarım kararları: (1) Foundry Local Windows/Mac'e özgü yerel bir runtime olduğu için container'ın **içine paketlenmedi** -- container, `FOUNDRY_BASE_URL=http://host.docker.internal:<port>/v1` ile host'taki Foundry Local'e ağ üzerinden bağlanıyor (`docker-compose.yml`'de `extra_hosts: host.docker.internal:host-gateway` ile Linux uyumluluğu da eklendi). (2) `chroma_db/` build zamanında image'a gömülmedi (Foundry Local'e ihtiyaç duyduğu için `docker build` sırasında değil, host'ta `scripts/build_vector_db.py` ile önceden oluşturulup çalışma zamanında salt-okunur mount ediliyor). Kod tarafında bunu mümkün kılan şey: `foundry-local-sdk` paketinin kodda hiç import edilmediğinin fark edilmesi -- uygulama zaten sadece OpenAI-uyumlu REST çağrıları (`openai`/`langchain-openai`) kullanıyor, bu da Linux container'dan host'a HTTP ile bağlanmayı sorunsuz hale getiriyor.

### Faz 6.4 — GitHub Actions CI

- **Amaç:** Her kod değişikliğinde testlerin otomatik çalışması.
- **Neden önemli:** Gerçek yazılım ekiplerinin standart pratiği; CV'de "CI/CD deneyimi var" demeni sağlar.
- **Yapılacaklar:**
  - `.github/workflows/test.yml` ile pytest'i her push'ta çalıştır
- **Teknoloji:** GitHub Actions
- **Çıktı:** Yeşil tik alan bir CI pipeline'ı
- **Not:** `.github/workflows/test.yml` yazıldı: `main`'e her push/PR'da Ubuntu runner'da Python 3.12 kurup `pytest -v` çalıştırıyor. Faz 5.3'te testlerin bilinçli olarak sunucu gerektirmeyecek şekilde tasarlanmış olması burada karşılığını buluyor -- `@pytest.mark.integration` testleri `require_live_server` fixture'ı sayesinde runner'da Foundry Local bulunamadığı için otomatik atlanacak, geri kalan 21 test sorunsuz çalışmalı. `origin/main`'e push edildi (kullanıcı onayıyla), workflow tetiklendi ve GitHub API üzerinden takip edildi: **`status: completed, conclusion: success`** -- gerçek bir yeşil tik alındı ([run #1](https://github.com/osmanfurkanerkan/foundry-local-rag-assistant/actions)).

---

## FAZ 7 — Dokümantasyon ve Sunum

### Faz 7.1 — README ve Mimari Diyagramı

- **Amaç:** Projeyi baştan sona anlatan, kurulum talimatları içeren bir README yazmak.
- **Neden önemli:** Bir projenin "bitmiş" sayılması için okunabilir dokümantasyonu şart; işe alım süreçlerinde ilk bakılan şeylerden biri.
- **Yapılacaklar:**
  - Proje amacı, mimari diyagram, kurulum adımları, kullanım örnekleri
- **Teknoloji:** Markdown
- **Çıktı:** Yayına hazır `README.md`
- **Not:** README tamamen yeniden yazıldı -- eski hali sadece Faz 1.6 (MVP) durumunu yansıtıyordu, Faz 2-6'nın (hybrid search, reranking, semantic chunking, multi-turn, streaming, LangChain/LangGraph, corrective RAG, değerlendirme, API, web arayüzü, Docker, CI) tamamı eksikti. Yeni README: öne çıkan özellikler listesi, güncellenmiş mimari diyagram (CLI + web arayüzü + API + corrective RAG akışını gösteriyor), üç farklı kullanım şekli (CLI/API/web), test ve değerlendirme komutları, Docker (test edilemedi notuyla), ve kısa bir "Proje Hikayesi" bölümü (en çarpıcı 3 bulguyu özetleyip detay için PROJECT_PLAN.md'ye yönlendiriyor) içeriyor. CI badge'i de eklendi (Faz 6.4'te doğrulanan gerçek workflow'a işaret ediyor).

### Faz 7.2 — Kod Temizliği

- **Amaç:** Debug print'lerini kaldırmak, gerekli yerlere kısa yorumlar eklemek, kod stilini tutarlı hale getirmek.
- **Neden önemli:** Temiz kod, hem staj değerlendirmesinde hem gelecekte kodu tekrar okurken fark yaratır.
- **Yapılacaklar:**
  - Kod gözden geçirme, gereksiz kodu silme
- **Teknoloji:** —
- **Çıktı:** Temiz, okunabilir kod tabanı
- **Not:** `ruff` ad-hoc kurulup `src/`, `main.py`, `api.py`, `scripts/`, `tests/` üzerinde tam bir lint taraması yapıldı. Pyflakes (F-kategorisi: kullanılmayan import/değişken/ölü kod) **sıfır hata** verdi -- kodun aşamalı, dikkatli geliştirme tarzının bir sonucu. Debug `print()`/`TODO`/`pdb` kalıntısı da bulunmadı. `E501` (satır uzunluğu) ve `E402` (dosya başında olmayan import) uyarıları bilinçli olarak görmezden gelindi: `E402`, script'lerin `sys.path.insert()` sonrası `rag_engine` import etme deseninden kaynaklanıyor ve kasıtlı/gerekli; `E501`'in varsayılan 88 karakter sınırı bu projenin zaten benimsediği bir konvansiyon değil (`src/`'de tek başına 47 satır bunu aşıyor) -- ruff'ın keyfi varsayılanını kovalamak yerine `api.py`'deki gerçekten okunması zor tek satırı (uzun bir curl örneği) düzeltmekle yetinildi.
- **Çıktı:** Temiz, okunabilir kod tabanı

### Faz 7.3 — Demo Günü Provası

- **Amaç:** Sunumu, canlı demoyu ve anlatacağın hikayeyi hazırlamak.
- **Neden önemli:** İyi bir proje bile kötü anlatılırsa etkisini kaybeder.
- **Yapılacaklar:**
  - Problem tanımı → mimari özet → canlı demo (biri kaynak gösteren, biri "bilmiyorum" diyen soru) → öğrenilen dersler
- **Teknoloji:** —
- **Çıktı:** Prova edilmiş bir sunum akışı

---

## FAZ 8 — (Ayrı Mini-Proje) Portfolyo Sitesine Entegrasyon

> Bu faz, staj teslimatından **bağımsız, ikinci bir proje** olarak ele alınacak. Foundry Local kişisel bilgisayarında çalışır; portfolyo siten internete açık olduğunda ziyaretçilerin bilgisayarında bu runtime olmayacağı için farklı bir dağıtım stratejisi gerekir.

### Faz 8.1 — RAG Motorunu Yeniden Kullanılabilir Kütüphane Haline Getirme

- **Amaç:** Staj projesindeki retrieval/generate mantığını, farklı bir bilgi tabanıyla tekrar kullanılabilecek şekilde soyutlamak.
- **Yapılacaklar:** `rag_engine` adında ayrı bir Python paketi çıkar (chunking, retrieval, prompt mantığı burada yaşasın)

### Faz 8.2 — Public Deployment için Model Stratejisi

- **Amaç:** Ziyaretçilerin cevap alabilmesi için modelin nerede çalışacağına karar vermek.
- **Seçenekler:**
  - Kendi sunucunda/VPS'inde Foundry Local'ı arka planda çalıştırıp API olarak sunmak (yine "local", ama senin sunucunda)
  - Production'da hafif, ücretsiz/ucuz hosted bir küçük modele geçmek

### Faz 8.3 — CV/Proje İçeriklerini Bilgi Tabanı Yapma

- **Amaç:** "Benim hakkımda sor" senaryosu için CV, proje açıklamaları, blog yazıları gibi içerikleri chunk'layıp embed etmek.

### Faz 8.4 — Portfolyo Sitesine Chat Widget Ekleme

- **Amaç:** Siteye gömülebilecek küçük bir sohbet kutusu (frontend widget) + backend API bağlantısı.

---

## Backlog — İleri Seviye Ekstra Fikirler (İstersen İlerledikçe Ekleriz)

- **GraphRAG:** Doküman parçaları arası ilişki grafiği ile ilişkisel sorularda daha güçlü retrieval
- **Multi-modal RAG:** Dokümanlardaki tablo/diyagram/kod bloklarını da anlama
- **Feedback loop:** "Bu cevap kötüydü" geri bildirimini loglayıp sistemi iyileştirme
- **Guardrails:** Alakasız/zararlı sorulara karşı filtreleme katmanı
- **Observability paneli:** Sorgu süresi, token sayısı, seçilen chunk'ları gösteren bir "kaputun altı" ekranı
- **Sesli arayüz:** Speech-to-text + TTS ile tamamen local sesli asistan
- **Fine-tuning karşılaştırması:** RAG yaklaşımını küçük bir LoRA fine-tune denemesiyle kıyaslama

---

## Şu Anki Durum

- [x] Faz 0.1 — Proje İskeleti ve Git
- [x] Faz 0.2 — Python Ortamı
- [x] Faz 0.3 — Foundry Local Kurulumu
- [x] Faz 0.4 — Embedding Kavramını Elle Keşfetme
- [x] Faz 1.1 — Kaynak Dokümanları Toplama
- [x] Faz 1.2 — Doküman Temizleme ve Chunking
- [x] Faz 1.3 — Embedding Üretimi ve Vektör DB'ye Yazma
- [x] Faz 1.4 — Retrieval Fonksiyonu
- [x] Faz 1.5 — Prompt Şablonu ve Generate
- [x] Faz 1.6 — CLI Arayüzü (MVP)
- [x] Faz 2.1 — Hybrid Search
- [x] Faz 2.2 — Reranking
- [x] Faz 2.3 — Akıllı Chunking
- [x] Faz 2.4 — Mini Benchmark
- [x] Faz 3.1 — Multi-turn Hafıza
- [x] Faz 3.2 — Kaynak Gösterme
- [x] Faz 3.3 — Streaming Yanıt
- [x] Faz 4.1 — LangChain/LangGraph Geçişi
- [x] Faz 4.2 — Query Rewriting
- [x] Faz 4.3 — Corrective RAG
- [ ] Faz 4.4 — Multi-Corpus Router (opsiyonel, ertelendi)
- [x] Faz 5.1 — Test Soru Seti
- [x] Faz 5.2 — RAGAS Metrikleri (custom LLM-judge'a pivot edildi)
- [x] Faz 5.3 — Regresyon Testleri
- [x] Faz 6.1 — FastAPI Backend
- [x] Faz 6.2 — Web Arayüzü
- [x] Faz 6.3 — Docker (yazıldı, build/run bu ortamda test edilemedi -- Docker kurulu değil)
- [x] Faz 6.4 — GitHub Actions CI (push edildi, gerçek yeşil tik doğrulandı)
- [x] Faz 7.1 — README ve Mimari Diyagram
- [x] Faz 7.2 — Kod Temizliği
- [ ] Faz 7.3 — Demo Provası
- [ ] Faz 8.x — Portfolyo Entegrasyonu (ayrı proje, ileride)
