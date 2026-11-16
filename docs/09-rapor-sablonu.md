# 09 – Teknik Rapor Şablonu

Teslim edilecek kısa teknik raporun iskeletidir. Her bölümün yanında karşıladığı değerlendirme kriteri (K1–K20) ve kaynak doküman yazılıdır. Köşeli parantez içindeki alanlar test sonuçlarıyla doldurulacak.

---

## Kriter – Bölüm Eşleme Tablosu

| K | Kriter | Rapor Bölümü | Kaynak Doküman |
|---|---|---|---|
| 1 | Problem tanımı | 1 | 01 §1 |
| 2 | Amaç ve hedef | 2 | 01 §1.1 |
| 3 | Kullanım senaryosu | 3 | 02, 03 |
| 4 | LLM seçimi | 4 | 06 §6 |
| 5 | Prompt tasarımı | 5.1 | 05 |
| 6 | LLM API kullanımı | 6.2 | 06 §3 |
| 7 | Girdi tasarımı | 6.3 | 06 §3, 07 |
| 8 | Çıktı kalitesi | 7.2 | 04 |
| 9 | Prompt iyileştirme | 5.2 | 05 §6 |
| 10 | Uygulama geliştirme | 6 | Kod |
| 11 | Test senaryoları | 7.1 | 04 |
| 12 | Doğruluk | 7.2 | 04 |
| 13 | Tutarlılık | 7.3 | 04 §4.5 |
| 14 | Hata/halüsinasyon analizi | 7.4 | 04 §7 |
| 15 | Kullanılabilirlik | 6.4 | 06 §4 |
| 16 | Teknik açıklama | 6 | 06 |
| 17 | Etik ve güvenlik | 8 | 07, 08 |
| 18 | Dokümantasyon | Ek A | README, docs/ |
| 19 | Sunum ve demo | – | 10 |
| 20 | Sonuç ve değerlendirme | 9 | – |

---

# Futbol Soru-Cevap Asistanı – Teknik Rapor

**Ders:** BM 445 – Üretken Yapay Zekâ ve Büyük Dil Modelleri
**Hazırlayan(lar):** [...]
**Tarih:** [...]

