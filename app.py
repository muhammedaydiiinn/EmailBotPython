from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, EmailHistory, Settings
from email_service import EmailService
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mail_system.db')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Upload klasörünü oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Veritabanını başlat
db.init_app(app)

# E-posta servisini başlat
email_service = EmailService()

def init_app():
    """Uygulamayı başlatır ve veritabanını oluşturur."""
    with app.app_context():
        # Veritabanını oluştur
        db.create_all()
        
        # E-posta servisini başlat
        email_service.init_app(app)

@app.route('/')
def index():
    """Ana sayfa - E-posta gönderme formu ve geçmiş"""
    with app.app_context():
        history = EmailHistory.query.order_by(EmailHistory.sent_at.desc()).all()
        settings = Settings.query.first()
        return render_template('index.html', history=history, settings=settings)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """SMTP ve e-posta ayarları"""
    if request.method == 'POST':
        try:
            # Mevcut ayarları al
            current_settings = Settings.query.first()
            current_attachment = current_settings.attachment_path if current_settings else None

            # Word dosyası yükleme
            attachment_path = None
            if 'word_file' in request.files:
                file = request.files['word_file']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    attachment_path = filepath

            # SMTP şifresini kontrol et
            smtp_password = request.form.get('smtp_password', '').strip()
            
            # Eğer yeni ayar oluşturuluyorsa şifre zorunlu
            if not current_settings and not smtp_password:
                flash('İlk kurulum için SMTP şifresi gerekli.', 'error')
                return redirect(url_for('settings'))
                
            # Eğer mevcut ayarlar varsa ve şifre girilmemişse, mevcut şifreyi kullan
            if not smtp_password and current_settings:
                smtp_password = current_settings.smtp_password
                if not smtp_password:
                    flash('SMTP şifresi gerekli.', 'error')
                    return redirect(url_for('settings'))

            # Ayarları güncelle
            email_service.update_settings(
                smtp_server=request.form['smtp_server'].strip(),
                smtp_port=int(request.form['smtp_port']),
                smtp_username=request.form['smtp_username'].strip(),
                smtp_password=smtp_password,
                sender_email=request.form['sender_email'].strip(),
                sender_name=request.form['sender_name'].strip(),
                email_subject=request.form['email_subject'].strip(),
                email_body=request.form['email_body'].strip(),
                attachment_path=attachment_path or current_attachment
            )
            flash('Ayarlar başarıyla güncellendi.', 'success')
        except ValueError as e:
            flash(f'Geçersiz değer: {str(e)}', 'error')
        except Exception as e:
            flash(f'Ayarlar güncellenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('settings'))

    settings = Settings.query.first()
    return render_template('settings.html', settings=settings)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Dosya yükleme"""
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'filename': filename, 'filepath': filepath})

@app.route('/send', methods=['POST'])
def send_emails():
    if 'file' not in request.files:
        flash('Lütfen bir CSV dosyası seçin.', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Dosya seçilmedi.', 'error')
        return redirect(url_for('index'))
    
    if not file.filename.endswith('.csv'):
        flash('Lütfen geçerli bir CSV dosyası yükleyin.', 'error')
        return redirect(url_for('index'))
    
    try:
        # CSV dosyasını UTF-8 encoding ile oku
        df = pd.read_csv(file, encoding='utf-8')
        
        # E-posta sütununu kontrol et
        if 'email' not in df.columns:
            flash('CSV dosyasında "email" sütunu bulunamadı.', 'error')
            return redirect(url_for('index'))
        
        # Boş e-postaları filtrele ve geçerli e-posta formatını kontrol et
        valid_emails = []
        for _, row in df.iterrows():
            email = str(row['email']).strip()
            if pd.notna(email) and '@' in email:
                valid_emails.append(email)
        
        if not valid_emails:
            flash('Geçerli e-posta adresi bulunamadı.', 'error')
            return redirect(url_for('index'))
        
        # E-postaları gönder
        result = email_service.send_bulk_emails(valid_emails)
        
        if result['failed'] > 0:
            flash(f"Toplam {result['total']} e-postadan {result['successful']} tanesi başarıyla gönderildi, {result['failed']} tanesi başarısız oldu.", 'warning')
        else:
            flash(f"Tüm e-postalar başarıyla gönderildi! ({result['successful']} adet)", 'success')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Dosya işlenirken bir hata oluştu: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    init_app()
    app.run(debug=True, port=3000)