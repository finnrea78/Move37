FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_MOVE37_API_BASE_URL=
ARG VITE_MOVE37_API_TOKEN=
ENV VITE_MOVE37_API_BASE_URL=${VITE_MOVE37_API_BASE_URL}
ENV VITE_MOVE37_API_TOKEN=${VITE_MOVE37_API_TOKEN}

COPY src/move37/web/package.json /app/src/move37/web/package.json
WORKDIR /app/src/move37/web
RUN npm install

COPY src/move37 /app/src/move37
RUN npm run build

FROM nginx:1.27-alpine
ARG VERSION=dev
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="move37-web"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.revision="${VCS_REF}"

COPY --from=builder /app/src/move37/web/dist /usr/share/nginx/html
COPY src/move37/web/nginx.proxy.conf /etc/nginx/move37/nginx.proxy.conf
COPY src/move37/web/nginx.standalone.conf /etc/nginx/move37/nginx.standalone.conf
COPY src/move37/web/docker-entrypoint/40-web-mode.sh /docker-entrypoint.d/40-web-mode.sh

RUN chmod +x /docker-entrypoint.d/40-web-mode.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
