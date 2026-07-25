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

### Faz 2.2 — Reranking (Cross-Encoder)

- **Amaç:** İlk aramadan gelen top-N sonucu, daha güçlü ama daha yavaş bir modelle yeniden sıralamak.
- **Neden önemli:** Embedding araması hızlı ama kaba; cross-encoder daha yavaş ama çok daha isabetli. İkisini birleştirmek (geniş ara + dar süz) modern RAG sistemlerinin standart deseni.
- **Yapılacaklar:**
  - Yerel bir cross-encoder modeli (`sentence-transformers` reranker) entegre et
  - Top-10 sonucu al, rerank ile top-3'e indir
- **Teknoloji:** `sentence-transformers`
- **Çıktı:** Rerank öncesi/sonrası sonuçları karşılaştıran küçük bir test scripti

### Faz 2.3 — Akıllı (Semantic) Chunking

- **Amaç:** Sabit boyut yerine, anlam sınırlarına göre chunk'lama.
- **Neden önemli:** Sabit boyut bazen bir cümleyi ya da fikri ortadan böler, retrieval kalitesini düşürür.
- **Yapılacaklar:**
  - Başlık/paragraf sınırlarına göre bölme stratejisi dene
  - Eski (sabit boyut) ve yeni chunking sonuçlarını karşılaştır
- **Teknoloji:** `langchain-text-splitters` (semantic/markdown splitter)
- **Çıktı:** Güncellenmiş, daha kaliteli chunk seti

### Faz 2.4 — Mini Benchmark: Chunk Boyutu ve Top-K Deneyleri

- **Amaç:** Farklı chunk boyutu / top-k değerlerinin cevap kalitesine etkisini sistematik ölçmek.
- **Neden önemli:** "Sezgiyle" değil, veriyle karar vermeyi öğrenmek — gerçek mühendislik pratiği.
- **Yapılacaklar:**
  - 3-4 farklı konfigürasyon dene, aynı soru setiyle test et
  - Sonuçları basit bir tabloya/log dosyasına yaz
- **Teknoloji:** Python, basit loglama
- **Çıktı:** Hangi konfigürasyonun en iyi sonucu verdiğine dair kısa bir bulgu notu

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

### Faz 3.2 — Kaynak Gösterme ve "Bilmiyorum" Davranışı

