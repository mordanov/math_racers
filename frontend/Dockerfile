FROM public.ecr.aws/docker/library/node:20-alpine AS builder

RUN npm install -g pnpm

WORKDIR /build/frontend
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY frontend/ ./
COPY assets/ /build/assets/
RUN pnpm build

FROM public.ecr.aws/docker/library/nginx:1.27-alpine AS runtime

RUN apk upgrade --no-cache

COPY --from=builder /build/frontend/dist /usr/share/nginx/html
COPY frontend/nginx.frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
