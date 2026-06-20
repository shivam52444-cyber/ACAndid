# -----------------------------
# 1. BASE IMAGE
# -----------------------------
FROM python:3.11-slim

# -----------------------------
# 2. SYSTEM DEPENDENCIES
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# 3. WORKDIR
# -----------------------------
WORKDIR /app

# -----------------------------
# 4. COPY REQUIREMENTS FIRST (for caching)
# -----------------------------
COPY requirements.txt .

# -----------------------------
# 5. INSTALL PYTHON DEPENDENCIES
# -----------------------------
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# -----------------------------
# 6. COPY PROJECT FILES
# -----------------------------
COPY . .

# -----------------------------
# 7. ENV VARIABLES
# -----------------------------
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# -----------------------------
# 8. EXPOSE PORT
# -----------------------------
EXPOSE 10000

# -----------------------------
# 9. START COMMAND (STREAMLIT)
# -----------------------------
CMD ["streamlit", "run", "frontend.py", "--server.port=10000", "--server.address=0.0.0.0"]
