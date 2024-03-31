FROM node:12

WORKDIR /app
COPY package*.json ./

RUN npm install --force --legacy-peer-deps

COPY . .

RUN npm run build

CMD npm start