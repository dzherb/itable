FROM node:23.3-alpine AS build
WORKDIR /app
COPY package.json package.json
RUN yarn install
COPY . .
RUN yarn build

FROM alpine
COPY --from=build /app/dist/client /tmp_static

CMD mv /tmp_static/* /static && rm -rf /tmp_static