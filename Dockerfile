FROM public.registry.u-hopper.com/python:3.8

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app/src

ENV FLASK_APP /app/src/dynap/main
ENV JOB_PATH /app/jars
ENV MONGODB_HOST "mongodb"
# CMD ["flask", "run",  "--host=0.0.0.0"]

ENV PYTHONPATH /app

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "dynap.main:flask_application"]
# CMD ["gunicorn", "-b", "0.0.0.0:5001", "dynap.main:flask_application"]

