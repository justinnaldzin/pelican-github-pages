Title: Running Kubernetes locally via Minikube
Date: 2018-3-1
Tags: kubernetes, minikube, kubectl
Summary: [Kubernetes](https://kubernetes.io) is an open-source system for automating deployment, scaling, and management of containerized applications.  [Minikube](https://github.com/kubernetes/minikube) is a tool that makes it easy to run Kubernetes locally. Minikube runs a single-node Kubernetes cluster inside a VM on your laptop for users looking to try out Kubernetes or develop with it day-to-day.

## Overview

[Kubernetes](https://kubernetes.io) is an open-source system for automating deployment, scaling, and management of containerized applications.

[Minikube](https://github.com/kubernetes/minikube) is a tool that makes it easy to run Kubernetes locally. Minikube runs a single-node Kubernetes cluster inside a VM on your laptop for users looking to try out Kubernetes or develop with it day-to-day.

<p align="center">
<img src="images/logos/kubernetes_logo.png" alt="Kubernetes" hspace="100" vspace="10">
<img src="images/logos/kubernetes_name.png" alt="Kubernetes" hspace="100" vspace="10">
</p>

## Requirements

#### Install Java 8

> NOTE: Java 9 fails as of this writing

```sh
brew tap caskroom/versions
brew update
brew cask install java8
```

#### Install kubectl
```sh
brew install kubectl
```

#### Install VirtualBox
```sh
brew cask install virtualbox
brew cask install virtualbox-extension-pack
```

#### Install Minikube
```sh
brew cask install minikube
```

### kubectl Configuration

The kubectl config file is located at:

**~/.kube/config**

```sh
apiVersion: v1
clusters:
- cluster:
    certificate-authority: /Users/user/.minikube/ca.crt
    server: https://192.168.99.100:8443
  name: minikube
contexts:
- context:
    cluster: minikube
    user: minikube
  name: minikube
current-context: minikube
kind: Config
preferences: {}
users:
- name: minikube
  user:
    as-user-extra: {}
    client-certificate: /Users/user/.minikube/client.crt
    client-key: /Users/user/.minikube/client.key
```

## Hello World

#### Start minikube cluster
```sh
minikube start
```

Starting minikube automatically generates a kubeconfig entry and switches to that context.

#### Show kubectl contexts
```sh
kubectl config get-contexts
kubectl config use-context minikube
```

#### View cluster info
```sh
kubectl cluster-info
```

#### Run an image creating a deployment
```sh
kubectl run hello-minikube --image=k8s.gcr.io/echoserver:1.4 --port=8080
kubectl expose deployment hello-minikube --type=NodePort
kubectl get pod
curl $(minikube service hello-minikube --url)
```

#### Kubernetes Dashboard
```sh
minikube dashboard
```

#### Delete deployment
```sh
kubectl delete deployment hello-minikube
```

#### Stopping a Cluster
```sh
minikube stop
```

#### Deleting a Cluster
```sh
minikube delete
```
