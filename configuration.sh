#!/bin/sh

if [ ! -d "/etc/nginx/ssl" ]; then
    mkdir /etc/nginx/ssl
    openssl req -newkey rsa:4096 -days 365 -nodes -x509 \
            -subj "/C=KR/ST=Seoul/L=Seoul/O=42Seoul/OU=Student/CN=junghych" \
            -keyout /etc/nginx/ssl/junghych.key \
            -out /etc/nginx/ssl/junghych.crt
    mkdir -p /run/nginx
fi

nginx -g "daemon off;"