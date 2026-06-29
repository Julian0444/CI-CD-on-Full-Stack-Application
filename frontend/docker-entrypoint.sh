#!/bin/sh
set -eu

# --- 1) Inyectar la URL del backend en runtime (12-factor) ---
: "${VITE_API_URL:=http://localhost:8080}"
: "${REACT_APP_API_URL:=${VITE_API_URL}}"

cat <<EOC > /usr/share/nginx/html/env-config.js
window.__ENV__ = window.__ENV__ || {};
window.__ENV__.VITE_API_URL = "${VITE_API_URL}";
window.__ENV__.REACT_APP_API_URL = "${REACT_APP_API_URL}";
EOC

# --- 2) Generar el server de Nginx escuchando en $PORT (Render lo inyecta) ---
: "${PORT:=80}"

cat <<EOC > /etc/nginx/conf.d/default.conf
server {
    listen       ${PORT};
    server_name  _;
    root         /usr/share/nginx/html;
    index        index.html;

    # SPA: cualquier ruta desconocida cae en index.html (React Router)
    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOC

exec nginx -g "daemon off;"
