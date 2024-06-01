FROM golang:1.22.2-alpine3.19
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

FROM alpine:3.19
ENV IN_CONTAINER=true
RUN apk --no-cache add ca-certificates
RUN apk add --no-cache tzdata
WORKDIR /root/
COPY --from=0 /go/main .
EXPOSE 5057
CMD ["./main"]

