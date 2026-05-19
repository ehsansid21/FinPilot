FROM nginx:alpine

# Copy custom Nginx configuration for reverse-proxying
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy all static assets to Nginx default public directory
COPY . /usr/share/nginx/html

EXPOSE 80

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
