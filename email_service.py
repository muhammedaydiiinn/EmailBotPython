import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import os
from dotenv import load_dotenv
from models import db, EmailHistory, Settings
from flask import current_app
import base64

load_dotenv()

class EmailService:
    def __init__(self, app=None):
        self.settings = None
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Uygulama bağlamını başlatır."""
        self.app = app
        with app.app_context():
            self.settings = Settings.query.first()

    def _refresh_settings(self):
        """Ayarları veritabanından yeniden yükler."""
        if not self.app:
            raise RuntimeError("Flask uygulaması başlatılmamış")
            
        with self.app.app_context():
            self.settings = Settings.query.first()

    def update_settings(self, smtp_server, smtp_port, smtp_username, smtp_password, sender_email, sender_name, email_subject, email_body, attachment_path=None):
        """SMTP ve e-posta ayarlarını günceller."""
        if not self.app:
            raise RuntimeError("Flask uygulaması başlatılmamış")

        with self.app.app_context():
            # Mevcut ayarları kontrol et
            settings = Settings.query.first()
            
            if settings:
                # Mevcut ayarları güncelle
                settings.smtp_server = smtp_server
                settings.smtp_port = smtp_port
                settings.smtp_username = smtp_username
                if smtp_password:  # Şifre sadece değiştirilmek istendiğinde güncelle
                    settings.smtp_password = smtp_password
                settings.sender_email = sender_email
                settings.sender_name = sender_name
                settings.email_subject = email_subject
                settings.email_body = email_body
                if attachment_path:
                    settings.attachment_path = attachment_path
            else:
                # Yeni ayar oluştur
                settings = Settings(
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    smtp_username=smtp_username,
                    smtp_password=smtp_password,
                    sender_email=sender_email,
                    sender_name=sender_name,
                    email_subject=email_subject,
                    email_body=email_body,
                    attachment_path=attachment_path
                )
                db.session.add(settings)

            try:
                db.session.commit()
                self.settings = settings  # Yerel ayarları güncelle
            except Exception as e:
                db.session.rollback()
                raise e

    def send_email(self, recipient_email):
        """Tek bir e-posta gönderir."""
        # Gönderim öncesi ayarları yenile
        self._refresh_settings()
        
        if not self.settings:
            raise RuntimeError("E-posta ayarları bulunamadı")
            
        if not self.settings.smtp_password:
            raise RuntimeError("SMTP şifresi ayarlanmamış")
        
        try:
            # E-posta mesajını oluştur
            msg = MIMEMultipart()
            
            # Gönderen ve alıcı bilgilerini ayarla
            msg['From'] = f"{self.settings.sender_name}"
            msg['To'] = recipient_email
            msg['Subject'] = self.settings.email_subject

            # E-posta içeriğini oluştur
            text = MIMEText(self.settings.email_body, 'plain')
            text.set_charset('utf-8')
            msg.attach(text)

            # Dosya ekle
            if self.settings.attachment_path and os.path.exists(self.settings.attachment_path):
                with open(self.settings.attachment_path, 'rb') as f:
                    attachment = MIMEApplication(f.read(), _subtype='docx')
                    attachment.add_header('Content-Disposition', 'attachment',
                                       filename=os.path.basename(self.settings.attachment_path))
                    msg.attach(attachment)

            # SMTP sunucusuna bağlan
            server = smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port)
            server.starttls()
            
            # SMTP kimlik doğrulama
            smtp_password = self.settings.smtp_password
            if not smtp_password:
                raise ValueError("SMTP şifresi bulunamadı")
                
            server.login(self.settings.smtp_username, smtp_password)

            # E-postayı gönder
            server.sendmail(
                from_addr=self.settings.sender_email,
                to_addrs=recipient_email,
                msg=msg.as_string()
            )

            # Bağlantıyı kapat
            server.quit()

            # Başarılı gönderimi kaydet
            with self.app.app_context():
                history = EmailHistory(
                    recipient=recipient_email,
                    status='success',
                    subject=self.settings.email_subject,
                    attachment_sent=bool(self.settings.attachment_path)
                )
                db.session.add(history)
                db.session.commit()

            return True, None

        except Exception as e:
            error_msg = f"E-posta gönderimi başarısız: {str(e)}"
            # Hata durumunu kaydet
            with self.app.app_context():
                history = EmailHistory(
                    recipient=recipient_email,
                    status='failed',
                    error_message=error_msg,
                    subject=self.settings.email_subject,
                    attachment_sent=bool(self.settings.attachment_path)
                )
                db.session.add(history)
                db.session.commit()
            return False, error_msg

    def send_bulk_emails(self, email_list):
        """Toplu e-posta gönderir."""
        # Gönderim öncesi ayarları yenile
        self._refresh_settings()
        
        if not self.settings:
            raise RuntimeError("E-posta ayarları bulunamadı")
        
        total = len(email_list)
        successful = 0
        failed = 0
        errors = []

        for i, email in enumerate(email_list, 1):
            success, error = self.send_email(email)
            if success:
                successful += 1
            else:
                failed += 1
                errors.append(f"{email}: {error}")

            # Her gönderim arasında gecikme
            if i < total:
                time.sleep(self.settings.delay_between_emails)

        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'errors': errors
        }

    def get_email_history(self, limit=50):
        """Gönderilen e-postaların geçmişini getirir."""
        if not self.app:
            raise RuntimeError("Flask uygulaması başlatılmamış")
            
        with self.app.app_context():
            return EmailHistory.query.order_by(EmailHistory.sent_at.desc()).limit(limit).all() 