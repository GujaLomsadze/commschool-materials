# How to RUN ProvectusLabs - KAFKA UI

```shell
wget https://github.com/provectus/kafka-ui/releases/download/v0.7.2/kafka-ui-api-v0.7.2.jar
```

```shell
sudo nano application.yaml
```

```shell
clusters:
- name: local
  bootstrapServers: localhost:9092

server:
  port: 8080
```


```shell
java -jar kafka-ui-api-v0.7.2.jar --spring.config.additional-location=application.yml
```