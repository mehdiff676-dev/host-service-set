# استخدام صورة بايثون رسمية
FROM python:3.11-slim

# تعيين مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملفات المتطلبات أولاً (للاستفادة من طبقات Docker cache)
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات التطبيق
COPY . .

# إنشاء مجلد uploads إذا لم يكن موجوداً
RUN mkdir -p uploads

# تعيين المنفذ
EXPOSE 10000

# متغير بيئة لتشغيل Flask في production
ENV FLASK_ENV=production

# أمر التشغيل
CMD ["python", "app.py"]