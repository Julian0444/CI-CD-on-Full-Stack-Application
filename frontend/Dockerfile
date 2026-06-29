# syntax=docker/dockerfile:1

# Etapa de build
FROM node:20-alpine AS builder
WORKDIR /app

# La URL del backend se inyecta en runtime (ver docker-entrypoint.sh),
# no en build-time, para que la misma imagen sirva en QA y Prod.
ARG VITE_API_URL=http://localhost:8080
ENV VITE_API_URL=${VITE_API_URL}

COPY package.json ./
COPY package-lock.json ./
RUN npm ci --omit=dev

# Copiar el resto del código y construir la app
COPY . .
RUN npm run build

# Etapa de runtime (Nginx)
FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html
COPY --from=builder /app/build/ ./
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Render (y otros PaaS) inyectan el puerto vía $PORT; por defecto 80 en local.
ENV PORT=80
EXPOSE 80

# Comando de inicio (inyecta la URL del backend en env-config y arranca Nginx en $PORT)
ENTRYPOINT ["/entrypoint.sh"]
