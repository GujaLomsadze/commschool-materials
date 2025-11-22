# Setting Up PostgreSQL Master-Slave (Primary-Replica) Replication - Manual Configuration

## Prerequisites

You have two fresh PostgreSQL instances:
- **Instance 1 (Master/Primary)**: Port 5432 at `/var/lib/postgresql/instance1`
- **Instance 2 (Slave/Replica)**: Port 5433 at `/var/lib/postgresql/instance2`

## Step 1: Configure the Master (Instance 1)

### Start the master instance
```bash
sudo systemctl start postgresql-instance1
```
or
```bash
sudo -u postgres /usr/lib/postgresql/*/bin/pg_ctl -D /var/lib/postgresql/instance1 -l /var/lib/postgresql/instance1/logfile start
```

### Create replication user
```bash
sudo -u postgres psql -p 5432 -c "CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replicator_password';"
```

### Edit postgresql.conf on master
```bash
sudo -u postgres nano /var/lib/postgresql/instance1/postgresql.conf
```

Find and modify these lines (uncomment if needed):
```conf
listen_addresses = 'localhost'          # Already set by default
port = 5432                              # Already set

# WAL settings
wal_level = replica                      # Change from 'replica' or 'minimal'
max_wal_senders = 3                      # Uncomment and set to 3
max_replication_slots = 3                # Uncomment and set to 3
wal_keep_size = 64MB                     # For PG 13+, or use wal_keep_segments = 64 for older
hot_standby = on                         # Uncomment
```

Save and exit (Ctrl+X, then Y, then Enter).

### Edit pg_hba.conf on master
```bash
sudo -u postgres nano /var/lib/postgresql/instance1/pg_hba.conf
```

Add at the end of the file:
```conf
# Replication connections
host    replication     replicator      127.0.0.1/32            md5
host    replication     replicator      ::1/128                 md5
```

Save and exit.

### Restart master to apply changes
```bash
sudo systemctl restart postgresql-instance1
```

### Create replication slot
```bash
sudo -u postgres psql -p 5432 -c "SELECT * FROM pg_create_physical_replication_slot('replica_1_slot');"
```

Verify:
```bash
sudo -u postgres psql -p 5432 -c "SELECT * FROM pg_replication_slots;"
```

## Step 2: Prepare the Replica (Instance 2)

### Stop instance 2
```bash
sudo systemctl stop postgresql-instance2
```

### Remove existing data in instance2
```bash
sudo rm -rf /var/lib/postgresql/instance2/*
```

### Create .pgpass file for authentication
```bash
sudo -u postgres bash -c "echo 'localhost:5432:replication:replicator:replicator_password' > /var/lib/postgresql/.pgpass"
sudo -u postgres chmod 600 /var/lib/postgresql/.pgpass
```

### Clone master data to replica using pg_basebackup
```bash
sudo -u postgres pg_basebackup -h localhost -p 5432 -U replicator -D /var/lib/postgresql/instance2 -Fp -Xs -P -R
```

Wait for the backup to complete. You should see progress output.

### Modify port in replica's postgresql.conf
```bash
sudo -u postgres nano /var/lib/postgresql/instance2/postgresql.conf
```

Find the line:
```conf
port = 5432
```

Change it to:
```conf
port = 5433
```

Save and exit.

## Step 3: Configure Replica Settings

### Verify standby.signal file exists
```bash
ls -la /var/lib/postgresql/instance2/standby.signal
```

This file should have been created by `pg_basebackup -R`. If it doesn't exist:
```bash
sudo -u postgres touch /var/lib/postgresql/instance2/standby.signal
```

### Check postgresql.auto.conf
```bash
cat /var/lib/postgresql/instance2/postgresql.auto.conf
```

You should see replication configuration. If the file is empty or missing, create it:
```bash
sudo -u postgres nano /var/lib/postgresql/instance2/postgresql.auto.conf
```

Add:
```conf
primary_conninfo = 'host=localhost port=5432 user=replicator password=replicator_password application_name=replica1'
primary_slot_name = 'replica_1_slot'
```

