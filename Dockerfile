# ---------- Base Image ----------
FROM python:3.13-slim

# ---------- System Dependencies (Required for Chromium + Playwright Chromium) ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates fonts-liberation \
    libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libgtk-3-0 libgbm1 libnss3 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libxrender1 libpangocairo-1.0-0 \
    libpango-1.0-0 libatspi2.0-0 libxshmfence1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ---------- Create Working Directory ----------
WORKDIR /app

# ---------- Install Python Dependencies ----------
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ---------- Install Playwright + Chromium ----------
RUN pip install playwright
RUN playwright install --with-deps chromium

# ---------- Copy Application Code ----------
COPY . .

# ---------- Expose Port ----------
EXPOSE 8000

# ---------- Start FastAPI (Uvicorn) ----------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
