# Apache NiFi 2.7.2 – Single Node Setup on Ubuntu (Local)

---

## 1. Download Apache NiFi 2.7.2

```bash
cd /opt
sudo wget https://dlcdn.apache.org/nifi/2.7.2/nifi-2.7.2-bin.zip
```

Extract the archive:

```bash
sudo unzip nifi-2.7.2-bin.zip
sudo mv nifi-2.7.2 nifi
```

Fix permissions:

```bash
sudo chown -R $USER:$USER /opt/nifi
```

---

## 2. Basic Configuration (Single Node, HTTP)

Edit the main configuration file:

```bash
nano /opt/nifi/conf/nifi.properties
```

### Enable HTTP (recommended for local development)

Set:

```properties
nifi.web.http.host=0.0.0.0
nifi.web.http.port=8080
```

Ensure HTTPS is disabled:

```properties
nifi.web.https.port=

nifi.remote.input.host=
nifi.remote.input.secure=false
nifi.remote.input.socket.port=
nifi.remote.input.http.enabled=true
nifi.remote.input.http.transaction.ttl=30 sec
nifi.remote.contents.cache.expiration=30 secs
```



---

## SET JAVA HOME

```
readlink -f /usr/bin/java
```

```
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
```

## 3. Start Apache NiFi

```bash
cd /opt/nifi
sudo bin/nifi.sh start
```

Check status:

```bash
sudo bin/nifi.sh status
```

View logs:

```bash
tail -f logs/nifi-app.log
```

---

## 5. Access NiFi UI

Open a browser and navigate to:

```
http://localhost:8080/nifi
```

---

## 6. Stop / Restart NiFi

```bash
bin/nifi.sh stop
bin/nifi.sh restart
```

---

## 7. Useful Directories

| Purpose | Path |
|------|------|
| Config | `/opt/nifi/conf` |
| Logs | `/opt/nifi/logs` |
| FlowFile Repos | `/opt/nifi/flowfile_repository` |
| Content Repo | `/opt/nifi/content_repository` |
| Provenance Repo | `/opt/nifi/provenance_repository` |
| State | `/opt/nifi/state` |

---

## 8. Needed for PG\
```
jdbc:postgresql://localhost:5432/mydb
cd /opt/nifi/lib
wget https://jdbc.postgresql.org/download/postgresql-42.7.4.jar
chmod 644 postgresql-42.7.4.jar
```

```
jdbc:postgresql://localhost:5432/postgres
org.postgresql.Driver
/opt/nifi/lib/postgresql-42.7.4.jar
```
