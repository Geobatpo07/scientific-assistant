# Teslas.ai UI – Streamlit (CPU only)
FROM python:3.11-slim

WORKDIR /app

# Dépendances strictement nécessaires
RUN pip install --no-cache-dir streamlit requests

# Copier l'arborescence UI pour conserver le chemin app/ui/streamlit_app.py
RUN mkdir -p app/ui
COPY app/ui /app/app/ui

EXPOSE 8501

CMD ["streamlit", "run", "app/ui/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
