FROM python:3.12-slim

WORKDIR /frontend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Streamlit needs this env variable in Docker
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]
