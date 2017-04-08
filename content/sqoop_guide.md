Title: Sqoop Guide
Date: 2017-4-1
Category: Guides
Tags: sqoop, hadoop, hdfs

## Overview

The following guide explains how to use Sqoop to transfer data from relational databases to Hadoop HDFS


## What is Sqoop?

Sqoop is a command-line tool designed to transfer data between relational database servers and Hadoop.  It has the ability to import and export data between Hadoop HDFS and multiple relational databases such as MySQL, Oracle, and SQL Server.


## Installing JDBC Drivers

Download and install the **MySQL** JDBC Driver
```sh
curl -L 'https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.41.tar.gz' | tar xz
sudo cp mysql-connector-java-5.1.41/mysql-connector-java-5.1.41-bin.jar /usr/hdp/current/sqoop-client/lib
```

Download and install the **Oracle** JDBC Driver
```sh
curl -L 'http://download.oracle.com/otn/utilities_drivers/jdbc/11204/ojdbc6.jar'
sudo cp ojdbc6.jar /usr/hdp/current/sqoop-client/lib
```

Download and install the **Microsoft SQL Server** JDBC Driver
```sh
curl -L 'https://download.microsoft.com/download/0/2/A/02AAE597-3865-456C-AE7F-613F99F850A8/enu/sqljdbc_6.0.81cd12.100_enu.tar.gz' | tar xz
sudo cp sqljdbc_6.0/enu/jre8/sqljdbc42.jar /usr/hdp/current/sqoop-client/lib
```

Alternatively specify the classpath to the driver
```sh
export HADOOP_CLASSPATH=/usr/local/jars/sqljdbc4.jar
```


## Sqoop basics

Check sqoop version
```sh
sqoop version
```

List of commands
```sh
sqoop help
```

More command specific
```sh
sqoop help import
```

List databases
```sh
sqoop list-databases --connect 'jdbc:sqlserver://<hostname>' --username <username> -P --verbose
```

List tables
```sh
sqoop list-tables --connect 'jdbc:sqlserver://<hostname>;database=<database>' \
--username <username> -P --verbose
```


## Transfer relational database tables into Hadoop HDFS


#### Sqoop Import into HDFS

Import from a table
```sh
sqoop import --connect 'jdbc:sqlserver://<hostname>\;database=<database>' \
--username <username> -P --verbose
--table <table> \
--as-avrodatafile \
--compress \
--verbose \
--target-dir "/data/<schema>/staging/<table>"
```

Import from a table with `where` conditions
```sh
sqoop import --connect 'jdbc:sqlserver://<hostname>\;database=<database>' \
--username <username> -P --verbose
--table <table> \
--as-avrodatafile \
--compress \
--verbose \
--target-dir "/data/<schema>/staging/<table>" \
--where "1=1" \
--num-mappers <n>  #  Use 'n' map tasks to import in parallel
```

Import from a table specifying a query
```sh
sqoop import --connect 'jdbc:sqlserver://<hostname>\;database=<database>' \
--username <username> -P --verbose
--table <table> \
--as-avrodatafile \
--compress \
--verbose \
--target-dir "/data/<schema>/staging/<table>" \
--query 'SELECT * FROM <table> WHERE 1=1' \
--delete-target-dir  # Overwrite target directory if it already exists
```

#### Sqoop Job

Create a Sqoop Job
```sh
sqoop job --create <jobname> \
-- \
import \
--connect 'jdbc:sqlserver://<hostname>\;database=<database>' \
--username <username> --password-file .secrets \
--table <table> \
--check-column <primarykey> \
--as-avrodatafile \
--compress \
--verbose \
--target-dir "/data/<schema>/staging/<table>" \
--incremental append \
--last-value 0 \
--split-by <primarykey>
```

Create a password file
```sh
echo -n <password> > .secrets
```

Verify Job
```sh
sqoop job --list
```

Inspect Job
```sh
sqoop job --show <jobname>
```

Execute Job
```sh
sqoop job --exec <jobname>
```

#### Sqoop Import into Hive

Import from a table and create Hive table
```sh
sqoop import --connect 'jdbc:sqlserver://<hostname>\;database=<database>' \
--username <username> -P --verbose \
--table <table> \
--hive-import \
--create-hive-table
```
