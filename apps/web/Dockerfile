# Build the WenQuest web app, then serve it with Caddy; /api is forwarded to the gateway.
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build:h5

# 白板课编辑器 (round 35): React + Excalidraw, served at /wb-editor/
FROM node:22-alpine AS wbeditor
WORKDIR /ed
COPY wb-editor/package.json wb-editor/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY wb-editor/ ./
RUN node build.mjs

FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist/build/h5 /srv/app
COPY --from=wbeditor /ed/dist /srv/app/wb-editor
EXPOSE 80
