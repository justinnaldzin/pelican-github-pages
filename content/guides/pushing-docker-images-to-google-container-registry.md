Title: Pushing Docker images to Google Container Registry
Date: 2018-3-17
Tags: google cloud, container registry, docker
Summary: The following guide explains how to build Docker images and push to [Google Container Registry](https://cloud.google.com/container-registry/docs/).

### Overview

The following guide explains how to build Docker images and push to [Google Container Registry](https://cloud.google.com/container-registry/docs/).

<p align="center">
<img src="images/logos/card_gcp_containerregistry.png" alt="Container Registry">
</p>

### Build Docker image
```sh
IMAGE_NAME=my-image
docker build -t $IMAGE_NAME .
```

### Tag the image with a registry name
```sh
PROJECT_ID=my-gcp-project
TAG=1.0
docker tag $IMAGE_NAME gcr.io/$PROJECT_ID/$IMAGE_NAME:$TAG
```

### Push the image to Container Registry
```sh
gcloud docker -- push gcr.io/$PROJECT_ID/$IMAGE_NAME:$TAG
```

### View the image's registry name in web browser
```sh
open http://gcr.io/$PROJECT_ID/$IMAGE_NAME
```

### Delete the image from Container Registry
```sh
gcloud container images delete gcr.io/$PROJECT_ID/$IMAGE_NAME:$TAG
```
