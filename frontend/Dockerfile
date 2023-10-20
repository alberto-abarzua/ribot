FROM node:20-alpine3.18

WORKDIR /app

COPY package*.json ./

RUN npm install --loglevel verbose

COPY . .

RUN npm run build

EXPOSE 3000



CMD ["npm","run","dev"]
