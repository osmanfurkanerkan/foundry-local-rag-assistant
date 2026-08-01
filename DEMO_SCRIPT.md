# Demo Günü Sunum Akışı (Faz 7.3)

Toplam süre hedefi: ~6-8 dakika. Aşağıdaki adımlar gerçek sunucuda prova edildi (bkz. PROJECT_PLAN.md, Faz 7.3).

## Hazırlık (demo başlamadan önce, kapalı kapılar ardında)

```powershell
foundry server start
foundry model load phi-3.5-mini
foundry model load qwen3-embedding-0.6b
foundry server status   # portu not al, gerekirse FOUNDRY_BASE_URL ile override et
```

Web arayüzü demosu yapılacaksa `uvicorn api:app --reload` komutunu da bu sırada başlatıp `http://127.0.0.1:8000`'i tarayıcıda önceden aç.

## 1. Problem Tanımı (~1 dk)

- LLM'ler kendi eğitim verisinin dışındaki (özel, güncel, kurum-içi) bilgiyi bilmez, sorulduğunda halüsinasyon üretme riski taşır.
- RAG (Retrieval-Augmented Generation): soruyu cevaplamadan önce ilgili dokümanları bulup (retrieve) bunları prompt'a ekleyip (augment) modelin bu bağlamla cevap üretmesini (generate) sağlıyor.
- Senaryo: "RAG öğrenirken, öğrendiğini öğreten bir RAG asistanı" -- bilgi tabanı Foundry Local/RAG/embedding'in resmi Microsoft Learn dokümantasyonu.
- Anahtar kısıt: **tamamen offline**, Foundry Local ile kendi bilgisayarında çalışıyor.

## 2. Mimari Özet (~1-1.5 dk)

README'deki diyagramı göster (veya tahtaya çiz):

```
Kullanıcı → CLI / Web UI → FastAPI (api.py) → RagPipeline
                                                  │
                    ┌─────────────────────────────┼──────────────────┐
                    ▼                             ▼                  ▼
         Hybrid+Rerank Retrieval          Foundry Local LLM     Corrective RAG
       (embedding + BM25, cross-encoder)   (LangChain ChatOpenAI)  (LangGraph)
```

Bir cümlede: "Retrieval kalitesini hybrid search + reranking ile yükselttik, orkestrasyonu LangChain/LangGraph'e taşıdık, ve her adımı gerçek sunucuyla test edip sonuçları PROJECT_PLAN.md'ye kaydettik."

## 3. Canlı Demo (~2-3 dk)

CLI ile (`main.py`) ya da web arayüzüyle (`http://127.0.0.1:8000`) sırayla:

**a) Kaynak gösteren, doğru cevap:**
> "What is Retrieval-Augmented Generation (RAG) and how does it work?"

Beklenen: RAG'ın 3 adımını (retrieve/augment/generate) doğru açıklayan bir cevap + `Kaynak: rag-solution-design-and-evaluation-guide, retrieval-augmented-generation`.

**b) Takip sorusu (multi-turn, opsiyonel ama etkileyici):**
> "How does its architecture work?"

Beklenen: "its" zamiri geçmişten doğru çözümlenip Foundry Local mimarisiyle ilgili doğru kaynaklara gidiyor.

**c) Alakasız soru -- dürüstlük testi:**
> "What is the current stock price of Microsoft?"

Beklenen: **tam olarak** "I could not find this in the available documents." -- kaynak satırı yok, halüsinasyon yok.

## 4. Öğrenilen Dersler (~1.5-2 dk)

En güçlü hikaye: "her şey ilk seferde çalıştı" değil, "gerçek sorunlar çıktı, kök nedenini bulduk, karar verdik" hikayesi.

- **Küçük/yerel modelin dil sınırı**: `phi-3.5-mini`, Türkçe girdide dört ayrı yerde (soru ayrıştırma, reranking, query expansion, corrective RAG retry) tutarsızlaştı -- en çarpıcısı, "Foundry"yi bina/döküm ustalığı anlamında yorumlaması. Karar: asistanın çalışma dilini İngilizce'ye sabitledik.
- **Veriyle karar verme**: chunk boyutu/top-k benchmark'ında 4 farklı ayarın hepsi aynı sonucu verdi -- sezgiyle "iyileştirdik" sanmak yerine ölçüp gerçek darboğazın başka yerde (döküman örtüşmesi) olduğunu bulduk.
- **Canlı prova gerçek bir bug yakaladı** (bu fazda!): model bazen doğru cevabın sonuna "bulamadım" ifadesini dejenere şekilde ekliyordu, basit bir substring kontrolü bu yüzden geçerli kaynakları gizliyordu. `is_refusal()` fonksiyonuyla düzeltildi + regresyon testi eklendi -- "prova etmeden demo'ya çıkma" dersinin somut kanıtı.
- **RAGAS bağımlılık çakışması**: modern LangChain 1.x yığınını bozduğu için kaldırıldı, yerine kendi LLM-judge değerlendirmemizi yazdık (%93 retrieval/faithfulness/relevancy, %100 doğru refusal).

## Notlar / Riskler

- Foundry Local'in portu her başlatmada değişebilir -- demo öncesi mutlaka `foundry server status` ile kontrol et.
- İlk soru embedding modelinin "soğuk başlama" gecikmesini içerir (birkaç saniye); ikinci sorudan itibaren daha hızlı.
- Web arayüzü demosu görsel olarak daha etkileyici; CLI ise "kaputun altını" göstermek için daha uygun (streaming'i görmek gibi).
