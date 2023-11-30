FROM node:20.2.0-alpine3.16

# Create app directory
WORKDIR /app/

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]

