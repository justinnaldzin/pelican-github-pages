Title: Apache Spark integration with Jupyter Notebook
Date: 2017-5-16
Tags: apache, spark, pyspark, python, jupyter
Summary: This guide explains multiple ways to install Apache Spark 2.x locally and integrate with Jupyter Notebook by installing various Spark kernels.


## Table of Contents

This guide explains multiple ways to install Apache Spark 2.x locally and integrate with Jupyter Notebook by installing various Spark kernels.

1. [Apache Spark 2.x overview](#apache-spark-2.x-overview)
2. [Jupyter Notebook overview](#jupyter-notebook-overview)
3. [Install the required packages](#required-packages)
    - [Python 3.5+](#python)
    - [Java SE Development Kit](#java)
4. [Install Apache Spark](#install-apache-spark)
    - [Pre-built](#pre-built)
    - [Source code](#source-code)
5. [Set environment variables](#set-environment-variables)
6. [Install Jupyter Notebook](#install-jupyter-notebook)
7. [Install a Spark kernel for Jupyter Notebook](#install-a-spark-kernel-for-jupyter-notebook)
    - [PySpark with IPythonKernel](#pyspark with ipythonkernel)
    - [Apache Toree](#apache-toree)
    - [Sparkmagic](#sparkmagic)


## Apache Spark 2.x overview

Apache Spark is an open-source cluster-computing framework.  Spark provides an interface for programming entire clusters with implicit data parallelism and fault-tolerance.  The release of Spark 2.0 included a number of significant improvements including unifying DataFrame and DataSet, replacing SQLContext and HiveContext with the SparkSession entry point, and much more.  As of this writing, Spark's latest release is 2.1.1.


## Jupyter Notebook overview

[Jupyter Notebook](http://jupyter.org/) is a web-based interactive computational environment in which you can combine code execution, rich text, mathematics, plots and rich media to create a notebook.  The actual Jupyter notebook is nothing more than a JSON document containing an ordered list of input/output cells.  Jupyter notebooks an be converted to a number of open standard output formats including HTML, presentation slides, LaTeX, PDF, ReStructuredText, Markdown, and Python.

Jupyter Notebook has support for over 40 programming languages, with the most popular being Python, R, Julia and Scala.  The different components of Jupyter include:

- Jupyter Notebook App
- Jupter documents
- kernels
- Notebook Dashboard

Be sure to check out the [Jupyter Notebook beginner guide](http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/index.html) to learn more, including [how to install Jupyter Notebook](https://jupyter.readthedocs.io/en/latest/index.html).

Additionally check out some [Jupyter Notebook tips, tricks and shortcuts](https://www.dataquest.io/blog/jupyter-notebook-tips-tricks-shortcuts/).


## Required packages

Integrating Spark with Jupyter Notebook requires the following packages:

- Python 3.5+
- Java SE Development Kit
- Apache Spark 2.x
- Jupyter Notebook


#### Python

Download and Install Python 3
 - [download link](https://www.python.org/downloads/)


#### Java

Java 7+ is required for Spark which you can download from Oracle's website

- [macOS download link](https://www.java.com/en/download/faq/java_mac.xml)
- [Linux download link](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)

## Install Apache Spark

There are two types of Spark packages available to download:

- Pre-built for Apache Hadoop 2.7 and later
- Source code


#### Pre-built

The pre-built package is the simplest option.

On the [Spark downloads page](http://spark.apache.org/downloads.html), choose to download the zipped Spark package pre-built for Apache Hadoop 2.7+.  Unzip the .tgz file and move the folder to your home directory.

```sh
wget -qO- https://d3kbcqa49mib13.cloudfront.net/spark-2.1.1-bin-hadoop2.7.tgz | tar xvz -C ~/
```

Create a symbolic link from this folder to `~/spark`.

```sh
ln -s ~/spark-2.1.1-bin-hadoop2.7 ~/spark
```


#### Source code

Building from the source code offers the ability to configure specific components to install and their version numbers.

On the [Spark downloads page](http://spark.apache.org/downloads.html), choose to download the zipped Spark source code package.  Unzip the .tgz file and move the folder to your home directory.

```sh
wget -qO- https://d3kbcqa49mib13.cloudfront.net/spark-2.1.1.tgz | tar xvz -C ~/
```

Create a symbolic link from this folder to `~/spark`

```sh
ln -s ~/spark-2.1.1 ~/spark
```

There are two options for building Spark.  The first one uses the Scala Build Tool (sbt) which needs to be installed

##### macOS:
```sh
brew install sbt
```

##### Linux:
```sh
curl https://bintray.com/sbt/rpm/rpm | sudo tee /etc/yum.repos.d/bintray-sbt-rpm.repo
yum -y install sbt
```

Navigate to the directory where you unzipped Spark and build Spark.

```sh
cd ~/spark
sbt assembly
sbt package
```

The second option for building Spark is with maven

```sh
export MAVEN_OPTS="-Xmx2g -XX:MaxPermSize=512M -XX:ReservedCodeCacheSize=512m"
cd ~/spark/
./dev/change-scala-version.sh 2.12  # specify Scala v2.12
./build/mvn -Pyarn -Phadoop-2.7,yarn,mesos,hive,hive-thriftserver -Dscala-2.12 -Dhadoop.version=2.7.0 -DskipTests clean package
```


## Set environment variables

##### macOS:

Add the environment variables to your bash profile located at `~/.bash_profile`

```
echo 'export SPARK_HOME=~/spark' >> ~/.bash_profile
echo 'export PYTHONPATH=$PYTHONPATH:$SPARK_HOME/python:$SPARK_HOME/python/lib:$SPARK_HOME/python/lib/py4j-0.10.4-src.zip' >> ~/.bash_profile
echo 'export PATH=$PATH:$SPARK_HOME/bin' >> ~/.bash_profile
echo 'export PYSPARK_PYTHON=python3' >> ~/.bash_profile
echo 'export PYSPARK_DRIVER_PYTHON=python3' >> ~/.bash_profile
source ~/.bash_profile
cp $SPARK_HOME/conf/log4j.properties.template $SPARK_HOME/conf/log4j.properties  # minimize the Verbosity of Spark
```


##### Linux:

Create a bash profile startup script located at `/etc/profile.d/spark.sh` and add the environment variables

```
echo 'export SPARK_HOME=~/spark' >> /etc/profile.d/spark.sh
echo 'export PYTHONPATH=$PYTHONPATH:$SPARK_HOME/python:$SPARK_HOME/python/lib:$SPARK_HOME/python/lib/py4j-0.10.4-src.zip' >> /etc/profile.d/spark.sh
echo 'export PATH=$PATH:$SPARK_HOME/bin' >> /etc/profile.d/spark.sh
echo 'export PYSPARK_PYTHON=python3' >> /etc/profile.d/spark.sh
echo 'export PYSPARK_DRIVER_PYTHON=python3' >> /etc/profile.d/spark.sh
source /etc/profile.d/spark.sh
cp $SPARK_HOME/conf/log4j.properties.template $SPARK_HOME/conf/log4j.properties  # minimize the Verbosity of Spark
```


## Install Jupyter Notebook

Install with `pip`
```sh
pip3 install jupyter
```


## Install a Spark kernel for Jupyter Notebook

There are three ways to add Spark kernels in Jupyter notebooks

1. PySpark with IPythonKernel
2. [Apache Toree](https://toree.apache.org)
3. [Sparkmagic](https://github.com/jupyter-incubator/sparkmagic) kernel


### PySpark with IPythonKernel

Setting up PySpark in Jupyter is the easiest way to get started with interactive Spark sessions.

Define a new kernel by creating a JSON file at: `/usr/local/share/jupyter/kernels/pyspark/kernel.json`
```json
{
 "display_name": "PySpark",
 "language": "python",
 "argv": [
  "/usr/bin/python3",
  "-m",
  "ipykernel",
  "-f",
  "{connection_file}"
 ],
 "env": {
  "SPARK_HOME": "~/spark/",
  "PYTHONPATH": "~/spark/python/:~/spark/python/lib/py4j-0.x.x.x-src.zip",
  "PYTHONSTARTUP": "~/spark/python/pyspark/shell.py",
  "PYSPARK_SUBMIT_ARGS": "--master local[*] --conf spark.executor.cores=1 --conf spark.executor.memory=512m pyspark-shell"
 }
}
```

By adding these environment variables, calling the `pyspark` executable directly will launch Jupyter Notebook with PySpark kernel

```sh
export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON="jupyter"
export PYSPARK_DRIVER_PYTHON_OPTS="notebook"
```

### Apache Toree

Toree is an Apache Incubating project originally created by developers at IBM.

**Note!** A pip-installable package isn't currently available for Toree v0.2.0 which is required for Spark 2.x support.  Therefore we need to build and package up Toree.  This requires [Docker](https://www.docker.com/) to be installed.

Setup the Docker repository

```
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum makecache fast
```

Install the latest version of Docker Community Edition

```
yum -y install docker-ce
usermod -aG docker $(whoami)  # add your user to the 'docker' group
```

Start Docker

```
systemctl start docker
systemctl enable docker
```

Clone and build Toree from the Toree repository from GitHub.

```
git clone https://github.com/apache/incubator-toree.git
cd incubator-toree/
APACHE_SPARK_VERSION=2.1.1 make pip-release
```

Install Toree from the archive

```
pip3 install dist/toree-pip/toree-0.2.0.dev1.tar.gz
```

Add all the Toree kernels to Jupyter
```sh
jupyter toree install --spark_home=$SPARK_HOME --interpreters=Scala,PySpark,SparkR,SQL --python_exec=python3 --spark_opts="--master=local[*]"
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
