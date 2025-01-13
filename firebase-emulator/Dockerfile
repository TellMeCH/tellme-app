FROM openjdk:11-jre-slim

RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g firebase-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /firebase

COPY firebase.json .

EXPOSE 9099 8085 9000 5001 4400 4500

CMD ["firebase", "emulators:start", "--project", "tellme-app-dev", "--only", "auth"]