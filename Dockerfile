FROM alpine:3.6

RUN apk --no-cache add py-pip ca-certificates gcc \
        python2-dev musl-dev libffi-dev openssl-dev make && \
    pip install ara

CMD [ "ara-manage", "runserver" ]
