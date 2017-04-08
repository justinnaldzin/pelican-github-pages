Title: Sqoop and Hive Best Practices
Date: 2017-4-7
Category: Guides
Tags: sqoop, hive, hadoop, hdfs

The following describes the HDFS architecture and best practices of using Sqoop and Hive to load data from relational databases.


## Architecture


#### Overview

- Tables brought into HDFS using Sqoop should be imported into a staging area using a temporary external table.
- Hive SQL will be used to select from the external staging table and insert the data into the production table.
- Data in staging will be deleted upon successful load to production.

#### HDFS

- HDFS Location: `/data/<schema>`
- Staging: `/data/<schema>/staging`
- Production: `/data/<schema>/production`
- Avro Schema: `/metadata/<schema>/<table>.avsc`

#### Hive

- External tables should be created to point to HDFS locations within the production HDFS directory.

#### Partitioning

- Where applicable, data should be partitioned by a `date` column.
- Use Hive's dynamic partitioning feature to automatically create partitions on data insert.



## Workflow

#### Setup

Define project variables
```sh
HOSTNAME=<hostname>
USERNAME=<username>
DATABASE=<database>
SCHEMA=$DATABASE
TABLE=<table>
STAGE_TABLE=STG_$TABLE
```

Create HDFS file structure
```sh
hadoop fs -mkdir /data/$SCHEMA/staging/$TABLE
hadoop fs -mkdir /data/$SCHEMA/production/$TABLE
hadoop fs -chown hive:hdfs /data/$SCHEMA/staging/$TABLE
hadoop fs -chown hive:hdfs /data/$SCHEMA/production/$TABLE
hadoop fs -chmod -R 777 /data/$SCHEMA/staging/$TABLE
hadoop fs -chmod -R 777 /data/$SCHEMA/production/$TABLE
```

Create a Hive Database named the same as the HDFS Schema above
```sql
hive -e "CREATE DATABASE IF NOT EXISTS $DATABASE;"
```

#### Staging

Sqoop Import into HDFS
```sh
sqoop import --connect 'jdbc:sqlserver://'"$HOSTNAME"';database='"$DATABASE" \
--username $USERNAME -P --verbose \
--table $TABLE \
--as-avrodatafile \
--compress \
--verbose \
--target-dir "/data/$SCHEMA/staging/$TABLE" \
--delete-target-dir  \
&> $TABLE.log
```

Copy the AVRO schema to HDFS
```sh
hadoop fs -put $TABLE.avsc /metadata/${SCHEMA,,}/${TABLE,,}.avsc
```

Run the Hive DDL
```sh
hive -e "CREATE EXTERNAL TABLE $DATABASE.$STAGE_TABLE
ROW FORMAT SERDE
'org.apache.hadoop.hive.serde2.avro.AvroSerDe'
STORED AS INPUTFORMAT
'org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat'
OUTPUTFORMAT
'org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat'
LOCATION '/data/${SCHEMA,,}/stage/$TABLE'
TBLPROPERTIES (
'avro.schema.url'='/metadata/${SCHEMA,,}/${TABLE,,}.avsc');"
```

Test the Staging table
```sh
hive -e "SELECT * FROM $DATABASE.$STAGE_TABLE LIMIT 10;"
```

#### Production

Run the Hive DDL
```sh
hive -e "CREATE EXTERNAL TABLE $DATABASE.$TABLE(
    <COLUMN_1> <DATATYPE>,
    ...
    <COLUMN_n> <DATATYPE>
)
STORED AS ORC
LOCATION '/data/${SCHEMA,,}/production/${TABLE,,}';"
```

Copy data from Staging to Production
```sh
hive -e "SET hive.exec.dynamic.partition=true;"
hive -e "USE $DATABASE;"
hive -e "INSERT INTO TABLE $DATABASE.$TABLE
         SELECT * FROM $DATABASE.$STAGE_TABLE;"
hive -e "ANALYZE TABLE $DATABASE.$TABLE COMPUTE STATISTICS FOR COLUMNS;"
```

Truncate Staging table
```sh
hive -e "TRUNCATE TABLE IF EXISTS $DATABASE.$STAGE_TABLE"
```

Incremental load process should run with [Oozie](https://oozie.apache.org/) or cron.
