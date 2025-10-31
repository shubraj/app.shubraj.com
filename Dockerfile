# Dockerfile
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Disable numba JIT to avoid llvmlite/numba compile issues in constrained envs
ENV NUMBA_DISABLE_JIT=1
# Hint pymatting to avoid numba usage
ENV PYMATTING_NO_JIT=1

RUN apt-get update && apt-get install -y \
    libgl1 \
    libgomp1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /backend

# Install dependencies
COPY ./backend/requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django application
COPY ./backend /backend
RUN chmod -R 755 /backend/staticfiles 

# Collect static files
RUN python manage.py collectstatic --noinput

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "shubrajcom.wsgi:application", "--workers", "4"]
