FROM python:3

WORKDIR /home/Documents

COPY . /home/Documents
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

WORKDIR /home/Documents/app

CMD ["tail", "-f", "/dev/null"]
