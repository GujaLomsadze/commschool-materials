
```bash
sudo mkdir -p /etc/redis/sentinel
```

```bash
sudo nano /etc/redis/sentinel/sentinel-26379.conf
```
```
port 26379
bind 127.0.0.1 ::1
protected-mode yes

dir /var/lib/redis/sentinel-26379
logfile /var/log/redis/sentinel-26379.log
pidfile /run/redis/sentinel-26379.pid

# --- MONITOR THE MASTER ---
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1
```


```bash
sudo cp /etc/redis/sentinel/sentinel-26379.conf /etc/redis/sentinel/sentinel-26380.conf
sudo cp /etc/redis/sentinel/sentinel-26379.conf /etc/redis/sentinel/sentinel-26381.conf

```

```bash
sudo nano /etc/redis/sentinel/sentinel-26380.conf
```

```
port 26380
dir /var/lib/redis/sentinel-26380
logfile /var/log/redis/sentinel-26380.log
pidfile /run/redis/sentinel-26380.pid
```

```bash
sudo mkdir -p /var/lib/redis/sentinel-26379 /var/lib/redis/sentinel-26380 /var/lib/redis/sentinel-26381
sudo chown -R redis:redis /var/lib/redis/sentinel-26379 /var/lib/redis/sentinel-26380 /var/lib/redis/sentinel-26381
```



```bash
sudo -u redis redis-sentinel /etc/redis/sentinel/sentinel-26379.conf
sudo -u redis redis-sentinel /etc/redis/sentinel/sentinel-26380.conf
sudo -u redis redis-sentinel /etc/redis/sentinel/sentinel-26381.conf
```


```bash
redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
```



# In case permissions dont work

```
sudo chown redis:redis /etc/redis/sentinel/*.conf
sudo chmod 640 /etc/redis/sentinel/*.conf

sudo chown -R redis:redis /etc/redis/sentinel

```
