# Kafka 3‑Broker Cluster (3 Nodes) + ZooKeeper (3 Nodes) on **WSL Ubuntu** (Local)

This guide sets up a **local** Kafka cluster with **3 Kafka brokers** and a **3‑node ZooKeeper quorum** on **one WSL Ubuntu instance** (single machine).  
It is intended for local development/testing.

> **Important:** In Kafka/ZooKeeper `.properties` files, **do not use** environment variables like `$USER`.  
> ZooKeeper and Kafka **do not expand** them. Use **absolute paths** (e.g., `/home/lomsadze/...`).

---

## 0) Prerequisites

```bash
sudo apt update
sudo apt install -y wget tar net-tools openjdk-17-jdk
java -version
```

---

## 1) Download Kafka (ZooKeeper mode)

```bash
cd ~
wget https://downloads.apache.org/kafka/3.9.1/kafka_2.13-3.9.1.tgz
tar -xzf kafka_2.13-3.9.1.tgz
mv kafka_2.13-3.9.1 kafka
```

---

## 2) Create local directories

> Replace `lomsadze` below with **your** Linux username if different.

```bash
mkdir -p /home/lomsadze/kafka-local/{zk1,zk2,zk3,broker1,broker2,broker3,conf}
```

---

## 3) Configure ZooKeeper (3 nodes)

### 3.1 Create `myid` files

```bash
echo "1" > /home/lomsadze/kafka-local/zk1/myid
echo "2" > /home/lomsadze/kafka-local/zk2/myid
echo "3" > /home/lomsadze/kafka-local/zk3/myid
```

Verify:

```bash
ls -l /home/lomsadze/kafka-local/zk{1,2,3}/myid
cat /home/lomsadze/kafka-local/zk1/myid
cat /home/lomsadze/kafka-local/zk2/myid
cat /home/lomsadze/kafka-local/zk3/myid
```

### 3.2 Create ZooKeeper config files

Create these three files:

**`/home/lomsadze/kafka-local/conf/zookeeper-1.properties`**
```properties
tickTime=2000
initLimit=5
syncLimit=2

dataDir=/home/lomsadze/kafka-local/zk1
clientPort=2181

server.1=127.0.0.1:2888:3888
server.2=127.0.0.1:2889:3889
server.3=127.0.0.1:2890:3890
```

**`/home/lomsadze/kafka-local/conf/zookeeper-2.properties`**
```properties
tickTime=2000
initLimit=5
syncLimit=2

dataDir=/home/lomsadze/kafka-local/zk2
clientPort=2182

server.1=127.0.0.1:2888:3888
server.2=127.0.0.1:2889:3889
server.3=127.0.0.1:2890:3890
```

**`/home/lomsadze/kafka-local/conf/zookeeper-3.properties`**
```properties
tickTime=2000
initLimit=5
syncLimit=2

dataDir=/home/lomsadze/kafka-local/zk3
clientPort=2183

server.1=127.0.0.1:2888:3888
server.2=127.0.0.1:2889:3889
server.3=127.0.0.1:2890:3890
```

### 3.3 Start ZooKeeper (3 terminals)

**Terminal A**
```bash
~/kafka/bin/zookeeper-server-start.sh /home/lomsadze/kafka-local/conf/zookeeper-1.properties
```

**Terminal B**
```bash
~/kafka/bin/zookeeper-server-start.sh /home/lomsadze/kafka-local/conf/zookeeper-2.properties
```

**Terminal C**
```bash
~/kafka/bin/zookeeper-server-start.sh /home/lomsadze/kafka-local/conf/zookeeper-3.properties
```

**Healthy quorum**: one shows `LEADING`, two show `FOLLOWING`.

Optional quick check:

```bash
echo stat | nc 127.0.0.1 2181 | grep Mode
echo stat | nc 127.0.0.1 2182 | grep Mode
echo stat | nc 127.0.0.1 2183 | grep Mode
```

---

## 4) Configure Kafka brokers (3 nodes)

Create these three files:

**`/home/lomsadze/kafka-local/conf/server-1.properties`**
```properties
broker.id=1
listeners=PLAINTEXT://127.0.0.1:9092
advertised.listeners=PLAINTEXT://127.0.0.1:9092

log.dirs=/home/lomsadze/kafka-local/broker1

num.partitions=3
min.insync.replicas=2

offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2

zookeeper.connect=127.0.0.1:2181,127.0.0.1:2182,127.0.0.1:2183
```

**`/home/lomsadze/kafka-local/conf/server-2.properties`**
```properties
broker.id=2
listeners=PLAINTEXT://127.0.0.1:9093
advertised.listeners=PLAINTEXT://127.0.0.1:9093

log.dirs=/home/lomsadze/kafka-local/broker2

num.partitions=3
min.insync.replicas=2

offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2

zookeeper.connect=127.0.0.1:2181,127.0.0.1:2182,127.0.0.1:2183
```

**`/home/lomsadze/kafka-local/conf/server-3.properties`**
```properties
broker.id=3
listeners=PLAINTEXT://127.0.0.1:9094
advertised.listeners=PLAINTEXT://127.0.0.1:9094

log.dirs=/home/lomsadze/kafka-local/broker3

num.partitions=3
min.insync.replicas=2

offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2

zookeeper.connect=127.0.0.1:2181,127.0.0.1:2182,127.0.0.1:2183
```

Ensure broker log dirs exist:

```bash
mkdir -p /home/lomsadze/kafka-local/broker{1,2,3}
ls -ld /home/lomsadze/kafka-local/broker*
```

---

## 5) Start Kafka brokers (3 terminals)

**Terminal D**
```bash
~/kafka/bin/kafka-server-start.sh /home/lomsadze/kafka-local/conf/server-1.properties
```

**Terminal E**
```bash
~/kafka/bin/kafka-server-start.sh /home/lomsadze/kafka-local/conf/server-2.properties
```

**Terminal F**
```bash
~/kafka/bin/kafka-server-start.sh /home/lomsadze/kafka-local/conf/server-3.properties
```

Success looks like:

- `... [KafkaServer id=X] started ...`
- No `AccessDeniedException`
- No “cannot create or validate log dirs” errors

---
