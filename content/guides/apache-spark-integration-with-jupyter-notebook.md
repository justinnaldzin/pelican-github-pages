Title: Apache Spark integration with Jupyter Notebook
Date: 2017-4-11
Tags: apache, spark, pyspark, python, jupyter
Summary: This guide explains how to install PySpark locally and integrate with Jupyter Notebook.


## Table of Contents

This guide explains how to install PySpark locally and integrate with Jupyter Notebook.
Here are the steps to follow:

1. [Jupyter Notebook overview](#jupyter-notebook-overview)
2. [Install the required packages](#required-packages)
    - [Python 3.5+](#python)
    - [Java SE Development Kit](#java)
    - [Apache Spark 2.1.0](#apache-spark)
    - [Scala Build Tool](#scala-build-tool)
3. [Build Apache Spark](#build-apache-spark)
4. [Set environment variables](#environment-variables)
5. [Install Jupyter Notebook](#jupyter-notebook)
6. [Install a Spark kernel for Jupyter Notebook](#install-a-spark-kernel-for-jupyter-notebook)


## Jupyter Notebook overview

[Jupyter Notebook](http://jupyter.org/) has support for over 40 programming languages, with the most popular being Python, R, Julia and Scala.  The different components of Jupyter include:

- Jupyter Notebook App
- Jupter documents
- kernels
- Notebook Dashboard

Be sure to check out the [Jupyter Notebook beginner guide](http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/index.html) to learn more, including [how to install Jupyter Notebook](https://jupyter.readthedocs.io/en/latest/index.html).


## Required packages

Integrating PySpark with Jupyter Notebook requires the following packages:

1. Python 3.5+
2. Java SE Development Kit
3. Apache Spark 2.1.0
4. Scala Build Tool
5. Jupyter Notebook


#### Python

Download and Install Python 3
 - [download link](https://www.python.org/downloads/)

#### Java

Java 7+ is required which you can download from Oracle's website

- [macOS download link](https://www.java.com/en/download/faq/java_mac.xml)
- [Linux download link](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)

#### Apache Spark

On the [Spark downloads page](http://spark.apache.org/downloads.html), choose to download the zipped Spark source code (.tgz file).
Unzip the .tgz file and move the folder to your home directory.
Create a symbolic link from `$HOME/spark`.

#### Scala build tool

In order to build Spark, you will need the Scala build tool, which you can install via:

- macOS: `brew install sbt`
- Linux: [instructions](http://www.scala-sbt.org/release/tutorial/Installing-sbt-on-Linux.html)


## Build Apache Spark

Navigate to the directory where you unzipped Spark and run `sbt assembly` to build Spark.

`sbt package`

Or with maven

```
export MAVEN_OPTS="-Xmx2g -XX:ReservedCodeCacheSize=512m"
./build/mvn -Pyarn -Phadoop-2.4 -Dhadoop.version=2.4.0 -DskipTests clean package
./build/mvn -Phadoop-2.7,yarn,mesos,hive,hive-thriftserver -DskipTests clean install
```

## Environment variables

Add the following environment variables to your `~/.bash_profile`

```
# Spark
export PYTHONPATH=$PYTHONPATH:$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-x.zip
export PYSPARK_SUBMIT_ARGS="--master local[*]"
echo "SPARK_HOME=/path_to_downloaded_spark/" >> .bash_profile
echo "PATH=$PATH:/$SPARK_HOME/bin:/$SPARK_HOME/python:/$SPARK_HOME/python/lib/py4j-x.x.x-blahblah.zip" >> .bash_profile
```


## Install Jupyter Notebook

Install with `pip`
```sh
pip install jupyter
```


## Install a Spark kernel for Jupyter Notebook

Currently there are three ways to configure Spark in Jupyter notebooks

1. PySpark with IPythonKernel
2. [Apache Toree](https://toree.apache.org)
3. [Sparkmagic](https://github.com/jupyter-incubator/sparkmagic) kernel

### Using PySpark with IPythonKernel

Setting up PySpark in Jupyter is the easiest way to get started with interactive Spark sessions.

Define a new kernel by creating a JSON file at: `/usr/local/share/jupyter/kernels/pyspark/kernel.json`
```json
{
 "display_name": "PySpark",
 "language": "python",
 "argv": [
  "/path/to/bin/python3",
  "-m",
  "ipykernel",
  "-f",
  "{connection_file}"
 ],
 "env": {
  "SPARK_HOME": "/path/to/spark/",
  "PYTHONPATH": "/path/to/spark/python/:/path/to/spark/python/lib/py4j-0.x.x.x-src.zip",
  "PYTHONSTARTUP": "/path/to/spark/python/pyspark/shell.py",
  "PYSPARK_SUBMIT_ARGS": "--master local[*] --conf spark.executor.cores=1 --conf spark.executor.memory=512m pyspark-shell"
 }
}
```

By adding these environment variables, calling the `pyspark` executable directly will launch Jupyter Notebook with PySpark kernel
```sh
PYSPARK_PYTHON=python3
PYSPARK_DRIVER_PYTHON="jupyter"
PYSPARK_DRIVER_PYTHON_OPTS="notebook"
```

### Apache Toree

Toree is an Apache Incubating project originally created by developers at IBM.

Install Apache Toree
```sh
pip install toree
```

Configure Apache Toree installation with Jupyter.  Apache Toree supports multiple IPython kernels, including Python via PySpark. The beauty of Apache Toree is that it greatly simplifies adding new kernels with the –interpreters argument.
```sh
jupyter toree install --interpreters=PySpark
```

Confirm installation by listing the available kernels
```sh
jupyter kernelspec list
```

Launch Jupyter Notebook
```sh
jupyter notebook
```

### Sparkmagic

[Sparkmagic](https://github.com/jupyter-incubator/sparkmagic) is a set of tools for interactively working with remote Spark clusters through [Livy](http://livy.io), a Spark REST server, in Jupyter notebooks. The Sparkmagic project includes a set of magics for interactively running Spark code in multiple languages, as well as some kernels that you can use to turn Jupyter into an integrated Spark environment.
