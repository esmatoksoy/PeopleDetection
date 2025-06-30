import os
from email.message import EmailMessage
import smtplib

class MailPhotoSender:
    def __init__(self, from_email, password, smtp_server, smtp_port):
        self.from_email = from_email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    def send_mail_with_image(self, subject, body, to_email, image_path):
        """
        Bir resim ekiyle birlikte e-posta gönderir.
        image_path, resim dosyasının tam ve geçerli bir yolu olmalıdır.
        """
        # Dosyanın var olup olmadığını kontrol etmek, hata ayıklamayı kolaylaştırır.
        if not os.path.exists(image_path):
            print(f"HATA: E-posta gönderilemedi çünkü resim dosyası bulunamadı: {image_path}")
            return # Dosya yoksa fonksiyonu durdur

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg.set_content(body)

        try:
            with open(image_path, 'rb') as img:
                img_data = img.read()
                # Dosya adını yoldan otomatik olarak al
                img_name = os.path.basename(image_path) 
                msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename=img_name)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.starttls()
                smtp.login(self.from_email, self.password)
                smtp.send_message(msg)
            print(f"E-posta sent to {to_email} successfully.")

        except Exception as e:
            print(f"E-posta error: {e}")
        
