FROM node:20

# Create app directory
WORKDIR /app/

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]

