FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine
ARG VERSION=dev
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="penroselamarck-web"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.revision="${VCS_REF}"

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.proxy.conf /etc/nginx/penroselamarck/nginx.proxy.conf
COPY nginx.standalone.conf /etc/nginx/penroselamarck/nginx.standalone.conf
COPY docker-entrypoint/40-web-mode.sh /docker-entrypoint.d/40-web-mode.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
