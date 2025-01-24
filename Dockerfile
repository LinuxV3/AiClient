FROM python:3.12.3
WORKDIR /app
RUN python3 -m venv venv
RUN source venv/bin/activate
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3", "main.py"]
