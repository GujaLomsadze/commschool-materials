#!/bin/bash
#
# Bootstrap script for a 2-node ClickHouse cluster with ZooKeeper
#
# - Installs ClickHouse Server & Client
# - Installs and configures ZooKeeper
# - Sets hostnames based on IP
# - Configures ClickHouse replication macros
# - Configures remote_servers cluster
# - Enables network access & services
#

# ================================
# Cluster variables
# ================================
NODE1="clickhouse01"
NODE2="clickhouse02"

ZK1="x.x.x.x"
ZK2="x.x.x.x"

CLICKHOUSE_REPO="https://packages.clickhouse.com/deb"
ARCH=$(dpkg --print-architecture)

# ================================
# Detect local IP and set hostname
# ================================
LOCAL_IP=$(hostname -I | awk '{print $1}')

if [[ "$LOCAL_IP" == "$ZK1" ]]; then
    sudo hostnamectl set-hostname "$NODE1"
elif [[ "$LOCAL_IP" == "$ZK2" ]]; then
    sudo hostnamectl set-hostname "$NODE2"
else
    echo "⚠️ Warning: IP $LOCAL_IP does not match known node IPs."
    echo "Hostname will not be changed."
fi

# ================================
# System update & base dependencies
# ================================
sudo apt update
sudo apt upgrade -y

# ZooKeeper + Java are required for ClickHouse replication
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    zookeeperd \
    default-jre

# ================================
# ClickHouse repository setup
# ================================
curl -fsSL https://packages.clickhouse.com/rpm/lts/repodata/repomd.xml.key \
    | sudo gpg --dearmor -o /usr/share/keyrings/clickhouse-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/clickhouse-keyring.gpg] \
$CLICKHOUSE_REPO stable main" \
| sudo tee /etc/apt/sources.list.d/clickhouse.list

sudo apt update

# ================================
# Install ClickHouse
# ================================
sudo apt install -y clickhouse-server clickhouse-client

# ================================
# Ensure config include directories exist
# ================================
sudo mkdir -p /etc/clickhouse-server/config.d
sudo mkdir -p /etc/clickhouse-server/users.d

# ================================
# /etc/hosts for cluster resolution
# ================================
echo -e "$ZK1 $NODE1\n$ZK2 $NODE2" | sudo tee -a /etc/hosts

# ================================
# ZooKeeper myid (required for quorum)
# ================================
if [[ $(hostname) == "$NODE1" ]]; then
    echo "1" | sudo tee /etc/zookeeper/conf/myid
elif [[ $(hostname) == "$NODE2" ]]; then
    echo "2" | sudo tee /etc/zookeeper/conf/myid
fi

# ================================
# ZooKeeper configuration
# ================================
cat <<EOF | sudo tee /etc/zookeeper/conf/zoo.cfg > /dev/null
tickTime=2000
initLimit=10
syncLimit=5
dataDir=/var/lib/zookeeper
clientPort=2181
server.1=$NODE1:2888:3888
server.2=$NODE2:2888:3888
EOF

sudo systemctl restart zookeeper
sudo systemctl enable zookeeper

# ================================
# ClickHouse macros (replication)
# ================================
#
# These macros are used by ReplicatedMergeTree
#
if [[ $(hostname) == "$NODE1" ]]; then
    cat <<EOF | sudo tee /etc/clickhouse-server/config.d/macros.xml
<yandex>
    <macros>
        <replica>clickhouse01</replica>
        <shard>1</shard>
    </macros>
</yandex>
EOF
elif [[ $(hostname) == "$NODE2" ]]; then
    cat <<EOF | sudo tee /etc/clickhouse-server/config.d/macros.xml
<yandex>
    <macros>
        <replica>clickhouse02</replica>
        <shard>1</shard>
    </macros>
</yandex>
EOF
fi

# ================================
# ClickHouse remote_servers cluster
# ================================
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

# ================================
# Base ClickHouse config tweaks
# ================================
CONFIG_FILE="/etc/clickhouse-server/config.xml"
sudo cp $CONFIG_FILE "${CONFIG_FILE}.bak"

# Allow network access
sudo sed -i \
    's/<!--\s*<listen_host>0.0.0.0<\/listen_host>\s*-->/<listen_host>0.0.0.0<\/listen_host>/g' \
    $CONFIG_FILE

if ! grep -q "<listen_host>0.0.0.0</listen_host>" $CONFIG_FILE; then
    sudo sed -i '/<listen_host>/i \ \ \ \ <listen_host>0.0.0.0</listen_host>' \
        $CONFIG_FILE
fi

# ================================
# ZooKeeper config for ClickHouse
# ================================
cat <<EOF | sudo tee /etc/clickhouse-server/config.d/zookeeper.xml > /dev/null
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

# ================================
# Firewall (if UFW is enabled)
# ================================
if command -v ufw &> /dev/null; then
    sudo ufw allow 9000/tcp   # Native ClickHouse
    sudo ufw allow 8123/tcp   # HTTP interface
fi

# ================================
# Start and enable services
# ================================
sudo systemctl restart clickhouse-server
sudo systemctl enable clickhouse-server

sudo systemctl start zookeeper
sudo systemctl start clickhouse-server

# ================================
# Done
# ================================
echo "✅ Cluster setup complete!"
echo "ClickHouse and ZooKeeper are running."
