FROM python:3

WORKDIR /home/Documents

COPY . /home/Documents
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

CMD ["tail", "-f", "/dev/null"]