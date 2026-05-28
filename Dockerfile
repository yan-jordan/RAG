# directory: Dockerfile
FROM python:3.11-slim

# ممانعت از ایجاد فایل‌های کش کامپایل پایتون (.pyc) در کانتینر
ENV PYTHONDONTWRITEBYTECODE=1
# ممانعت از ذخیره‌سازی بافر خروجی‌های لاگ پایتون برای پایش آنی لاگ‌ها
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# نصب ملزومات سیستمی توزیع دبیان برای اجرای روان کتابخانه‌های بهینه‌سازی
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل نیازمندی‌ها و نصب لایه‌های پکیج‌های پایتون
COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 🛑 اصلاح این خط (افزودن فاصله بین کلمه COPY، نقطه و مسیر مقصد)
COPY . /code/

# باز کردن پورت اصلی وب‌سایت جنگو
EXPOSE 8000

# اعمال مایگریشن‌ها و راه‌اندازی وب‌سرور جنگو بر روی پورت مشخص
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]