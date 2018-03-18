FROM python:3.6.3
ADD src /src
ADD res /res
ADD requirements.txt /
RUN pip install -r requirements.txt
CMD ["python", "./src/main.py"]