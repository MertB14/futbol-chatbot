# 01 – Gereksinimler

**Proje:** Futbol Soru-Cevap Asistanı (BM 445 – Proje 3: LLM Tabanlı Soru-Cevap Asistanı)
**Teknolojiler:** Python, Streamlit, GPT-5.6 Luna (OpenCode Go üzerinden, OpenAI uyumlu API), JSON

## 1. Problem Tanımı

Futbolla ilgilenen kullanıcılar kurallar, taktikler, kulüpler, oyuncular ve turnuvalar hakkındaki sorularına hızlı ve anlaşılır cevap almak istiyor. Bilgiler farklı kaynaklara dağılmış durumda, arama motorları da çoğu zaman doğrudan cevap yerine uzun sayfalar gösteriyor. Bu proje, hazır bir LLM'i sistem promptlarıyla yönlendirerek **yalnızca futbol konusunda** cevap veren basit bir sohbet uygulaması geliştirir.

## 1.1 Amaç ve Hedefler

**Genel amaç:** Hazır bir LLM'i API üzerinden kullanarak futbol hakkındaki soruları doğru, tarafsız ve anlaşılır biçimde yanıtlayan, konu dışına çıkmayan bir sohbet asistanı geliştirmek. Bu süreçte prompt tasarımı, API kullanımı ve çıktıların değerlendirilmesi pratik olarak öğrenilecek.

**Ölçülebilir hedefler** (sonuçlar [04-test-plani.md](04-test-plani.md) ile ölçülür):

| ID | Hedef | Ölçüt |
|---|---|---|
| H1 | Doğru cevap | Bilgi sorularında ortalama doğruluk puanı ≥ 4.0 / 5 |
| H2 | Tutarlı cevap | Ortalama tutarlılık puanı ≥ 4.0 / 5 (aynı soru 3 kez + farklı ifadeler) |
| H3 | Az halüsinasyon | Bilgi sorularında halüsinasyon içeren cevap oranı ≤ %10; tuzak soruların en az 4/5'inde yanlış varsayımın düzeltilmesi |
| H4 | Doğru davranış | Konu dışı, güncel bilgi, mod dışı, etik ve injection testlerinin %100'ünün geçmesi |
| H5 | Prompt iyileştirmenin etkisi | Son prompt sürümünün (v2) ortalama puanının, minimal prompta (v0) göre daha yüksek olması |
| H6 | Hızlı cevap | Ortalama ilk cevap süresi < 10 sn |
| H7 | Kolay kullanım | Kullanıcının açıklama okumadan ilk sorusunu sorabilmesi (örnek soru butonları, karşılama mesajı) |
| H8 | Veriye dayalı model seçimi | 3 model aynı test setiyle karşılaştırılır; seçilen ana model, genel puanda ilk sırada olur ya da tercih nedeni (hız, maliyet) açıklanır |

## 2. Kapsam

Kullanıcı kenar çubuğundan üç **konu modundan** birini seçer. Her modun ayrı bir sistem promptu vardır.

| Mod | Odak | Örnek Konular |
|---|---|---|
| **Kurallar & Taktik** | Oyunun kuralları ve taktik bilgi | Ofsayt, VAR, penaltı, kartlar, dizilişler (4-3-3, 3-5-2), pres, gegenpressing |
| **Türk Futbolu** | Türkiye'deki futbol | Süper Lig, Türk kulüpleri, milli takım, Türk futbol tarihi, derbiler |
| **Dünya Futbolu** | Uluslararası futbol | Avrupa ligleri, Şampiyonlar Ligi, Dünya Kupası, efsane oyuncular, kulüp tarihleri |

### Kapsam Dışı

