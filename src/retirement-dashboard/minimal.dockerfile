FROM python:3.11-slim

WORKDIR /app

# Install just Flask
RUN pip install Flask==3.0.3

# Copy only the simple app
COPY simple_app.py /app/app.py

EXPOSE 8000

CMD ["python", "app.py"]
