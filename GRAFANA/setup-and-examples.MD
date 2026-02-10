```
sudo apt-get update
sudo apt-get install -y software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/grafana.gpg
echo "deb [signed-by=/usr/share/keyrings/grafana.gpg] https://packages.grafana.com/oss/deb stable main" \
| sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install grafana
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
sudo systemctl status grafana-server
```

```
SELECT
  $__timeGroup(created_at, '5m') AS time,
  SUM(total_amount) AS revenue
FROM public.ecommerce_transactions
WHERE $__timeFilter(created_at)
GROUP BY 1
ORDER BY 1;

```
