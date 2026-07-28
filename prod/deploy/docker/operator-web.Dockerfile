# operator-web image (ASC-007): nginx serving the v0.1.0 HTML MVP + runtime config.js.
# Build context = repo root:
#   docker build -f deploy/docker/operator-web.Dockerfile -t operator-web:dev .
FROM nginx:1.27-alpine

RUN apk add --no-cache gettext  # provides envsubst

COPY services/operator-web/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY services/operator-web/web/config.js.template /usr/share/nginx/html/config.js.template
COPY services/operator-web/web/docker-entrypoint.sh /docker-entrypoint.d/40-asc-config.sh
# Live console is the default UI (ASC-043); it calls control-api via same-origin /api.
COPY services/operator-web/web/console/ /usr/share/nginx/html/
# The v0.1.0 clickable MVP is kept at /mvp as the design/interaction reference.
COPY app/agent_simulation_control_plane_mvp.html /usr/share/nginx/html/mvp/index.html

RUN chmod +x /docker-entrypoint.d/40-asc-config.sh
EXPOSE 8080
