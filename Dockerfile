FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python api/manage.py seed_data && python api/manage.py runserver 0.0.0.0:8000"]
