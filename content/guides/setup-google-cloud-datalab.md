Title: Setup Google Cloud Datalab
Date: 2018-3-25
Tags: google cloud, datalab
Summary: The following guide shows how to use the `datalab` command line tool to set up and open Google Cloud Datalab.

# Overview

The following guide shows how to use the `datalab` command line tool to set up and open Google Cloud Datalab.

<p align="center">
<img src="images/logos/card_gcp_clouddatalab.png" alt="Cloud Datalab">
</p>

#### Update to the latest gcloud version
```sh
gcloud components update
```

#### Install Datalab
```sh
gcloud components install datalab
```

#### Create Datalab instance

The `datalab create` command also creates the following Google Cloud Platform resources:

1. The `datalab-network` network
2. A firewall rule on the `datalab-network` allowing incoming SSH connections
3. The `datalab-notebooks` Google Cloud Source Repository
4. The persistent disk for storing Cloud Datalab notebooks

```sh
INSTANCE_NAME=my-datalab-instance
datalab create $INSTANCE_NAME
```

#### Stop Datalab instance to avoid incurring unnecessary costs

```sh
datalab stop $INSTANCE_NAME
```

#### Connect to Datalab after the instance is stopped

```sh
datalab connect $INSTANCE_NAME
```

#### Delete Datalab VM instance and its Persistent Disk
```sh
datalab delete --delete-disk $INSTANCE_NAME
```

#### Delete Datalab VM instance without deleting the Persistent Disk
```sh
datalab delete --keep-disk $INSTANCE_NAME
```

---
