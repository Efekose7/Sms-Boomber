 Efe Kose SMS B00MBER V2

Bu proje, SMS gönderimi için geliştirilmiş bir araçtır. Python ile yazılmıştır ve hem Termux (Android) hem de Kali Linux (Linux) üzerinde kolayca çalıştırılabilir.

 Özellikler
- Python 3 ile uyumlu
- Kolay kurulum
- Açık kaynak

 Kurulum

 1. Gerekli Paketleri Yükleyin

**Termux için:**
```bash
pkg update && pkg install python git -y
```

**Kali Linux için:**
```bash
sudo apt update && sudo apt install python3 git -y
```

 2. Repoyu Klonlayın
```bash
git clone https://github.com/Efekose7/Sms-Boomber.git
cd Sms-Boomber
```

 3. Gereksinimleri Yükleyin
```bash
pip install -r requirements.txt
```

 4. Programı Başlatın
```bash
python main.py
```

## Notlar
- Python 3 yüklü olmalıdır.
- `services_config.py` dosyasını kendi servis bilgilerinize göre düzenleyebilirsiniz.
- Herhangi bir hata ile karşılaşırsanız, lütfen bir issue açın.

---

**Bu proje eğitim amaçlıdır. Lütfen yasalara uygun şekilde kullanınız.** 
