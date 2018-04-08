Title: Jupyter Notebook with Apache Spark
Date: 2018-4-1
Tags: jupyter, spark, python, scala, java
Summary: This guide installs Python, Jupyter, Java, Scala, and Apache Spark

## Overview

This guide installs the following:

- Python 3.6.4
- Jupyter
- Java 1.8.0_162
- Scala 2.12.5
- Apache Spark 2.3.0

<p align="center">
<img src="images/logos/jupyter.png" alt="Jupyter" width="200" valign="bottom" hspace="30" vspace="10">
<img src="images/logos/spark.png" alt="Spark" valign="top" hspace="20" vspace="10">
</p>

## Setup

#### Install Python 3.6
```sh
brew install python3
```

#### Install Jupyter
```sh
pip3 install jupyter
```

#### Install Java
```sh
brew update
brew tap caskroom/cask
brew cask install java
```

#### Install Apache Spark and Scala
```sh
brew update
brew install scala
brew install apache-spark
```

## Update `.bash_profile`

Add the following to `~/.bash_profile`

```sh
# For Apache Spark
if which java > /dev/null; then export JAVA_HOME=$(/usr/libexec/java_home); fi

# For ipython notebook and pyspark integration
if which pyspark > /dev/null; then
  export SPARK_HOME="/usr/local/Cellar/apache-spark/2.3.0/libexec/"
  export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/build:$PYTHONPATH
  export PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.6-src.zip:$PYTHONPATH
fi
```

## Launch Jupyter Notebook
```sh
jupyter notebook
```

#### Install `findspark`

Within a new Notebook using the Python 3 kernel, use [findspark](https://github.com/minrk/findspark) to add PySpark to `sys.path` at runtime

```python
!pip3 install findspark

import findspark
findspark.init()
```

## Example script

The following example script loads tables from an external MySQL database

> NOTE: Download the [JDBC driver for MySQL (Connector/J)](https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.46.zip)

```
import os
os.environ["PYSPARK_SUBMIT_ARGS"] = "--packages mysql:mysql-connector-java:5.1.46 pyspark-shell"

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext

# Create SparkContext and SQLContext
appName = "PySpark app"
conf = SparkConf().setAppName(appName)
sc = SparkContext(conf=conf)
sqlContext = SQLContext(sc)

# Config
host = '10.0.0.1'
database = 'mydatabase'
table = 'mytable'
url='jdbc:mysql://{}/{}'.format(host, database)
properties = {
    'user': 'root',
    'password': 'password',
    'driver': 'com.mysql.jdbc.Driver'
}

df = sqlContext.read.jdbc(url, table, properties=properties)
df.show()
```