- **Amaç:** Her cevapta hangi dokümandan geldiğini göstermek; bağlam yetersizse dürüstçe "bilmiyorum" demek.
- **Neden önemli:** RAG'ın en büyük avantajı budur — kaynağı belirsiz, halüsinasyonlu cevaplara karşı güven inşa eder.
- **Yapılacaklar:**
  - Her chunk'a kaynak/başlık metadata'sı ekle (Faz 1.3'te zaten kaydedilmişti, burada kullan)
  - Cevabın sonuna "Kaynak: ..." ekle
  - Prompt'a "bağlam yetersizse bilmediğini söyle" talimatını güçlendir, test et
- **Teknoloji:** Prompt engineering
- **Çıktı:** Kaynaklı cevaplar veren, bilmediğini itiraf edebilen asistan

### Faz 3.3 — Streaming Yanıt

- **Amaç:** Cevabın kelime kelime, canlı şekilde ekrana yazılması.
- **Neden önemli:** Kullanıcı deneyimini büyük ölçüde iyileştirir (ChatGPT tarzı his); teknik olarak stream API kullanmayı öğretir.
- **Yapılacaklar:**
  - Foundry Local'ın streaming chat API'sini kullan
  - CLI'da kelime kelime yazdırma
- **Teknoloji:** Foundry Local streaming API
- **Çıktı:** Akıcı, canlı yazan bir CLI deneyimi

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

### Faz 4.2 — Query Rewriting

- **Amaç:** Kullanıcının kötü ifade edilmiş/belirsiz sorusunu, arama öncesi modelin kendisinin düzeltmesi.
- **Neden önemli:** Gerçek kullanıcı soruları nadiren "mükemmel arama sorgusu" gibi yazılır; bu adım retrieval kalitesini ciddi artırır.
- **Yapılacaklar:**
  - Aramadan önce küçük bir LLM çağrısıyla soruyu yeniden yaz/genişlet
  - Öncesi/sonrası retrieval sonuçlarını karşılaştır
- **Teknoloji:** LangChain, Foundry Local
- **Çıktı:** Query rewriting açık/kapalı iki modun karşılaştırmalı testi

### Faz 4.3 — Corrective RAG (Self-Grading Retrieval)

- **Amaç:** Sistemin, bulduğu chunk'ların soruyu cevaplamaya yeterli olup olmadığını kendi değerlendirmesi; yetersizse farklı bir strateji denemesi.
- **Neden önemli:** Bu, "akıllı" RAG ile "sabit boru hattı" RAG arasındaki farkı yaratan ileri seviye bir teknik (agentic davranış).
- **Yapılacaklar:**
  - Retrieval sonrası bir "grading" adımı ekle: model chunk'ların alakalı olup olmadığını puanlasın
  - Yetersizse: query rewriting'i tekrar dene veya top-k'yı artır
- **Teknoloji:** LangGraph (döngüsel/koşullu akışlar için)
- **Çıktı:** Zayıf sonuçlarda kendini düzelten bir retrieval döngüsü

### Faz 4.4 — (Opsiyonel Stretch) Multi-Corpus Router

- **Amaç:** İkinci bir bilgi kaynağı (örn. kendi ders notların) ekleyip, sistemin hangi kaynağa bakacağına kendisinin karar vermesi.
- **Neden önemli:** Gerçek dünya sistemleri genelde tek kaynaklı değildir; bu, projenin kişisel dokunuşunu da katıyor (Senaryo B'yi buraya entegre ediyoruz).
- **Yapılacaklar:**
  - İkinci bir Chroma koleksiyonu oluştur (kişisel notlar)
  - Basit bir "router" promptu: soru hangi kaynağa daha yakın, oraya yönlendir
- **Teknoloji:** LangGraph
- **Çıktı:** İki farklı kaynak arasında akıllıca seçim yapabilen asistan

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

### Faz 5.2 — RAGAS ile Otomatik Metrikler

- **Amaç:** Faithfulness (cevap bağlama sadık mı), answer relevancy, context precision gibi metrikleri otomatik hesaplamak.
- **Neden önemli:** Elle her cevabı okuyup değerlendirmek ölçeklenmez; otomatik metrikler ilerlemeni objektif olarak takip etmeni sağlar.
- **Yapılacaklar:**
  - RAGAS kütüphanesini kur, "judge" model olarak Foundry Local'daki modeli kullan
  - Test soru setini çalıştırıp metrikleri hesapla
- **Teknoloji:** RAGAS
- **Çıktı:** Bir metrik raporu (örn. `eval_report.md`)

### Faz 5.3 — Regresyon Testi Altyapısı

- **Amaç:** Kod değişikliklerinin sistemi bozup bozmadığını otomatik kontrol eden testler yazmak.
- **Neden önemli:** İleri fazlarda (hybrid search, reranking, agentic akışlar) yeni değişiklikler eskiyi bozabilir; testler bunu erkenden yakalar.
- **Yapılacaklar:**
  - `pytest` ile temel testler: retrieval boş dönmüyor mu, cevap belirli anahtar kelimeleri içeriyor mu vb.
  - Eval setini periyodik çalıştıran bir script
- **Teknoloji:** pytest
- **Çıktı:** `tests/` klasöründe çalışan test paketi

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

### Faz 6.2 — Web Arayüzü

- **Amaç:** Tarayıcıdan kullanılabilir basit bir sohbet arayüzü.
- **Neden önemli:** Demo günü için CLI yerine görsel bir arayüz göstermek çok daha etkileyici.
- **Yapılacaklar:**
  - Streamlit ile hızlı bir arayüz **veya** basit bir HTML/JS + fetch ile FastAPI'ye bağlanan minimal bir sayfa
- **Teknoloji:** Streamlit (hızlı) veya HTML/JS (daha gösterişli)
- **Çıktı:** Tarayıcıda çalışan, soru sorup cevap alınabilen arayüz

### Faz 6.3 — Docker Paketleme

- **Amaç:** Projeyi tek komutla, herhangi bir bilgisayarda ayağa kaldırılabilir hale getirmek.
- **Neden önemli:** "Bende çalışıyor" sorununu tamamen ortadan kaldırır; profesyonel projelerin standart teslim şekli.
- **Yapılacaklar:**
  - `Dockerfile` yaz
  - `docker build` + `docker run` ile test et
- **Teknoloji:** Docker
- **Çıktı:** Tek komutla çalışan bir container

### Faz 6.4 — GitHub Actions CI

- **Amaç:** Her kod değişikliğinde testlerin otomatik çalışması.
- **Neden önemli:** Gerçek yazılım ekiplerinin standart pratiği; CV'de "CI/CD deneyimi var" demeni sağlar.
- **Yapılacaklar:**
  - `.github/workflows/test.yml` ile pytest'i her push'ta çalıştır
- **Teknoloji:** GitHub Actions
- **Çıktı:** Yeşil tik alan bir CI pipeline'ı

---

## FAZ 7 — Dokümantasyon ve Sunum

### Faz 7.1 — README ve Mimari Diyagramı

- **Amaç:** Projeyi baştan sona anlatan, kurulum talimatları içeren bir README yazmak.
- **Neden önemli:** Bir projenin "bitmiş" sayılması için okunabilir dokümantasyonu şart; işe alım süreçlerinde ilk bakılan şeylerden biri.
- **Yapılacaklar:**
  - Proje amacı, mimari diyagram, kurulum adımları, kullanım örnekleri
- **Teknoloji:** Markdown
- **Çıktı:** Yayına hazır `README.md`

### Faz 7.2 — Kod Temizliği

- **Amaç:** Debug print'lerini kaldırmak, gerekli yerlere kısa yorumlar eklemek, kod stilini tutarlı hale getirmek.
- **Neden önemli:** Temiz kod, hem staj değerlendirmesinde hem gelecekte kodu tekrar okurken fark yaratır.
- **Yapılacaklar:**
  - Kod gözden geçirme, gereksiz kodu silme
- **Teknoloji:** —
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
- [ ] Faz 1.4 — Retrieval Fonksiyonu
- [ ] Faz 1.5 — Prompt Şablonu ve Generate
- [ ] Faz 1.6 — CLI Arayüzü (MVP)
- [ ] Faz 2.1 — Hybrid Search
- [ ] Faz 2.2 — Reranking
- [ ] Faz 2.3 — Akıllı Chunking
- [ ] Faz 2.4 — Mini Benchmark
- [ ] Faz 3.1 — Multi-turn Hafıza
- [ ] Faz 3.2 — Kaynak Gösterme
- [ ] Faz 3.3 — Streaming Yanıt
- [ ] Faz 4.1 — LangChain/LangGraph Geçişi
- [ ] Faz 4.2 — Query Rewriting
- [ ] Faz 4.3 — Corrective RAG
- [ ] Faz 4.4 — Multi-Corpus Router (opsiyonel)
- [ ] Faz 5.1 — Test Soru Seti
- [ ] Faz 5.2 — RAGAS Metrikleri
- [ ] Faz 5.3 — Regresyon Testleri
- [ ] Faz 6.1 — FastAPI Backend
- [ ] Faz 6.2 — Web Arayüzü
- [ ] Faz 6.3 — Docker
- [ ] Faz 6.4 — GitHub Actions CI
- [ ] Faz 7.1 — README ve Mimari Diyagram
- [ ] Faz 7.2 — Kod Temizliği
- [ ] Faz 7.3 — Demo Provası
- [ ] Faz 8.x — Portfolyo Entegrasyonu (ayrı proje, ileride)