Save and exit.

## Step 4: Start the Replica
```bash
sudo systemctl start postgresql-instance2
```

### Check if replica started successfully
```bash
sudo systemctl status postgresql-instance2
```

## Step 5: Verify Replication is Working

### On Master - Check replication connections
```bash
sudo -u postgres psql -p 5432 -c "SELECT * FROM pg_stat_replication;"
```

Expected output should show one row with:
- `application_name`: replica1
- `state`: streaming
- `client_addr`: 127.0.0.1

### On Master - Check replication slots
```bash
sudo -u postgres psql -p 5432 -c "SELECT * FROM pg_replication_slots;"
```

You should see `replica_1_slot` with `active = t`.

### On Replica - Check if in recovery mode
```bash
sudo -u postgres psql -p 5433 -c "SELECT pg_is_in_recovery();"
```

Expected output: `t` (true) - meaning it's a replica.

### On Replica - Check WAL receiver status
```bash
sudo -u postgres psql -p 5433 -c "SELECT * FROM pg_stat_wal_receiver;"
```

You should see status information about the WAL receiver.

### Check replication lag
```bash
sudo -u postgres psql -p 5432 -c "SELECT application_name, state, sync_state, 
       pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes,
       replay_lag
FROM pg_stat_replication;"
```

## Step 6: Test Replication

### On Master - Create test database and table
```bash
sudo -u postgres psql -p 5432
```

Run these SQL commands:
```sql
CREATE DATABASE testdb;
\c testdb
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO employees (name, department) VALUES 
    ('Alice Johnson', 'Engineering'),
    ('Bob Smith', 'Sales'),
    ('Carol White', 'Marketing');

SELECT * FROM employees;
\q
```

### On Replica - Verify data was replicated
```bash
sudo -u postgres psql -p 5433
```

Run these SQL commands:
```sql
\c testdb
SELECT * FROM employees;
```

You should see the same 3 rows!

### Test that replica is read-only

Still in the replica psql session:
```sql
INSERT INTO employees (name, department) VALUES ('Dave Brown', 'HR');
```

Expected error:
```
ERROR:  cannot execute INSERT in a read-only transaction
```
```sql
\q
```

### Test continuous replication

Open two terminals side by side:

**Terminal 1 (Master):**
```bash
sudo -u postgres psql -p 5432 testdb
```

**Terminal 2 (Replica):**
```bash
sudo -u postgres psql -p 5433 testdb
```

In Terminal 1 (Master), insert data:
```sql
INSERT INTO employees (name, department) VALUES ('Eve Davis', 'Finance');
```

In Terminal 2 (Replica), immediately query:
```sql
SELECT * FROM employees ORDER BY id;
```

You should see the new row almost instantly!

## Step 7: Create Monitoring Commands

### Check replication status (save as script)
```bash
sudo tee /usr/local/bin/check-replication > /dev/null <<'EOF'
#!/bin/bash

echo "======================================"
echo "MASTER STATUS (Port 5432)"
echo "======================================"
sudo -u postgres psql -p 5432 -x -c "SELECT 
    application_name,
    client_addr,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) as send_lag_bytes,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) as replay_lag_bytes,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;"

echo ""
echo "======================================"
echo "REPLICA STATUS (Port 5433)"
echo "======================================"
sudo -u postgres psql -p 5433 -c "SELECT pg_is_in_recovery() as is_replica;"

echo ""
sudo -u postgres psql -p 5433 -x -c "SELECT 
    status,
    received_lsn,
    received_tli,
    last_msg_send_time,
    last_msg_receipt_time
FROM pg_stat_wal_receiver;"

echo ""
echo "======================================"
echo "REPLICATION SLOTS"
echo "======================================"
sudo -u postgres psql -p 5432 -c "SELECT 
    slot_name,
    slot_type,
    active,
    restart_lsn,
    confirmed_flush_lsn
FROM pg_replication_slots;"
EOF

sudo chmod +x /usr/local/bin/check-replication
```

