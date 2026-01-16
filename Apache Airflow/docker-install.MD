# Install Docker + Docker Compose on Ubuntu (WSL)

## 1) Update system

```
sudo apt update -y
sudo apt upgrade -y
```

## 2) Install prerequisites

```
sudo apt install -y ca-certificates curl gnupg lsb-release
```

## 3) Add Docker GPG key

```
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

```
## 4) Add Docker repository
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```
## 5) Install Docker Engine + Docker Compose
sudo apt update -y
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```
## 6) Start Docker service
sudo service docker start
```

## 7) Allow running docker without sudo

```
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

## 8) Test Docker

```
docker run hello-world
```

## 9) Test Docker Compose

```
docker compose version
```
