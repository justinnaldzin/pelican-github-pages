Title: Configuring gcloud
Date: 2018-2-1
Tags: google cloud platform, gcloud
Summary: Configuring gcloud

<p align="center">
<img src="images/logos/gcp_googlecloud_vertical.png" alt="Google Cloud Platform" hspace="50">
</p>

# Configuring gcloud with user credentials

> NOTE: Repeat these steps if you need multiple configurations for different projects and accounts.

### Create a gcloud named configuration
```sh
CONFIG_NAME=my-config
gcloud config configurations create $CONFIG_NAME
```

### Initialize gcloud
```sh
gcloud init
```

Follow the prompts and ensure the config is now activated 

### List configurations
```sh
gcloud config configurations list
```

---

# Configuring gcloud to use a service account

### Creating a service account
```sh
PROJECT_ID=gcp-project-id
SERVICE_ACCOUNT_NAME=my-service-account
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME --display-name "$SERVICE_ACCOUNT_NAME"
```

### Granting roles to service accounts

##### Add a role to the service account

```sh
gcloud projects add-iam-policy-binding $PROJECT_ID --member='${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com' --role='roles/owner'
```

##### Alternatively add a group to the service account with a role

```sh
GROUP=group:my.group@domain.com
gcloud iam service-accounts add-iam-policy-binding ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --member=$GROUP --role='roles/owner'
```

### Create and download a private key
```sh
KEY_FILE=${SERVICE_ACCOUNT_NAME}_${PROJECT_ID}.json
gcloud iam service-accounts keys create $KEY_FILE --iam-account ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
```

### Create a gcloud named configuration
```sh
CONFIG_NAME=$SERVICE_ACCOUNT_NAME
gcloud config configurations create $CONFIG_NAME
```

### Activate service account
```sh
gcloud auth activate-service-account ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --key-file=$KEY_FILE
```

Ensure the config is now activated 

### List configurations
```sh
gcloud config configurations list
```

---

# Generating application default credentials

> NOTE: This creates a file located at: `/Users/user/.config/gcloud/application_default_credentials.json`

```sh
gcloud auth application-default login
```

---

# RBAC (Role-Based Access Control) for Google Kubernetes Engine 

### Setting up RBAC with `ClusterRoleBinding`

Create a `ClusterRoleBinding` that gives your Google identity a `cluster-admin` role to gain full control over every resource in the cluster and in all namespaces.  This is needed before attempting to create additional Role or ClusterRole permissions.  See the [RBAC documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/role-based-access-control) for more info.

```sh
kubectl create clusterrolebinding cluster-admin-binding --clusterrole cluster-admin --user $(gcloud config get-value account)
```
