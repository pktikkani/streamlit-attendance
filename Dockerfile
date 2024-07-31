FROM ubuntu:latest
LABEL authors="pavankumar"

ENTRYPOINT ["top", "-b"]