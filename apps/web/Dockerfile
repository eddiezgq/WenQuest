# Build the WenQuest web app, then serve it with Caddy; /api is forwarded to the gateway.
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build:h5

FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist/build/h5 /srv/app
EXPOSE 80
