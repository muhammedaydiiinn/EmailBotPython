# Toplu E-posta Gönderim Sistemi

Bu Flask tabanlı web uygulaması, toplu e-posta gönderimi için geliştirilmiş profesyonel bir sistemdir. CSV dosyasından alıcı listesini okuyarak, kişiselleştirilmiş e-postalar göndermenizi sağlar.

## 🚀 Özellikler

- 📊 CSV dosyasından alıcı listesi okuma
- ✉️ Kişiselleştirilmiş e-posta içeriği oluşturma
- 📎 Dosya ekleme desteği (Word, PDF vb.)
- 🔒 Gmail veya Outlook SMTP desteği
- 📝 Detaylı loglama ve gönderim geçmişi
- ⏱️ Spam koruması için akıllı gönderim gecikmesi
- 💾 SQLite veritabanı ile veri saklama
- 🌐 Web arayüzü ile kolay kullanım

## 🛠️ Teknik Gereksinimler

```
Python 3.9+
Flask 2.0+
pandas 1.3+
python-docx 0.8+
flask-sqlalchemy 2.5+
python-dotenv 0.19+
```

## 🔧 Kurulum

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/muhammedaydiiinn/EmailBotPython.git
   cd EmailBotPython
   ```

2. Sanal ortam oluşturun ve aktifleştirin:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Gereksinimleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. `.env` dosyasını oluşturun:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///mail_system.db
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

## 🚦 Çalıştırma

1. Uygulamayı başlatın:
   ```bash
   python app.py
   ```

2. Tarayıcınızda `http://localhost:3000` adresine gidin

## 📋 CSV Dosya Formatı

CSV dosyanız aşağıdaki formatta olmalıdır:

```csv
email
user@example.com
jane@example.com
```

## 🔐 Güvenlik Notları

- Gmail için "Uygulama Şifresi" kullanın:
  1. Google Hesabınıza gidin
  2. Güvenlik > 2 Adımlı Doğrulama'yı açın
  3. Uygulama Şifreleri > Yeni şifre oluştur

- Outlook için:
  1. Microsoft hesap ayarlarına gidin
  2. Güvenlik > Uygulama şifreleri
  3. Yeni bir uygulama şifresi oluşturun

## 📊 Veritabanı Yapısı

- `EmailHistory`: Gönderim geçmişi
- `Settings`: SMTP ve e-posta ayarları

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Branch'inizi push edin
5. Pull Request oluşturun
