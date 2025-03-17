from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from cryptography.fernet import Fernet
import os
from base64 import b64encode, b64decode

db = SQLAlchemy()

# Şifreleme anahtarı oluşturma/yükleme
def get_encryption_key():
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        key = Fernet.generate_key()
        with open('.env', 'a') as f:
            f.write(f'\nENCRYPTION_KEY={key.decode()}\n')
    return key if isinstance(key, bytes) else key.encode()

# Şifreleme nesnesi
_fernet = None
def get_fernet():
    global _fernet
    if _fernet is None:
        _fernet = Fernet(get_encryption_key())
    return _fernet

class EmailHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    subject = db.Column(db.String(255))  # Gönderilen e-postanın konusu
    recipient_name = db.Column(db.String(255))  # Alıcının adı
    recipient_company = db.Column(db.String(255))  # Alıcının şirketi
    attachment_sent = db.Column(db.Boolean, default=False)  # Ek dosya gönderildi mi?
    ip_address = db.Column(db.String(45))  # Gönderen IP adresi

    def __repr__(self):
        return f'<EmailHistory {self.recipient} - {self.status}>'

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smtp_server = db.Column(db.String(255), nullable=False, default='smtp.gmail.com')
    smtp_port = db.Column(db.Integer, nullable=False)
    smtp_username = db.Column(db.String(255), nullable=False)
    _smtp_password = db.Column('smtp_password', db.String(255))
    sender_email = db.Column(db.String(255), nullable=False)
    sender_name = db.Column(db.String(255), nullable=False)
    email_subject = db.Column(db.String(255), nullable=False)
    email_body = db.Column(db.Text, nullable=False)
    attachment_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    delay_between_emails = db.Column(db.Integer, default=2)  # E-postalar arası gecikme (saniye)
    max_daily_emails = db.Column(db.Integer, default=100)  # Günlük maksimum e-posta sayısı

    @property
    def smtp_password(self):
        """SMTP şifresini çöz ve döndür."""
        if not self._smtp_password:
            return None
        try:
            encrypted_bytes = b64decode(self._smtp_password)
            decrypted_bytes = get_fernet().decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            print(f"Şifre çözme hatası: {e}")
            return None

    @smtp_password.setter
    def smtp_password(self, password):
        """SMTP şifresini şifrele ve kaydet."""
        if not password:
            self._smtp_password = None
            return
            
        try:
            if isinstance(password, str):
                password = password.encode()
            encrypted_bytes = get_fernet().encrypt(password)
            self._smtp_password = b64encode(encrypted_bytes).decode()
        except Exception as e:
            print(f"Şifre şifreleme hatası: {e}")
            self._smtp_password = None

    def __repr__(self):
        return f'<Settings {self.smtp_username}>'

