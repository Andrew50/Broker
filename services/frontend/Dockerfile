FROM node:latest
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
# For a Node.js server setup
CMD ["node", "path/to/server.js"]


# docker build -t sveltekit-app .
