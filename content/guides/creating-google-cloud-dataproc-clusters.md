Title: Creating Google Cloud Dataproc Clusters
Date: 2018-3-20
Tags: google cloud, dataproc
Summary: [Cloud Dataproc](https://cloud.google.com/dataproc/) is a managed Spark and Hadoop service that lets you take advantage of open source data tools for batch processing, querying, streaming, and machine learning. Cloud Dataproc automation helps you create clusters quickly, manage them easily, and save money by turning clusters off when you don't need them. With less time and money spent on administration, you can focus on your jobs and your data.

[Cloud Dataproc](https://cloud.google.com/dataproc/) is a managed Spark and Hadoop service that lets you take advantage of open source data tools for batch processing, querying, streaming, and machine learning. Cloud Dataproc automation helps you create clusters quickly, manage them easily, and save money by turning clusters off when you don't need them. With less time and money spent on administration, you can focus on your jobs and your data.

<p align="center">
<img src="images/logos/gcp_clouddataproc.png" alt="Cloud Dataproc">
</p>

## Create a Cloud Dataproc cluster

```sh
CLUSTER_NAME=my-cluster
gcloud dataproc clusters create $CLUSTER_NAME
```

The above command creates a cluster with default Cloud Dataproc service settings.  Noteable cluster settings that are worth changing are:

- Staging bucket
   - Staging buckets are used for miscellaneous configuration and control files as well as output from the Cloud SDK gcloud dataproc clusters [diagnose](https://cloud.google.com/dataproc/docs/support/diagnose-command) command. 
- Network
   - Define a Compute Engine network to configure Firewall rules for connecting to the cluster and viewing the UI.

## Describe cluster
```sh
gcloud dataproc clusters describe $CLUSTER_NAME
```

## Delete cluster
> NOTE: Deleting the cluster does NOT delete the associated Cloud Storage bucket.

```sh
gcloud dataproc clusters delete $CLUSTER_NAME 
```

## Delete cluster and storage bucket
```sh
BUCKET_NAME=$(gcloud dataproc clusters describe $CLUSTER_NAME --format=json | jq -r '.config.configBucket')
gcloud dataproc clusters delete $CLUSTER_NAME 
gsutil -m rm -r gs://$BUCKET_NAME
```
