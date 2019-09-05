FROM quay.io/farrion/python3-ml:latest

LABEL maintainer="Mitesh Patel <mitpatel@redhat.com>"

COPY ./requirements.txt /requirements.txt
RUN pip3 install --upgrade pip

RUN pip3 install git+https://github.com/fabric8-analytics/fabric8-analytics-rudra#egg=rudra
RUN pip3 install -r requirements.txt

RUN pip3 install Cython==0.29.1 && pip3 install hpfrec==0.2.2.9

COPY ./entrypoint.sh /bin/entrypoint.sh
COPY ./src /src

RUN chmod +x /bin/entrypoint.sh

ENTRYPOINT ["/bin/entrypoint.sh"]
