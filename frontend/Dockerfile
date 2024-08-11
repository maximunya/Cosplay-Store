FROM node:12 AS build

WORKDIR /app
COPY package*.json ./

RUN npm install --force --legacy-peer-deps

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]