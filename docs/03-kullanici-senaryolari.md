# 03 – Kullanıcı Senaryoları

## 1. User Story'ler

| ID | User Story | Kabul Kriteri | Gereksinim |
|---|---|---|---|
| US-01 | Bir **yeni izleyici** olarak ofsayt kuralını sade bir dille sormak istiyorum, böylece maçları daha iyi anlayabilirim. | Cevap Türkçe, jargonsuz ve en az bir örnek içeriyor. | FR-01, FR-02 |
| US-02 | Bir **kullanıcı** olarak konu modunu seçmek istiyorum, böylece cevaplar ilgilendiğim alana odaklansın. | Kenar çubuğunda 3 mod var; seçim cevapların odağını değiştiriyor. | FR-03 |
| US-03 | Bir **taktik meraklısı** olarak önceki soruma atıfta bulunan bir takip sorusu sormak istiyorum ("Peki bu dizilişin zayıf yanı ne?"). | Model önceki mesajdaki dizilişi hatırlayarak cevap veriyor. | FR-04 |
| US-04 | Bir **kullanıcı** olarak sohbeti temizlemek istiyorum, böylece yeni bir konuya baştan başlayabilirim. | "Sohbeti Temizle" butonu geçmişi siliyor. | FR-05 |
| US-05 | Bir **kullanıcı** olarak futbol dışı bir soru sorduğumda bunun kapsam dışı olduğunu öğrenmek istiyorum. | Model kibarca reddediyor ve futbolla ilgili bir soru önerebiliyor. | FR-07 |
| US-06 | Bir **Süper Lig taraftarı** olarak bu sezonki puan durumunu sorduğumda bilginin güncel olmayabileceğini bilmek istiyorum. | Cevap, bilgilerin belirli bir tarihe kadar olduğunu belirten bir uyarı içeriyor. | FR-09 |
| US-07 | Bir **geliştirici** olarak test sorularını tek komutla çalıştırmak istiyorum, böylece prompt değişikliklerinin etkisini karşılaştırabilirim. | `python run_tests.py` tüm soruları çalıştırıp sonuçları dosyaya yazıyor. | FR-10 |
| US-08 | Bir **kullanıcı** olarak API'de sorun çıktığında ne olduğunu anlamak istiyorum. | Uygulama çökmüyor, Türkçe bir hata mesajı görünüyor. | FR-11 |
| US-09 | Bir **kullanıcı** olarak cevapların ne kadar yaratıcı ya da tutarlı olacağını ayarlamak istiyorum. | Kenar çubuğunda 0.0–1.0 arası bir temperature slider'ı var; değer değişince yeni cevaplar bu değerle üretiliyor. | FR-12 |
| US-10 | Bir **geliştirici** olarak testleri farklı temperature değerleriyle çalıştırmak istiyorum, böylece tutarlılığa etkisini ölçebilirim. | `python run_tests.py --temperature 0.7` çalışıyor; değer sonuç dosyasında görünüyor. | FR-13 |
| US-12 | Bir **kullanıcı** olarak bir cevabı beğenip beğenmediğimi belirtmek istiyorum. | Her cevabın altında 👍/👎 var; kenar çubuğunda oturum özeti güncelleniyor. | FR-14 |
| US-13 | Bir **kullanıcı** olarak ana model çalışmadığında da cevap almak istiyorum. | Ana model hata verince cevap yedek modelden geliyor ve "Yedek model kullanıldı" notu görünüyor. | FR-16 |
| US-14 | Bir **geliştirici** olarak aynı test setini 3 modelde çalıştırmak istiyorum, böylece model seçimini veriyle gerekçelendirebilirim. | `python run_tests.py --models a,b,c` 3 modelin sonuçlarını süre ve token bilgisiyle kaydediyor. | FR-15, FR-17 |
| US-11 | Bir **uygulama sahibi** olarak kötü niyetli kullanıcıların sistem promptunu ele geçirmesini veya kotayı tüketmesini engellemek istiyorum. | Injection testleri geçiyor; hız sınırı aşılınca uyarı gösteriliyor. | NFR-08 |

## 2. Kullanım Senaryoları

### Senaryo A – Kural öğrenme (Elif, Kurallar & Taktik)

1. Elif uygulamayı açar. Varsayılan mod "Kurallar & Taktik"tir.
2. "VAR hangi durumlarda devreye girer?" yazar.
3. Sistem soruyu ilgili sistem promptuyla LLM'e gönderir.
4. Elif, VAR'ın devreye girdiği 4 durumu (gol, penaltı, direkt kırmızı kart, kimlik karışıklığı) maddeler halinde görür.
5. Takip sorusu sorar: "Peki hakem VAR'a rağmen kararını değiştirmezse ne olur?"
6. Model önceki bağlamı kullanarak cevap verir.

### Senaryo B – Tarihî bilgi doğrulama (Mehmet, Türk Futbolu)

1. Mehmet modu "Türk Futbolu" olarak değiştirir. Sohbet geçmişi sıfırlanır.
2. "Türkiye 2002 Dünya Kupası'nda hangi takımları yendi?" diye sorar.
3. Model maçları listeler.
4. Mehmet "Bu sezon Süper Lig'de kim lider?" diye sorar.
5. Model, bilgisinin güncel olmayabileceğini belirtir ve güncel puan durumu için resmî kaynaklara bakmasını önerir.

### Senaryo C – Konu dışı soru

1. Kullanıcı herhangi bir modda "Bana makarna tarifi verir misin?" yazar.
2. Model yalnızca futbol konusunda yardımcı olabildiğini söyler ve örnek bir futbol sorusu önerir.

### Senaryo D – Mod dışı futbol sorusu (Can, Türk Futbolu modunda)

1. Can, Türk Futbolu modundayken "Guardiola'nın Barcelona'daki taktik anlayışı neydi?" diye sorar.
2. Model kısa bir cevap verir ve detay için "Dünya Futbolu" ya da "Kurallar & Taktik" moduna geçmesini önerir.

### Senaryo E – Temperature ayarı (Can)

1. Can, Dünya Futbolu modunda "Total futbolu bir benzetmeyle anlat" diye sorar. Temperature varsayılan değerde (0.3).
2. Cevap biraz kuru gelince slider'ı 0.8'e çeker ve soruyu tekrar sorar.
3. Daha yaratıcı benzetmeler içeren bir cevap alır.
4. İstatistik sorularına geçmeden önce slider'ı tekrar 0.2'ye indirir.

### Senaryo F – Otomatik test (Geliştirici)

1. Geliştirici `tests/test_questions.json` dosyasını hazırlar.
2. `python run_tests.py` komutunu çalıştırır.
3. Script her soruyu ilgili modla modele gönderir.
4. Sonuçlar `tests/results/results_<tarih>.json` ve `.csv` dosyalarına yazılır.
5. Geliştirici cevapları değerlendirme rubriğine göre puanlar (bkz. [04-test-plani.md](04-test-plani.md)).
