# Use a lightweight base image
FROM python:3.12-slim

WORKDIR /app

# Copy all code first (needed for setup.py)
COPY . .

# Install requirements and local package
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir .

# Set port for Cloud Run
ENV PORT=8080
EXPOSE 8080

# Start Streamlit
CMD ["bash", "-lc", "streamlit run app/streamlit_app.py --server.port $PORT --server.address 0.0.0.0"]

