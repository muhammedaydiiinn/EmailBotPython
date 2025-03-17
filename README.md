# Toplu E-posta Gönderim Sistemi

Bu Python projesi, CSV formatındaki e-posta listesinden alıcıları okuyarak kişiselleştirilmiş e-postalar göndermenizi sağlar.

## Özellikler

- CSV dosyasından alıcı listesi okuma
- Kişiselleştirilmiş e-posta içeriği
- Word dosyası ekleme desteği
- Gmail veya Outlook SMTP desteği
- Detaylı loglama sistemi
- Spam koruması için gönderim gecikmesi
- Hata yönetimi ve raporlama

## Gereksinimler

- Python 3.9 veya üzeri
- pandas
- smtplib (Python ile birlikte gelir)
- email.mime (Python ile birlikte gelir)

## Kurulum

1. Python 3.9 veya üzeri sürümü yükleyin
2. Gerekli paketleri yükleyin:
   ```
   pip install pandas
   ```

## Kullanım

1. `alistesi.csv` dosyasını hazırlayın (örnek format aşağıda)
2. `mulakat_sorulari.docx` dosyasını proje dizinine ekleyin
3. `mail_gonder.py` scriptini çalıştırın:
   ```
   python mail_gonder.py
   ```
4. İstendiğinde SMTP bilgilerini girin

## CSV Dosya Formatı

CSV dosyası aşağıdaki formatta olmalıdır:
```
email
ornek@email.com
```

## Güvenlik

- SMTP şifresi olarak uygulama şifresi kullanılmalıdır
- Gmail için: Google Hesap > Güvenlik > 2 Adımlı Doğrulama > Uygulama Şifreleri
- Outlook için: Microsoft Hesap > Güvenlik > Uygulama Şifreleri

## Log Dosyası

Tüm işlemler `log.txt` dosyasına kaydedilir:
- Başarılı gönderimler
- Hatalar
- SMTP bağlantı sorunları
- Dosya işlem hataları

## Notlar

- Her e-posta gönderimi arasında 2 saniye bekleme süresi vardır
- Spam filtrelerine takılmamak için dikkatli kullanılmalıdır
- Büyük e-posta listeleri için uzun süre gerekebilir 