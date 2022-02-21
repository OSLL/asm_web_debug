FROM nginx:latest

COPY ./docker/nginx.conf /etc/nginx/nginx.conf
COPY ./app/static /static
