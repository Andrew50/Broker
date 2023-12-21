# Build stage
# FROM node:18 AS build
# WORKDIR /app
# COPY package*.json ./
# RUN npm install
# COPY . .
# RUN npm run build

# # Production stage
# FROM node:18
# WORKDIR /app
# COPY --from=build /app/build . 
# COPY package.json .  
# EXPOSE 3000
# CMD ["node", "index.js"]


FROM node:18
WORKDIR /app
# COPY package*.json ./
COPY . .
RUN npm install
RUN npm run build
EXPOSE 3000
CMD ["node", "build/index.js"]