## 1. Problem Tanımı *(K1)*
[01 §1'den özet. 3–4 cümle.]

## 2. Amaç ve Hedefler *(K2)*
[Genel amaç + H1–H7 tablosu.]

## 3. Kullanım Senaryosu *(K3)*
[3 persona kısaca + 1–2 örnek senaryo.]

## 4. LLM Seçimi *(K4)*
### 4.1 Ön seçim
[Seçim kriterleri tablosu, sağlayıcı alternatifleri.]
### 4.2 Model karşılaştırması
[3 modelin karşılaştırma tablosu (04 §8.3): doğruluk, tutarlılık, halüsinasyon, süre, token. Kör puanlama yöntemi. Ana ve yedek model kararı ve gerekçesi. Aynı soruya 3 modelin verdiği cevaplardan 1–2 çarpıcı örnek.]

## 5. Prompt Tasarımı ve İyileştirme
### 5.1 Prompt tasarımı *(K5)*
[Tasarım ilkeleri, v1 temel prompt ve mod ekleri (kısaltılmış).]
### 5.2 Prompt iyileştirme *(K9)*
[v0 → v1 → v2 karşılaştırma tablosu. Her değişikliğin hangi testi düzelttiğine dair en az 2 somut örnek: önceki cevap / sonraki cevap.]

## 6. Uygulama *(K10, K16)*
### 6.1 Mimari
[Mimari diyagram + bileşenler.]
### 6.2 API kullanımı *(K6)*
[`llm_client.chat` örneği, parametreler: model, temperature, max_tokens, stream.]
### 6.3 Girdi tasarımı *(K7)*
[Mesaj formatı, `<kullanici_sorusu>` etiketleri, sohbet geçmişi sınırı, girdi doğrulama.]
### 6.4 Arayüz *(K15)*
[2–3 ekran görüntüsü: karşılama ekranı, örnek sohbet (süre/token bilgisi ve 👍/👎 ile), hata mesajı. Yedek model mekanizmasının kısa açıklaması.]
### 6.5 Kullanıcı geri bildirimi
[Demo ve denemeler sırasında toplanan 👍/👎 sayıları ve 👎 alan cevaplardan örnekler.]

## 7. Test ve Değerlendirme
### 7.1 Test senaryoları *(K11)*
[49 soru, 6 grup, 3 tekrar, 3 prompt sürümü, 3 temperature değeri, 3 model.]
### 7.1.1 Performans
[Model ve prompt sürümü bazında ortalama süre, ilk token süresi ve token sayıları. Prompt uzunluğunun token maliyetine etkisi (v0 ve v1 karşılaştırması).]
### 7.2 Doğruluk ve çıktı kalitesi *(K8, K12)*
[Mod bazında ortalama doğruluk ve kullanışlılık tablosu.]
### 7.3 Tutarlılık *(K13)*
[3 tekrar ve farklı ifade (FI) sonuçları; temperature karşılaştırma tablosu.]
### 7.4 Halüsinasyon analizi *(K14)*
[Halüsinasyon oranı (sürüm bazında), kategori dağılımı, en az 3 alıntılı örnek, olası nedenler.]

## 8. Etik ve Güvenlik *(K17)*
[Kişisel veri, telif, yanlış bilgi, sorumlu AI önlemleri; güvenlik önlemleri; injection ve etik test sonuçları.]

## 9. Sonuç ve Değerlendirme *(K20)*

### 9.1 Sonuçlar
[Hedef tablosu: H1–H7 → hedef / gerçekleşen / karşılandı mı?]

### 9.2 Sınırlılıklar
Önceden bilinen sınırlılıklar (sonuçlara göre güncellenecek):
- **Bilgi kesim tarihi:** Model güncel puan durumu, son transferler ve yeni sezon sonuçları hakkında bilgi veremez.
- **Harici veri yok:** Cevaplar yalnızca modelin eğitim verisine dayanır; kaynak gösterilemez.
- **Türk futbolu kapsamı:** Alt ligler ve az bilinen oyuncular gibi niş konularda halüsinasyon riski daha yüksek olabilir. [Sonuçlarla doğrulanacak]
- **Elle puanlama:** Değerlendirme tek kişi tarafından yapıldığında öznel olabilir.
- **Hız sınırı:** Oturum bazlı; sayfa yenilenince sıfırlanır.
- **Sınırlı model kümesi:** Karşılaştırma yalnızca OpenCode Go'daki 3 modelle yapıldı; sonuçlar başka modellere genellenemez.
- **Geri bildirim kalıcı değil:** 👍/👎 verileri gizlilik nedeniyle yalnızca oturum içinde tutulur; uzun vadeli analiz yapılamaz.
- **Sağlayıcı bağımlılığı:** Verinin üçüncü taraf sunucularda işlenmesi; servis kesintileri.

### 9.3 Geliştirilebilecek Yönler
- **RAG:** Futbol veri API'si veya Wikipedia ile güncel ve kaynaklı cevaplar
- **Canlı veri:** Puan durumu ve fikstür için harici API entegrasyonu
- **Daha geniş model karşılaştırması:** Farklı sağlayıcılardan modellerin eklenmesi
- **Otomatik değerlendirme:** LLM-as-judge ile puanlamanın kısmen otomatikleştirilmesi
- **Kalıcı geri bildirim:** Kullanıcı onayıyla, anonim 👍/👎 verilerinin saklanıp prompt iyileştirmede kullanılması
- **Kaynak gösterme:** Cevaplarda doğrulama için kaynak bağlantıları
- **Çok dillilik:** İngilizce destek

## Ek A – Dokümantasyon *(K18)*
[README bağlantısı, docs/ klasörünün listesi, depo bağlantısı.]

## Ek B – Test Sonuçlarının Tamamı
[results CSV dosyasına bağlantı veya tablo.]
