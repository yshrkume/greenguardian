FROM python:3.9
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
