# Ses listesi (sounds/ klasörüne koy: ad.ogg, ad.mp3 veya ad.wav)
Hepsi mono ya da stereo olabilir, kısa tutulmalıdır. Konumlandırmayı oyun kendisi yapar.
Dosya yoksa oyun yerine yapay ses üretir.

| Ad | Süre | Nasıl bir ses |
|---|---|---|
| ambient | 30-60 sn, döngü | Sunucu odası uğultusu: alçak vantilatör, hafif elektrik vızıltısı, ara sıra uzaktan disk tıkırtısı. Dikkat dağıtmayacak kadar sakin, dikişsiz döngü |
| boot | 1-2 sn | Cihaz açılışı: alçaktan yükselen elektronik süpürme, sonunda kısa dijital tık |
| click | 0.05 sn | Çok kısa mekanik klavye tuşu ya da röle tıkı |
| error | 0.4 sn | Alçak, sert, vızıltılı "reddedildi" sesi (buzzer) |
| ok | 0.4 sn | Kısa, yükselen üç notalı neşeli onay bipi |
| ping | 0.2 sn | Sonar benzeri temiz, tek bip. Tara ve portlar komutlarında sağdan sola dizilir, bu yüzden kuyruğu kısa olmalı |
| connect | 1-2 sn | Eski çevirmeli modem el sıkışması: tiz bip-bop, ardından cızırtı |
| tick | 0.05 sn | Çok kısa, kuru saat tıkı ya da metronom. Oyunun izlenme göstergesi, sürekli duyulacak, tiz ve yorucu olmamalı. Perdesi oyunda değişir |
| alarm | 1-1.5 sn | Siren ya da yüksek sesli iki tonlu uyarı. Tehlike hissi versin |
| exploit | 0.7 sn | Alçak bir gümbürtü (thump) ve ardından yükselen dijital cızırtı, kapının kırılması gibi |
| unlock | 1 sn | Kasa kapağı açılması, mekanik "klak" ardından yükselen parlak çınlama |
| dl | 0.3 sn | Kısa veri aktarım cıvıltısı, hızlı bip bip bip. İndirme boyunca her saniye tekrar eder |
| warn | 0.4 sn | Tiz, keskin çift bip (güvenlik duvarı uyarısı). Net duyulmalı, çünkü hangi kulaktan geldiğine karar veriliyor |
| block | 0.3 sn | Kısa kalkan sesi: hızlı "şş" ve parlak çınlama, saldırıyı savuşturma hissi |
| t1 | 0.4 sn | Ton kilidi, en kalın nota (yaklaşık 262 Hz, do). Yumuşak, çan ya da marimba benzeri |
| t2 | 0.4 sn | Aynı enstrüman, bir kademe ince (yaklaşık 330 Hz, mi) |
| t3 | 0.4 sn | Aynı enstrüman, daha ince (yaklaşık 415 Hz, sol diyez) |
| t4 | 0.4 sn | Aynı enstrüman, en ince (yaklaşık 523 Hz, do, bir oktav yukarı) |
| clear | 0.8 sn | Kayıt silme: hızlıca alçalan "vınnn" süpürmesi, silgi gibi |
| win | 3 sn | Zafer fanfarı: yükselen parlak arpej, sonunda uzun nota |
| lose | 2 sn | Düşen, bozulan elektronik ses, ardından cızırtılı kesilme (bağlantı kopması) |

## Nereden bulunur
freesound.org (lisans filtresi: CC0), pixabay.com/sound-effects, kenney.nl (CC0 ses paketleri).
Kendin üretirsen: Audacity (Generate menüsü ile ton, gürültü, süpürme üretebilirsin) ya da sfxr/jsfxr.

## Yeni eklenen sesler (Python sürümü)
| Ad | Süre | Nasıl bir ses |
|---|---|---|
| coin | 0.5 sn | Bozuk para ya da kasa "ding-ding" sesi, kredi kazanınca |
| lock | 0.6 sn | Frekans kilidi tam oturunca: net bir "klik" ve parlak çınlama |

Not: Python sürümünde `tick` ve `ping` gibi sesler dosyadan yüklenince perde (pitch) değişmez, sadece yapay sesler hızlanır/inceleşir. Dosya kullanacaksan tick için tek bir kısa ses yeterli.
