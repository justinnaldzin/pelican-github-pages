Title: Deploying Debezium on Kubernetes locally via Minikube
Date: 2018-3-5
Tags: debezium, kubernetes, minikube, change data capture, kafka
Summary: [Debezium](http://debezium.io) is an open source distributed platform for [change data capture](https://en.wikipedia.org/wiki/Change_data_capture). Start it up, point it at your databases, and your apps can start responding to all of the inserts, updates, and deletes that other apps commit to your databases. Debezium is durable and fast, so your apps can respond quickly and never miss an event, even when things go wrong.

## Overview

[Debezium](http://debezium.io) is an open source distributed platform for [change data capture](https://en.wikipedia.org/wiki/Change_data_capture). Start it up, point it at your databases, and your apps can start responding to all of the inserts, updates, and deletes that other apps commit to your databases. Debezium is durable and fast, so your apps can respond quickly and never miss an event, even when things go wrong.

## Setup

The following assumes you have [Kubernetes running locally via Minikube](running-kubernetes-locally-via-minikube).

#### Start minikube cluster
```sh
minikube start
```

#### Clone Debezium Kubernetes repo
```sh
git clone https://github.com/debezium/debezium-kubernetes.git
cd debezium-kubernetes
```
> NOTE:  The `debezium-kubernetes` repo uses outdated docker images and an outdated fabric8 version.  Need to update each `pom.xml` file:

- Change the docker images from `0.1-SNAPSHOT` to `0.8-SNAPSHOT`

```xml
<groupId>io.debezium</groupId>
<version>0.8-SNAPSHOT</version>
```

- Change the fabric 8 version from `2.2.115` to `2.2.215`

```xml
<fabric8.version>2.2.215</fabric8.version>
```

#### Build with Maven
```sh
mvn clean install
```

#### Deploy with Maven
```sh
mvn fabric8:apply
```

#### Get pod details
```sh
kubectl get pods
kubectl describe pods
```

## Kafka

#### Create a `schema-changes` topic for Debezium's MySQL connector
```sh
DB_NAME=ticketmonster
TOPIC=schema-changes.$DB_NAME
KAFKA_POD_NAME=$(kubectl get pod | grep -i running | grep kafka | awk '{ print $1 }')
kubectl exec $KAFKA_POD_NAME -- /kafka/bin/kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic $TOPIC 
```

## MySQL

#### Connect to the MySQL command line
```sh
MYSQL_POD_NAME=$(kubectl get pod | grep Running | grep ^mysql | awk '{ print $1 }')
MYSQL_POD_IP=$(kubectl describe pod $MYSQL_POD_NAME | grep IP | awk '{ print $2 }')
kubectl exec -it $MYSQL_POD_NAME -- /opt/rh/rh-mysql56/root/usr/bin/mysql -h$MYSQL_POD_IP -P3306 -uroot -padmin
```

#### Execute SQL

Skip this (see note below)

```
#kubectl exec -it $MYSQL_POD_NAME -- bash -c "curl -s -L https://gist.github.com/christian-posta/e20ddb5c945845b4b9f6eba94a98af09/raw | /opt/rh/rh-mysql56/root/usr/bin/mysql -h$MYSQL_POD_IP -P3306 -uroot -padmin"
```
> NOTE: The `GRANT` statements from the above script breaks replication.  Also this script references a different `inventory` database than the `ticketmonster` database that the `mysql56` image includes.

Instead use these statements that work

```sql
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replicator' IDENTIFIED BY 'replpass';
GRANT ALL PRIVILEGES ON ticketmonster.* TO 'ticket'@'%';
USE ticketmonster;
```

Proceed with the rest of the SQL script located [here](https://gist.github.com/christian-posta/e20ddb5c945845b4b9f6eba94a98af09/raw).

## Start Kafka Connect and Debezium

#### Expose API

###### In a new shell

Expose the API for the Kafka Connect cluster via pod port-forwarding (forward the pod's 8083 port to our local machine)

```sh
CONNECT_POD_NAME=$(kubectl get pod | grep -i running | grep ^connect | awk '{ print $1 }')
kubectl port-forward $CONNECT_POD_NAME 8083:8083
```

#### View Kafka Connect logs

###### In a new shell

```sh
CONNECT_POD_NAME=$(kubectl get pod | grep -i running | grep ^connect | awk '{ print $1 }')
kubectl logs -f $CONNECT_POD_NAME
```

#### Create a Debezium connector using the Kafka Connect service's REST API

```sh
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:8083/connectors/ -d '{ "name": "ticketmonster-connector", "config": { "connector.class": "io.debezium.connector.mysql.MySqlConnector", "tasks.max": "1", "database.hostname": "mysql", "database.port": "3306", "database.user": "replicator", "database.password": "replpass", "database.server.id": "184054", "database.server.name": "mysql-server-1", "database.binlog": "mysql-bin.000001", "database.whitelist": "ticketmonster", "database.history.kafka.bootstrap.servers": "kafka:9092", "database.history.kafka.topic": "schema-changes.ticketmonster" } }'
```

#### Consume all event streams from the Kafka topic
```sh
KAFKA_POD_NAME=$(kubectl get pod | grep -i running | grep ^kafka | awk '{ print $1 }')
kubectl exec $KAFKA_POD_NAME -- /kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic mysql-server-1.ticketmonster.customers --from-beginning --property print.key=true
```

#### List Kafka topics
```sh
kubectl exec $KAFKA_POD_NAME -- /kafka/bin/kafka-topics.sh --list --zookeeper zookeeper:2181
```

#### Delete connector
```sh
curl -X DELETE http://localhost:8083/connectors/ticketmonster-connector
```
