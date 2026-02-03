#!/bin/bash
# Set variables

NODE1="clickhouse01"
NODE2="clickhouse02"

ZK1="x.x.x.x"
ZK2="x.x.x.x"

CLICKHOUSE_REPO="https://packages.clickhouse.com/deb"

ARCH=$(dpkg --print-architecture)
# Set hostname based on local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
if [[ "$LOCAL_IP" == "$ZK1" ]]; then
    sudo hostnamectl set-hostname "$NODE1"
elif [[ "$LOCAL_IP" == "$ZK2" ]]; then
    sudo hostnamectl set-hostname "$NODE2"
else
    echo "⚠️ Warning: IP $LOCAL_IP does not match known node IPs. Hostname will not be changed."
fi

# Update and install dependencies
sudo apt update
sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl gnupg zookeeperd default-jre
# Add the ClickHouse GPG key
curl -fsSL https://packages.clickhouse.com/rpm/lts/repodata/repomd.xml.key | sudo gpg --dearmor -o /usr/share/keyrings/clickhouse-keyring.gpg
# Add the ClickHouse repository
echo "deb [signed-by=/usr/share/keyrings/clickhouse-keyring.gpg] $CLICKHOUSE_REPO stable main" | sudo tee /etc/apt/sources.list.d/clickhouse.list
# Update apt package lists
sudo apt update
# Install ClickHouse server and client
sudo apt install -y clickhouse-server clickhouse-client
# Create config directories
sudo mkdir -p /etc/clickhouse-server/config.d
sudo mkdir -p /etc/clickhouse-server/users.d
# Update /etc/hosts
echo -e "$ZK1 $NODE1\n$ZK2 $NODE2" | sudo tee -a /etc/hosts
# Configure ZooKeeper myid
if [[ $(hostname) == "$NODE1" ]]; then
    echo "1" | sudo tee /etc/zookeeper/conf/myid
elif [[ $(hostname) == "$NODE2" ]]; then
    echo "2" | sudo tee /etc/zookeeper/conf/myid
fi
# Configure ZooKeeper config
cat <<EOF | sudo tee /etc/zookeeper/conf/zoo.cfg > /dev/null
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/var/lib/zookeeper
clientPort=2181
server.1=$NODE1:2888:3888
server.2=$NODE2:2888:3888
EOF
# Restart and enable ZooKeeper
sudo systemctl restart zookeeper
sudo systemctl enable zookeeper
# Set ClickHouse macros
if [[ $(hostname) == "$NODE1" ]]; then
    echo "<yandex><macros><replica>clickhouse01</replica><shard>1</shard></macros></yandex>" | sudo tee /etc/clickhouse-server/config.d/macros.xml
elif [[ $(hostname) == "$NODE2" ]]; then
    echo "<yandex><macros><replica>clickhouse02</replica><shard>1</shard></macros></yandex>" | sudo tee /etc/clickhouse-server/config.d/macros.xml
fi
# Set remote servers config
cat <<EOF | sudo tee /etc/clickhouse-server/config.d/remote_servers.xml > /dev/null
<yandex>
    <remote_servers>
        <clickhouse_cluster>
            <shard>
                <replica>
                    <host>$NODE1</host>
                    <port>9000</port>
                </replica>
                <replica>
                    <host>$NODE2</host>
                    <port>9000</port>
                </replica>
            </shard>
        </clickhouse_cluster>
    </remote_servers>
</yandex>
EOF
# Modify config.xml: listen_host and zookeeper
CONFIG_FILE="/etc/clickhouse-server/config.xml"
# Backup the original config
sudo cp $CONFIG_FILE "${CONFIG_FILE}.bak"
# Uncomment <listen_host>0.0.0.0</listen_host> or add if not present
sudo sed -i 's/<!--\s*<listen_host>0.0.0.0<\/listen_host>\s*-->/<listen_host>0.0.0.0<\/listen_host>/g' $CONFIG_FILE
if ! grep -q "<listen_host>0.0.0.0</listen_host>" $CONFIG_FILE; then
    sudo sed -i '/<listen_host>/i \ \ \ \ <listen_host>0.0.0.0</listen_host>' $CONFIG_FILE
fi
# Uncomment and configure ZooKeeper section
sudo sed -i '/<!-- <zookeeper>/,/<\/zookeeper> -->/{
    s/<!--//g
    s/-->//g
}' $CONFIG_FILE
# Replace or add ZooKeeper nodes
sudo tee /etc/clickhouse-server/config.d/zookeeper.xml > /dev/null <<EOF
<yandex>
    <zookeeper>
        <node>
            <host>$ZK1</host>
            <port>2181</port>
        </node>
        <node>
            <host>$ZK2</host>
            <port>2181</port>
        </node>
    </zookeeper>
</yandex>
EOF
# Configure firewall
if command -v ufw &> /dev/null; then
    sudo ufw allow 9000/tcp
    sudo ufw allow 8123/tcp
fi
# Restart and enable ClickHouse server
sudo systemctl restart clickhouse-server
sudo systemctl enable clickhouse-server
# Startup
sudo systemctl start zookeeper
sudo systemctl start clickhouse-server
# Completion message
echo "✅ Cluster setup complete! ClickHouse and ZooKeeper are running."
