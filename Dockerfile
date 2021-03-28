FROM python:3.9
WORKDIR .
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
COPY startup.sh .
RUN bash deploy.sh
COPY . .
CMD ["python3", "-m", "DaisyX"]