### Run the monitoring script
```bash
check-replication
```

## Configuration Summary

### Master Configuration Files

**postgresql.conf** (`/var/lib/postgresql/instance1/postgresql.conf`):
- `wal_level = replica`
- `max_wal_senders = 3`
- `max_replication_slots = 3`
- `wal_keep_size = 64MB`
- `hot_standby = on`

**pg_hba.conf** (`/var/lib/postgresql/instance1/pg_hba.conf`):
- Added replication access for `replicator` user

### Replica Configuration Files

**postgresql.conf** (`/var/lib/postgresql/instance2/postgresql.conf`):
- `port = 5433` (changed from 5432)

**postgresql.auto.conf** (`/var/lib/postgresql/instance2/postgresql.auto.conf`):
- `primary_conninfo = 'host=localhost port=5432 user=replicator password=replicator_password application_name=replica1'`
- `primary_slot_name = 'replica_1_slot'`

**standby.signal** (`/var/lib/postgresql/instance2/standby.signal`):
- Empty file that signals this is a standby server

## Managing the Cluster

### Start both instances
```bash
sudo systemctl start postgresql-instance1
sudo systemctl start postgresql-instance2
```

### Stop both instances
```bash
sudo systemctl stop postgresql-instance2
sudo systemctl stop postgresql-instance1
```

Note: Stop replica first, then master.

### Restart both instances
```bash
sudo systemctl restart postgresql-instance1
sudo systemctl restart postgresql-instance2
```

### Check status
```bash
sudo systemctl status postgresql-instance1
sudo systemctl status postgresql-instance2
```

## Troubleshooting

### Replica not connecting to master

Check master logs:
```bash
tail -f /var/lib/postgresql/instance1/logfile
```

Check replica logs:
```bash
tail -f /var/lib/postgresql/instance2/logfile
```

### Authentication issues

Verify .pgpass file:
```bash
cat /var/lib/postgresql/.pgpass
```

Test connection manually:
```bash
sudo -u postgres psql "host=localhost port=5432 user=replicator dbname=replication"
```

### Replication lag increasing

Check master load:
```bash
sudo -u postgres psql -p 5432 -c "SELECT * FROM pg_stat_activity;"
```

Check disk I/O and available space:
```bash
df -h
iostat -x 1
```

### Reset replica (if needed)
```bash
# Stop replica
sudo systemctl stop postgresql-instance2

# Clear data
sudo rm -rf /var/lib/postgresql/instance2/*

# Re-clone from master
sudo -u postgres pg_basebackup -h localhost -p 5432 -U replicator -D /var/lib/postgresql/instance2 -Fp -Xs -P -R

# Change port
sudo -u postgres sed -i 's/port = 5432/port = 5433/' /var/lib/postgresql/instance2/postgresql.conf

# Start replica
sudo systemctl start postgresql-instance2
```

## Promoting Replica to Master (Manual Failover)

If master fails, promote replica:
```bash
# Stop master (if running)
sudo systemctl stop postgresql-instance1

# Promote replica
sudo -u postgres /usr/lib/postgresql/*/bin/pg_ctl promote -D /var/lib/postgresql/instance2

# Or using SQL
sudo -u postgres psql -p 5433 -c "SELECT pg_promote();"
```

Check promotion status:
```bash
sudo -u postgres psql -p 5433 -c "SELECT pg_is_in_recovery();"
```

Should return `f` (false) - it's now a master.

## Summary

Your PostgreSQL streaming replication is now configured:

- **Master (Instance 1)**: Port 5432 - Read/Write
- **Replica (Instance 2)**: Port 5433 - Read-Only
- **Replication Type**: Streaming replication with physical replication slot
- **Synchronization**: Asynchronous (near real-time)
- **Use Cases**: 
  - Load balancing (read queries on replica)
  - High availability (promote replica if master fails)
  - Backup (take backups from replica without impacting master)

All write operations go to master, and changes are automatically streamed to replica!