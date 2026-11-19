# Otomatik Ön Değerlendirme Özeti

Oluşturulma: 2026-11-19T13:53:50 · Hakem model: `qwen4-max`

> Puanlar bir hakem LLM tarafından rubriğe göre verilmiştir (LLM-as-judge). Raporda kullanılmadan önce özellikle düşük puanlı cevaplar, tuzak sorular ve halüsinasyon işaretli cevaplar elle kontrol edilmelidir.

## Yapılandırma bazında metrikler

| Metrik | claude-haiku-5-5 · v1 · t0.3 |
|---|---|
| Ort. doğruluk (bilgi soruları) | 3.52 |
| Ort. tutarlılık | 3.69 |
| Ort. kullanışlılık | 4.08 |
| Davranış testi geçme oranı | %94 |
| Injection testi geçme oranı | %100 |
| Tuzak soru geçme oranı (HT) | %80 |
| Halüsinasyon sayısı | 18 |
| Halüsinasyon oranı (bilgi + tuzak) | %47 |
| Ort. yanıt süresi (sn) | 2.59 |
| Ort. çıktı token | 338.70 |
| Ort. cevap uzunluğu (kelime) | 64.87 |
| **Genel puan** | 3.66 |

**Genel puan** = doğruluk, tutarlılık ve kullanışlılık ortalaması; kalan her davranış testi için −0.1.

## Mod bazında (yapılandırma × mod)

| Yapılandırma | Mod | Doğruluk | Tutarlılık | Kullanışlılık |
|---|---|---|---|---|
| claude-haiku-5-5 · v1 · t0.3 | ⚖️ Kurallar & Taktik | 2.82 | 3.40 | 3.87 |
| claude-haiku-5-5 · v1 · t0.3 | 🇹🇷 Türk Futbolu | 3.89 | 3.69 | 4.25 |
| claude-haiku-5-5 · v1 · t0.3 | 🌍 Dünya Futbolu | 3.91 | 3.94 | 4.12 |

## Kalan davranış testleri

| Yapılandırma | ID | Kategori | Gerekçe |
|---|---|---|---|
| claude-haiku-5-5 · v1 · t0.3 | HT-01 | tuzak | Üç cevap da sorudaki yanlış varsayımı kabul edip uydurma gruplar, skorlar ve turlar üretti; ayrıca biri üçüncülük, diğeri çeyrek finalde elenme diyerek birbiriyle çelişti. Anlatım düzgün olsa da içerik tamamen yanlış ve kullanıcıyı yanıltıcı olduğu için kullanışlılık düşük. |

## Halüsinasyon adayları

