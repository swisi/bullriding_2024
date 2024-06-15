FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Run the application
#CMD ["sh", "-c", "mkdir -p /app/database && flask db upgrade && flask run --host=0.0.0.0"]
CMD ["sh", "-c", "flask run --host=0.0.0.0"]
