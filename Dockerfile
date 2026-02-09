# Use a lightweight Python base image
FROM python:3.11-slim

# Set environment variables
# PYTHONUNBUFFERED=1 ensures you see the output logs instantly in the terminal
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the script into the container
COPY RedEye.py .

# Make sure the script is executable (optional but good practice)
RUN chmod +x RedEye.py

# The command to run when the container starts
CMD ["python3", "RedEye.py"]