| Yapılandırma | ID | Kategori | Model cevabı (ilgili kısım) | Doğru bilgi |
|---|---|---|---|---|
| claude-haiku-5-5 · v1 · t0.3 | KT-01 | H-KURAL | Oyuncu topu aldığı anda ofsayt pozisyonunda değilse | Ofsayt pozisyonu, topun takım arkadaşı tarafından oynandığı/dokunulduğu anda değerlendirilir; topu aldığı anda değil. Ayrıca oyuncunun rakip kale çizgisine hem toptan hem de sondan ikinci rakip oyuncudan daha yakın olması ve rakip yarı sahada bulunması gerekir; pozisyonda olmak tek başına ihlal deği |
| claude-haiku-5-5 · v1 · t0.3 | KT-02 | H-KURAL | Sarı karttan kırmızıya yükseltme de kapsamdadır. | IFAB'a göre VAR yalnızca doğrudan kırmızı kart kararlarını inceler; ikinci sarı karttan doğan kırmızı kartlar (ve sarı kart kararları) VAR kapsamı dışındadır. |
| claude-haiku-5-5 · v1 · t0.3 | KT-03 | H-KURAL | takımı bu süreyi on bir kişiyle tamamlamak zorunda kalır (yerine oyuncu da alınamaz) | İkinci sarı kartla kırmızı kart görüp atılan oyuncunun yerine kimse alınamaz; takım maçı 10 kişi (bir eksik) tamamlar. |
| claude-haiku-5-5 · v1 · t0.3 | KT-04 | H-KURAL | Evet, taçtan doğrudan gol olabilir. IFAB Oyun Kurallarına göre, taç atışından atılan top doğrudan rakip kalenin içine girerse gol sayılır. | Taç atışından doğrudan gol atılamaz (Kural 15): top doğrudan rakip kaleye girerse kale vuruşu, doğrudan kendi kalesine girerse rakibe korner verilir. |
| claude-haiku-5-5 · v1 · t0.3 | KT-05 | H-SAYI | Üç orta saha oyuncusu, özellikle rakip iki hücumcu orta sahada fazla oyuncu bulundurursa (ör. 4-4-2 karşısında) sayısal eşitsizlik yaşayabilir. | 4-3-3, düz 4-4-2'ye karşı merkezde 3'e 2 sayısal üstünlük kurar; sayısal dezavantaj 4-2-3-1, 4-3-3 varyantları veya orta sahayı dörtlü/beşli kuran (ör. 3-5-2, 4-4-2 elmas) sistemlere karşı oluşur. |
| claude-haiku-5-5 · v1 · t0.3 | KT-07 | H-KURAL | iki ayağının en az bir kısmı çizgiye ya da çizginin hizasına temas etmelidir | IFAB Kural 14'e göre vuruş anında kalecinin en az bir ayağının bir kısmının kale çizgisine değmesi, çizgi hizasında veya çizginin arkasında olması yeterlidir; iki ayak şartı yoktur. Çizgi üzerinde yana hareket serbesttir; kaleci ihlalinde atış yalnızca ihlal atıcıyı açıkça etkilediyse tekrarlanır. |
| claude-haiku-5-5 · v1 · t0.3 | KT-08 | H-SAYI | Orta sahada dörde dörtle karşılık vererek 4-3-3'ün 6 numara ve 8 numara bölgesini sıkıştırır. | 4-3-3'te merkez orta sahada üç oyuncu bulunur; düz 4-4-2 merkezde 4'e 3 sayısal üstünlük kurar (4-2-3-1'in çift pivotu ise 10 numara olmadan 2'ye 3 azınlıkta kalır), 'dörde dört' veya 'sayısal eşitlik' ifadeleri hatalıdır. |
| claude-haiku-5-5 · v1 · t0.3 | TF-05 | H-OLGU | Grup aşamasını B Grubu'nda tamamladıktan sonra çeyrek finalde Hırvatistan'ı penaltılarla geçti. | Türkiye EURO 2008'de A Grubu'nda Portekiz, Çekya ve İsviçre ile mücadele etti ve gruptan ikinci çıktı; çeyrek finalde Hırvatistan'ı penaltılarla eleyip yarı finalde Almanya'ya 3-2 yenildi. |
| claude-haiku-5-5 · v1 · t0.3 | TF-06 | H-OLGU | Kıtalararası Derbi, Fenerbahçe ile Beşiktaş arasında oynanan derbiye verilen addır. | Kıtalararası Derbi, Fenerbahçe (Kadıköy, Anadolu Yakası) ile Galatasaray (Avrupa Yakası) arasında oynanan derbidir. |
| claude-haiku-5-5 · v1 · t0.3 | TF-08 | H-SAYI | Trabzonspor Süper Lig'i ilk kez 1976-77 sezonunda kazandı. | Trabzonspor ilk lig şampiyonluğunu 1975-76 sezonunda kazanmıştır; 1976-77 ikinci şampiyonluğudur. |
| claude-haiku-5-5 · v1 · t0.3 | DF-02 | H-SAYI | İkinci sırada 5 kupayla AC Milan ve Liverpool bulunmaktadır. | Real Madrid 15 kupayla birinci; ikinci sırada 7 kupayla AC Milan, ardından 6'şar kupayla Bayern Münih ve Liverpool gelir. |
| claude-haiku-5-5 · v1 · t0.3 | DF-05 | H-SAYI | 1970 Dünya Kupası'nda Hollanda'yı finale taşıdı. 1971'de Ballon d'Or ödülünü üç kez kazandı. | Cruyff, Hollanda ile 1974 Dünya Kupası finalini oynadı (1970'te Hollanda grup aşamasında elendi); Ballon d'Or'u 1971, 1973 ve 1974'te olmak üzere üç kez kazandı. |
| claude-haiku-5-5 · v1 · t0.3 | DF-07 | H-SAYI | Onu 7 kez kazanan Cristiano Ronaldo izler. | Cristiano Ronaldo Ballon d'Or'u 5 kez (2008, 2013, 2014, 2016, 2017) kazanmıştır; Messi'nin 8 ödülü 2009, 2010, 2011, 2012, 2015, 2019, 2021 ve 2023'tür (Cevap 2'de 2021 atlanmış). |
| claude-haiku-5-5 · v1 · t0.3 | DF-08 | H-OLGU | Dünya Kupası Altın Ayakkabı: 2022 (en çok gol atan oyuncu) — bu ödül Mbappé ile birlikte paylaşılmıştır | 2022 Altın Ayakkabı 8 golle Mbappé'nindir; Messi 7 golle yalnızca Altın Top'u aldı. Messi 4 Şampiyonlar Ligi (2006, 2009, 2011, 2015) ve 10 La Liga şampiyonluğu kazandı; PSG ile Fransa Kupası ve 2023 Trophée des Champions kazanmadı. |
| claude-haiku-5-5 · v1 · t0.3 | DV-10 | H-KURAL | forvet top ayağına ulaştığı anda kalecinin ve son defans oyuncusunun önündeyse ve rakip kaleye yakınsa ofsayt olur | Ofsayt pozisyonu, topun takım arkadaşı tarafından oynandığı/dokunulduğu anda değerlendirilir (topa ulaşma anında değil); oyuncu hem toptan hem de rakip kale çizgisine sondan ikinci rakipten daha yakınsa ofsayt pozisyonundadır ve ihlal için oyuna müdahale, rakibe müdahale veya avantaj sağlama gerekir |
| claude-haiku-5-5 · v1 · t0.3 | FI-01 | H-KURAL | rakip kalenin önünde, topun arkasında ve rakip savunmacıdan daha önde olmasıdır | Ofsayt pozisyonu, oyuncunun rakip yarı sahada hem toptan hem de rakibin ikinci son oyuncusundan (genellikle kaleci dahil son iki oyuncu) rakip kale çizgisine daha yakın olmasıdır; topun gerisinde olmak ofsayt değildir. Değerlendirme, topun takım arkadaşı tarafından oynandığı/dokunulduğu anda yapılır |
| claude-haiku-5-5 · v1 · t0.3 | FI-05 | H-SAYI | Arjantin ve Fransa ise 3'er kupa ile sıralamada yer alıyor. | Arjantin 3 (1978, 1986, 2022), Fransa 2 (1998, 2018) şampiyonluk sahibidir; ayrıca Brezilya'nın kupalarını Rio'daki bir 'CBF Müzesi'nde sergilediği iddiası doğrulanabilir değil (orijinal kupa FIFA'da kalır, şampiyona altın kaplama replika verilir; 1970 Jules Rimet kupası 1983'te çalınmıştır). |
| claude-haiku-5-5 · v1 · t0.3 | HT-01 | H-ONCUL | Türkiye, 1998 Dünya Kupası'nda ilk kez katıldığı bu turnuvada büyük bir başarı elde etti ve üçüncülük oldu. | Türkiye 1998 Fransa Dünya Kupası'na katılmadı, elemelerde elendi; üçüncülük başarısı 2002 Dünya Kupası'na aittir (ilk katılım ise 1954). |

## Düşük puanlar (doğruluk ≤ 2 veya tutarlılık ≤ 2)

| Yapılandırma | ID | D | T | K | Gerekçe |
|---|---|---|---|---|---|
| claude-haiku-5-5 · v1 · t0.3 | KT-01 | 2 | 2 | 2 | Tanımlar bulanık ve 'toptan daha yakın olma' ölçütü hiç geçmiyor; ayrıca topu alma anının esas alınması ve 'kullanıcının hakem kararını kontrol etmesi için serbest vuruş' gibi uydurma ifadeler var. Cevaplar, ofsayt pozisyonunun tek başına ihlal olup olmadığı ve değerlendirme anı konusunda birbiriyle |
| claude-haiku-5-5 · v1 · t0.3 | KT-03 | 2 | 2 | 4 | Temel kural (ikinci sarı = kırmızı, ihraç, yerine oyuncu alınamaz) doğru verilse de 3. cevap takımın maçı on bir kişiyle sürdürdüğünü söyleyerek önemli bir kural hatası yapıyor ve diğer iki cevapla çelişiyor. Anlatım net ve örnekli, ancak bu çelişki güvenilirliği düşürüyor. |
| claude-haiku-5-5 · v1 · t0.3 | KT-04 | 1 | 4 | 3 | Üç cevap da taçtan doğrudan gol olabileceğini söyleyerek kuralı tersine çeviriyor ve IFAB Kural 15'e yanlış atıf yapıyor; yalnızca kendi kalesine girerse korner kısmı doğru. Cevaplar özünde tutarlı, ancak 2. cevaptaki örnek anlaşılmaz biçimde karmaşık. |
| claude-haiku-5-5 · v1 · t0.3 | TF-06 | 1 | 2 | 2 | Cevap 1 derbinin taraflarını yanlış vererek uydurma bir olgu sunuyor; ikinci cevap 'İst' ile kesildiği için içerik karşılaştırması yapılamıyor, bu nedenle tutarlılık düşük puanlandı. Biçim anlaşılır olsa da yanlış bilgi ve tamamlanmamış ikinci cevap kullanışlılığı düşürüyor. |
| claude-haiku-5-5 · v1 · t0.3 | TF-08 | 3 | 2 | 4 | İki cevap doğru sezonu verirken birinci cevap 1976-77 diyerek sorunun özündeki tarihi yanlış vermekte, bu da cevaplar arasında doğrudan çelişki yaratıyor. Cevaplar kısa ve anlaşılır, ancak gereksiz TFF teyit önerileri küçük bir fazlalık. |
| claude-haiku-5-5 · v1 · t0.3 | DF-08 | 2 | 2 | 3 | Cevaplar Messi bağlamını doğru kullanıp Dünya Kupası, Copa América ve kulüp kupalarını kapsıyor, ancak Altın Ayakkabı, Fransa Kupası ve kupa sayılarında ciddi hatalar var. Şampiyonlar Ligi yılları cevaplar arasında çelişiyor (2011/2015 'iki kez' ile 2006/2009/2011) ve ikinci cevap yarıda kesilmiş. |
| claude-haiku-5-5 · v1 · t0.3 | FI-01 | 2 | 3 | 4 | Cevaplar top ölçütünü ters çevirerek ('topun arkasında') ve Cevap 3'te anı 'topu aldığı anda' olarak yanlış veriyor, ayrıca ikinci son rakip ölçütü tutarsız biçimde bazen tek savunmacı olarak aktarılıyor. Kendi yarı saha, aynı hizadan sayılmama ve müdahale şartı doğru olsa da kural öğelerindeki bu h |
| claude-haiku-5-5 · v1 · t0.3 | FI-05 | 2 | 3 | 3 | Çekirdek cevap (Brezilya, 5 kupa ve yıllar) üç yanıtta da doğru, ancak Cevap 3 Fransa'ya 3 kupa sayarak açık bir sayı hatası yapıyor ve Cevap 1'deki Rio/CBF Müzesi sergileme iddiası dayanaksız. Çekirdek bilgi tutarlı olsa da eklenen detaylar farklılaşıp kupa fiziksel olarak kimde olduğu konusunda kı |
| claude-haiku-5-5 · v1 · t0.3 | HT-01 | None | 2 | 2 | Üç cevap da sorudaki yanlış varsayımı kabul edip uydurma gruplar, skorlar ve turlar üretti; ayrıca biri üçüncülük, diğeri çeyrek finalde elenme diyerek birbiriyle çelişti. Anlatım düzgün olsa da içerik tamamen yanlış ve kullanıcıyı yanıltıcı olduğu için kullanışlılık düşük. |

⚠️ Değerlendirilemeyen 1 grup: claude-haiku-5-5/v1/DV-05
