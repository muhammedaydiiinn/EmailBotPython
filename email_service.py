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
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Uygulama bağlamını başlatır ve ayarları yükler."""
        with app.app_context():
            self.settings = Settings.query.first()
            if not self.settings:
                self.settings = Settings(
                    smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                    smtp_port=int(os.getenv('SMTP_PORT', 587)),
                    smtp_username=os.getenv('SMTP_USERNAME', ''),
                    smtp_password=os.getenv('SMTP_PASSWORD', ''),
                    sender_email=os.getenv('SMTP_USERNAME', ''),
                    sender_name="İK Ekibi",
                    email_subject="Mülakat Soruları",
                    email_body="Merhaba,\n\nMülakat soruları ekte yer almaktadır.\n\nSaygılarımızla,\nİK Ekibi",
                    attachment_path="mulakat_sorulari.docx"
                )
                db.session.add(self.settings)
                db.session.commit()

    def update_settings(self, smtp_server, smtp_port, smtp_username, smtp_password, sender_email, sender_name, email_subject, email_body, attachment_path=None):
        """SMTP ve e-posta ayarlarını günceller."""
        with current_app.app_context():
            self.settings.smtp_server = smtp_server
            self.settings.smtp_port = smtp_port
            self.settings.smtp_username = smtp_username
            self.settings.smtp_password = smtp_password
            self.settings.sender_email = sender_email
            self.settings.sender_name = sender_name
            self.settings.email_subject = email_subject
            self.settings.email_body = email_body
            if attachment_path:
                self.settings.attachment_path = attachment_path
            db.session.commit()

    def send_email(self, recipient_email):
        """Tek bir e-posta gönderir."""
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
            server.login(self.settings.smtp_username, self.settings.smtp_password)

            # E-postayı gönder
            server.sendmail(
                from_addr=self.settings.sender_email,
                to_addrs=recipient_email,
                msg=msg.as_string()
            )

            # Bağlantıyı kapat
            server.quit()

            # Başarılı gönderimi kaydet
            with current_app.app_context():
                history = EmailHistory(
                    recipient=recipient_email,
                    status='success'
                )
                db.session.add(history)
                db.session.commit()

            return True, None

        except Exception as e:
            # Hata durumunu kaydet
            with current_app.app_context():
                history = EmailHistory(
                    recipient=recipient_email,
                    status='failed',
                    error_message=str(e)
                )
                db.session.add(history)
                db.session.commit()
            return False, str(e)

    def send_bulk_emails(self, email_list):
        """Toplu e-posta gönderir."""
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

            # Her gönderim arasında 2 saniye bekle
            if i < total:
                time.sleep(2)

        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'errors': errors
        }

    def get_email_history(self, limit=50):
        """Gönderilen e-postaların geçmişini getirir."""
        with current_app.app_context():
            return EmailHistory.query.order_by(EmailHistory.sent_at.desc()).limit(limit).all() 