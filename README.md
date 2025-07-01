Efe Kose SMS Bomber V3

Bu proje, çoklu SMS servisleri üzerinden SMS göndermek için geliştirilmiştir. Replit ve Termux gibi ortamlarda kolayca çalıştırılabilir.

Kurulum (Replit)

1. Bu projeyi Replit'e yükleyin veya klonlayın.
2. `requirements.txt` dosyası otomatik olarak bağımlılıkları yükleyecektir.
3. `main.py` dosyasını çalıştırmak için Replit arayüzünde **Run** butonuna tıklayın veya terminalde:
   ```sh
   python3 main.py
   ```

Özellikler
- Çoklu SMS servisi desteği
- Renkli ve modern log sistemi
- Thread (çoklu istek) desteği
- Kullanıcı dostu arayüz

Termux veya Linux'ta Çalıştırmak için
1. Projeyi indirin veya klonlayın.
2. Terminalde:
   ```sh
   pip install -r requirements.txt
   python3 main.py
   ```

Notlar
- Python 3.8+ önerilir.
- Bazı servisler IP engeli, rate limit veya ek güvenlik nedeniyle çalışmayabilir.
- Sadece eğitim ve test amaçlı kullanınız. 