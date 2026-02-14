# 🚀 راهنمای استقرار نوبان روی سرور چابکان

**سرور:** `noban.chbk.dev`  
**GitHub:** `https://github.com/itwman/noban`  
**دیتابیس:** MySQL چابکان (ریموت)

---

## مرحله ۱: ارسال به GitHub

```bash
cd C:\xampp\htdocs\NoBan

git init
git add .
git commit -m "Production ready - Chabokan deployment"
git remote add origin https://github.com/itwman/noban.git
git branch -M main
git push -u origin main
```

---

## مرحله ۲: روی سرور چابکان (SSH)

### ۲.۱ نصب وابستگی‌ها
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv \
    nginx redis-server default-libmysqlclient-dev \
    build-essential pkg-config git supervisor
```

### ۲.۲ دریافت کد
```bash
cd /home
sudo mkdir -p noban && sudo chown $USER:$USER noban
git clone https://github.com/itwman/noban.git /home/noban/NoBan
cd /home/noban/NoBan
```

### ۲.۳ محیط مجازی و پکیج‌ها
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### ۲.۴ تنظیم Environment
```bash
cp .env.production .env
nano .env
```

حتماً `SECRET_KEY` را عوض کنید:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### ۲.۵ Migrate و Static
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### ۲.۶ تست سریع
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## مرحله ۳: تنظیم سرویس‌ها

### Nginx
```bash
sudo cp deploy/nginx/noban-http-only.conf /etc/nginx/sites-available/noban
sudo ln -sf /etc/nginx/sites-available/noban /etc/nginx/sites-enabled/noban
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Supervisor
```bash
sudo mkdir -p /var/log/noban
sudo chown $USER:$USER /var/log/noban
sudo cp deploy/supervisor/noban.conf /etc/supervisor/conf.d/noban.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start noban
```

---

## مرحله ۴: SSL (در صورت نیاز)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d noban.chbk.dev
```

---

## آپدیت بعدی

```bash
cd /home/noban/NoBan
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart noban
```

---

## اطلاعات دیتابیس

| پارامتر | مقدار |
|---------|-------|
| Host | services.irn6.chabokan.net |
| Port | 14473 |
| Database | noban258_freddie |
| User | noban258_freddie |

---

## عیب‌یابی

```bash
# لاگ Gunicorn
sudo tail -f /var/log/noban/gunicorn-error.log

# لاگ Nginx
sudo tail -f /var/log/nginx/error.log

# وضعیت سرویس‌ها
sudo supervisorctl status noban
sudo systemctl status nginx
```
