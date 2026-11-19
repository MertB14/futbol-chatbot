# 08 – Etik ve Sorumlu Yapay Zekâ

Bu doküman NFR-09 gereksiniminin ayrıntılarını içerir. Teknik güvenlik önlemleri için bkz. [07-guvenlik.md](07-guvenlik.md).

## 1. Kişisel Veri ve Gizlilik (KVKK)

| ID | Önlem |
|---|---|
| ETK-01 | **Üçüncü taraf bildirimi:** Kullanıcının mesajları cevap üretmek için OpenCode Go üzerinden seçili yapay zekâ modeline gönderilir. Arayüzde bu açıkça belirtilir: *"Mesajların yanıt üretmek için üçüncü taraf bir yapay zekâ servisine gönderilir. Kişisel bilgilerini (ad, telefon, adres vb.) paylaşma."* |
| ETK-02 | **Veri saklamama:** Uygulama kullanıcı mesajlarını diske, veritabanına ya da loglara kaydetmez. Sohbet ve 👍/👎 geri bildirimleri yalnızca tarayıcı oturumu süresince bellekte (`st.session_state`) tutulur ve sayfa kapanınca silinir (SEC-16, FR-14). |
| ETK-03 | **Sağlayıcı politikası:** Verilerin sağlayıcı tarafında nasıl işlendiği ve saklandığı OpenCode'un gizlilik politikasına bağlıdır. Bu politika rapor yazılırken incelenir ve sınırlılıklar bölümünde belirtilir. |
| ETK-11 | **Kişisel bilgi gizleme:** Kullanıcı mesajına telefon numarası, T.C. kimlik numarası, e-posta, IBAN, kart numarası ya da adres (mahalle/sokak + kapı/daire no) yazarsa, mesaj modele gönderilmeden önce bu kısımlar `[TELEFON]`, `[ADRES]` gibi etiketlerle değiştirilir ve kullanıcıya 🔒 uyarısı gösterilir (`security.mask_personal_data`). Sohbet geçmişinde de yalnızca gizlenmiş hâl tutulur. Yanlış alarmı azaltmak için numara kalıpları en az 10 rakam ister; kimlik ve kart numaraları sağlama algoritmasıyla (T.C. kimlik algoritması, Luhn) doğrulanır. **Sınırlılık:** Ad-soyad, oyuncu adlarından ayırt edilemediği için tespit edilmez; kalıp dışı yazılmış bilgiler (ör. "sıfır beş yüz otuz iki...") yakalanamaz. |
| ETK-04 | **Kişiler hakkında bilgi:** Model, oyuncuların, teknik direktörlerin ve hakemlerin yalnızca kamuya açık futbol kariyerleri hakkında konuşur. Özel hayat, sağlık, aile ve doğrulanmamış iddialar hakkında spekülasyon yapmaz (sistem promptu – Etik bölümü). |

## 2. Telif Hakkı

| ID | Önlem |
|---|---|
| ETK-05 | Model haber makalelerini, kitapları veya telifli metinleri birebir kopyalamaz; bilgiyi kendi cümleleriyle özetler (sistem promptu). |
| ETK-06 | Arayüzde kulüp logoları, lig logoları ve telifli görseller kullanılmaz; yalnızca emoji ve metin kullanılır. |
| ETK-07 | Kullanılan kütüphaneler (Streamlit, openai, python-dotenv) açık kaynak lisanslıdır ve README'de listelenir. Modelin kullanım koşulları rapora eklenir. |

## 3. Yanlış Bilgi

| ID | Önlem |
|---|---|
| ETK-08 | **Sorumluluk uyarısı:** Arayüzde sabit bir uyarı bulunur: *"Cevaplar yapay zekâ tarafından üretilir ve hatalı olabilir. Önemli bilgileri resmî kaynaklardan (TFF, UEFA, FIFA) doğrula."* |
| | Ayrıca: "emin değilsen uydurma" kuralı, güncel bilgi uyarısı (FR-09), düşük varsayılan temperature (0.3), halüsinasyon analizi ve tuzak sorular ([04-test-plani.md](04-test-plani.md), Bölüm 4.6 ve 7). |

## 4. Sorumlu Yapay Zekâ

| ID | İlke | Uygulama |
|---|---|---|
| ETK-09 | **Tarafsızlık** | Kulüpler ve derbiler hakkında tarafsız dil (sistem promptu). Türk Futbolu modunda büyük kulüplerle ilgili test sorularında taraflı ifade olup olmadığı kontrol edilir. |
| ETK-10 | **Zarar önleme** | Hakaret, nefret söylemi ve aşağılayıcı tezahürat üretilmez (DV-11). Bahis tahmini ve bahis tavsiyesi verilmez (DV-12). |
| – | **Şeffaflık** | Kullanıcı bir yapay zekâyla konuştuğunu bilir (uygulama adı, uyarı metni). Modelin sınırlılıkları README'de ve raporda açıkça yazılır. |
| – | **İnsan denetimi** | Test sonuçları elle puanlanır; halüsinasyonlar tek tek incelenip raporlanır. |

## 5. Arayüzdeki Metinler

**Kenar çubuğu alt bilgisi:**
> ℹ️ Cevaplar yapay zekâ tarafından üretilir ve hatalı olabilir. Önemli bilgileri resmî kaynaklardan doğrula. Mesajların üçüncü taraf bir yapay zekâ servisine gönderilir; kişisel bilgilerini paylaşma.

## 6. Kontrol Listesi

- [ ] Kenar çubuğunda sorumluluk ve gizlilik uyarısı görünüyor
- [ ] Kullanıcı mesajları hiçbir dosyaya yazılmıyor
- [ ] Arayüzde logo ya da telifli görsel yok
- [ ] DV-11 (hakaret) ve DV-12 (bahis) testleri geçiyor
- [ ] OpenCode gizlilik politikası incelendi, rapora not edildi
- [ ] Raporda sınırlılıklar ve halüsinasyon örnekleri var