- Canlı skor, güncel puan durumu, son transferler (LLM'in bilgisi belirli bir tarihte kesilir; harici veri kaynağı kullanılmayacak)
- Bahis tahmini ve bahis tavsiyesi
- Futbol dışındaki konular
- Model eğitimi ve fine-tuning

## 3. Fonksiyonel Gereksinimler

| ID | Gereksinim | Öncelik |
|---|---|---|
| FR-01 | Kullanıcı metin kutusuna soru yazıp gönderebilmeli. | Zorunlu |
| FR-02 | Sistem soruyu, seçili modun sistem promptuyla birlikte LLM API'sine göndermeli ve cevabı ekranda göstermeli. | Zorunlu |
| FR-03 | Kullanıcı kenar çubuğundan 3 moddan birini seçebilmeli: Kurallar & Taktik, Türk Futbolu, Dünya Futbolu. | Zorunlu |
| FR-04 | **Sohbet geçmişi:** Oturum boyunca önceki mesajlar ekranda görünmeli ve çok turlu konuşma için modele bağlam olarak gönderilmeli (`st.session_state`). | Zorunlu |
| FR-05 | Kullanıcı sohbet geçmişini bir butonla temizleyebilmeli. | Zorunlu |
| FR-06 | Mod değiştiğinde sohbet geçmişi sıfırlanmalı (farklı sistem promptları birbirine karışmasın). | Zorunlu |
| FR-07 | **Konu dışı soruları reddetme:** Futbol dışındaki sorulara model kibarca, yalnızca futbol konusunda yardımcı olabildiğini söyleyerek cevap vermeli. | Zorunlu |
| FR-08 | Seçili modun konusu dışında kalan ama futbolla ilgili sorularda model kısa bir cevap verip kullanıcıyı uygun moda yönlendirmeli. | İsteğe bağlı |
| FR-09 | Model, güncel bilgi gerektiren sorularda (ör. "Bu sezon lider kim?") bilgisinin güncel olmayabileceğini belirtmeli. | Zorunlu |
| FR-10 | **Otomatik test scripti:** Test sorularını JSON dosyasından okuyup her birini ilgili modla modele göndermeli ve cevapları bir JSON/CSV dosyasına kaydetmeli. | Zorunlu |
| FR-11 | API hatalarında (geçersiz anahtar, zaman aşımı, kota) kullanıcıya anlaşılır bir hata mesajı gösterilmeli; uygulama çökmemeli. | Zorunlu |
| FR-12 | **Ayarlanabilir temperature:** Kullanıcı kenar çubuğundaki bir slider ile temperature değerini 0.0–1.0 arasında değiştirebilmeli (varsayılan 0.3, adım 0.1). Seçilen değer sonraki tüm isteklerde kullanılmalı. | Zorunlu |
| FR-13 | Test scripti `--temperature` parametresi almalı ve kullandığı değeri sonuç dosyasına yazmalı. | Zorunlu |
| FR-14 | **Geri bildirim:** Her asistan cevabının altında 👍/👎 butonu olmalı. Geri bildirimler yalnızca oturum içinde tutulmalı (diske yazılmaz, ETK-02); kenar çubuğunda oturum özeti gösterilmeli (ör. "👍 5 · 👎 1"). | Zorunlu |
| FR-15 | **Süre ve token ölçümü:** Her cevap için yanıt süresi ile girdi/çıktı token sayıları ölçülmeli. Arayüzde cevabın altında küçük yazıyla gösterilmeli; test sonuçlarına yazılmalı. | Zorunlu |
| FR-16 | **Yedek model:** Ana model hata verirse (zaman aşımı, sunucu hatası, kota/hız sınırı, model bulunamadı) istek bir kez `LLM_FALLBACK_MODEL` ile tekrarlanmalı. Yedek model kullanıldığında arayüzde bilgi notu görünmeli. Test scriptinde yedek model varsayılan olarak **kapalı** olmalı (karşılaştırmalar karışmasın). | Zorunlu |
| FR-17 | **Model karşılaştırması:** Test scripti `--model` ve `--models a,b,c` parametreleriyle aynı test setini birden fazla modelde çalıştırabilmeli. | Zorunlu |

## 4. Fonksiyonel Olmayan Gereksinimler

| ID | Gereksinim |
|---|---|
| NFR-01 | **Dil:** Arayüz ve cevaplar Türkçe olmalı. |
| NFR-02 | **Performans:** Normal koşullarda cevap 10 saniyenin altında gelmeli. Mümkünse cevap akış (streaming) ile gösterilmeli. |
| NFR-03 | **Güvenlik:** API anahtarı koda yazılmamalı; `.env` dosyasından ya da `st.secrets` üzerinden okunmalı. `.env` sürüm kontrolüne eklenmemeli. |
| NFR-04 | **Değiştirilebilirlik:** LLM sağlayıcısı tek bir modülde (`llm_client.py`) soyutlanmalı; sağlayıcı değişince yalnızca bu modül değişmeli. |
| NFR-05 | **Yapılandırma:** Sistem promptları koddan ayrı dosyalarda (`prompts/`) tutulmalı. |
| NFR-06 | **Maliyet:** Gereksiz token kullanımını önlemek için sohbet geçmişi son N mesajla sınırlandırılmalı (ör. son 10 mesaj). |
| NFR-07 | **Kullanılabilirlik:** Arayüz tek sayfa olmalı ve ilk kez kullanan biri açıklama okumadan kullanabilmeli. |
| NFR-08 | **Güvenlik:** Prompt injection koruması, girdi doğrulama, hız sınırı ve çıktı/log güvenliği uygulanmalı. Ayrıntılar [07-guvenlik.md](07-guvenlik.md) dosyasında (SEC-01 – SEC-16). |
| NFR-09 | **Etik:** Kişisel veri, telif, yanlış bilgi ve sorumlu AI ilkelerine uyulmalı. Ayrıntılar [08-etik.md](08-etik.md) dosyasında (ETK-01 – ETK-11). |

## 5. Kısıtlar ve Varsayımlar

- **Modeller:** OpenCode Go üzerinden 3 model test edilir (bkz. [04-test-plani.md](04-test-plani.md), Bölüm 8). Adaylar Claude Haiku 5.5, GPT-5.6 Luna ve Gemini 4 Argon; ölçüm sonucunda ana model GPT-5.6 Luna, yedek model Gemini 4 Argon seçildi. Karşılaştırma sonucuna göre ana model değişebilir. Bir model yedek model olarak kullanılır.
- **Ana LLM:** GPT-5.6 Luna, **OpenCode Go** aboneliği üzerinden kullanılır.
  - Model kimliği: `gpt-5.6-luna` (yedek: `gemini-4-argon`)
  - Base URL: `https://opencode.ai/zen/go/v1`
  - API OpenAI uyumlu olduğu için `openai` Python SDK'sı kullanılır.
  - Base URL ve model adı `.env` dosyasından okunur. Değişirlerse kod değişmez.
  - Go uç noktası her istekte `x-opencode-session` başlığı ister (istemci her sohbet için ekler).
  - Başlangıçta seçilen DeepSeek V4.1 Flash bırakıldı: ücretsiz sürümün (`-free`) kullanım limiti doluyor, Go sürümü ise Avrupa/ABD dışında barındırıldığı için hesap bölge ayarı *Global* olmadan çalışmıyor.
- Abonelik ve kullanım kotaları sınırlı olabilir. Hız sınırı ve `max_tokens` bu yüzden zorunlu.
- Modelin bilgisi eğitim verisinin kesildiği tarihle sınırlıdır.
- Harici veritabanı ya da futbol veri API'si kullanılmayacak.

## 6. Teslim Edilecekler

1. Çalışan Streamlit chatbot
2. En az 20 test sorusu ve cevaplarının değerlendirilmesi (bkz. [04-test-plani.md](04-test-plani.md))
3. Otomatik test scripti ve çıktıları
4. README: kurulum, kullanım ve örnekler (bkz. [../README.md](../README.md))
5. Teknik rapor (bkz. [09-rapor-sablonu.md](09-rapor-sablonu.md))
6. Demo (bkz. [10-demo-plani.md](10-demo-plani.md))
