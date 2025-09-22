# --- Build stage ---
FROM node:20-alpine AS build

WORKDIR /app
# If you have a lockfile, copy it too (package-lock.json or pnpm-lock.yaml etc.)
COPY package.json ./
# If you have a lockfile, uncomment the right line:
# COPY package-lock.json ./
# COPY pnpm-lock.yaml ./
# COPY yarn.lock ./

# Install deps
RUN npm ci || npm install

# Copy source and build
COPY . .
# Tailwind/Vite build
RUN npm run build

# --- Runtime stage ---
FROM nginx:alpine

# Nginx config (added in step 2 below)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static assets
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
