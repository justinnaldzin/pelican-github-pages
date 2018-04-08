Title: Google Cloud Datalab on a Cloud Dataproc cluster
Date: 2018-3-30
Tags: google cloud, dataproc, datalab, pyspark, apache spark
Summary: This guide shows how to use an initialization action to install Cloud Datalab on a Cloud Dataproc cluster.

# Overview

This guide shows how to use an initialization action to install Cloud Datalab on a Cloud Dataproc cluster.

<p align="center">
<img src="images/logos/card_gcp_clouddatalab.png" alt="Cloud Datalab" hspace="20" vspace="20" valign="middle">
<img src="images/logos/card_gcp_clouddataproc.png" alt="Cloud Dataproc" hspace="20" vspace="20" valign="middle">
<img src="images/logos/spark.png" alt="Apache Spark" width="200" hspace="20" vspace="20" valign="middle">
</p>

## Create a Cloud Storage bucket

> NOTE: The Dataproc staging bucket is NOT used to store Datalab notebooks.

```sh
PROJECT_NAME=my-project-name
STORAGE_CLASS=regional
BUCKET_LOCATION=us-east1
CLUSTER_NAME=dataproc-spark-cluster-1
BUCKET_NAME=${CLUSTER_NAME}-${BUCKET_LOCATION}
gsutil mb -p $PROJECT_NAME -c $STORAGE_CLASS -l $BUCKET_LOCATION gs://$BUCKET_NAME/
```

## Create Dataproc cluster with Datalab initialization action

```sh
PROJECT_ID=my-project-id
REGION=$BUCKET_LOCATION
ZONE=${REGION}-d
gcloud dataproc clusters create $CLUSTER_NAME --project $PROJECT_ID --bucket $BUCKET_NAME --region $REGION --zone $ZONE --initialization-actions gs://dataproc-initialization-actions/datalab/datalab.sh
```

## Dynamic Port Forwarding

To avoid opening a publicly reachable port on the cluster's master node, use dynamic port forwarding (via an SSH tunnel using the SOCKS protocol) to connect your browser to the Datalab notebook running on your cluster's master node.

## Setup SSH tunnel

Create an SSH tunnel to your cluster's master node from port 10000 on your localhost machine

```sh
MASTER_HOST_NAME=${CLUSTER_NAME}-m
PORT=10000
gcloud compute ssh $MASTER_HOST_NAME --project $PROJECT_ID --zone=$ZONE -- -D $PORT -N
```

## Open Datalab in your browser

Launch a new browser that connects through the SSH tunnel (using the SOCKS protocol) to the Datalab application running on your cluster's master node.

```sh
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome "http://$MASTER_HOST_NAME:8080" --proxy-server="socks5://localhost:$PORT" --host-resolver-rules="MAP * 0.0.0.0 , EXCLUDE localhost" --user-data-dir=/tmp/
```

Creating a new notebook with the Python3 kernel has the `SparkContext` available as `sc`

## Dataproc Web Interfaces

- Yarn Resource Manager:  http://master-host-name:8088
- HDFS NameNode:  http://master-host-name:9870
- Spark Master UI:  http://master-host-name:4040
- Spark History Server:  http://master-host-name:18080
- Hadoop Job History Server:  http://master-host-name:19888
