```bash
cd /opt
sudo curl -L -o spark.tgz https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz
sudo tar -xzf spark.tgz
sudo ln -s spark-3.5.1-bin-hadoop3 spark


echo 'export SPARK_HOME=/opt/spark' >> ~/.zshrc
echo 'export PATH=$SPARK_HOME/bin:$PATH' >> ~/.zshrc
source ~/.zshrc


spark-submit --version



spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  stream_raw.py

```