FROM nginx:alpine

# Set working directory
WORKDIR /usr/share/nginx/html

# Remove default NGINX content
RUN rm -rf ./*

# Copy frontend files
COPY . .

# Expose frontend port
EXPOSE 8080

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
