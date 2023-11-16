# Backend for live demo of controller interface


# Generate certificate

1. First remove the ssl server from the config file


2. Run nginx container


3. Craete the certificate
```
docker compose run --rm certbot certonly --webroot --webroot-path=/var/www/html -d api.demo.ribot.dev

```

4. Add the ssl server back to the config file

5. 

```
docker compose up --build
```
