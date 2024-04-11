FROM python:3.10-bullseye
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
#RUN pip install --upgrade pip
CMD ["gunicorn" , "sales_proj.wsgi","--bind", "0.0.0.0:80"]
EXPOSE 80