FROM node:17
RUN apt-get update -y

WORKDIR /usr/src/app
COPY build_and_run.sh build_and_run.sh
EXPOSE 3000
CMD bash ./build_and_run.sh
