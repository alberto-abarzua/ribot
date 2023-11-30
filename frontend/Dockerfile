FROM node:20.2.0-alpine3.16

WORKDIR /app

COPY package.json .
COPY package-lock.json .

RUN npm install --verbose

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
