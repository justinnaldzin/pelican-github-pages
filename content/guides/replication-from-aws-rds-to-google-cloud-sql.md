Title: Replication from AWS RDS MySQL to Google Cloud SQL (without downtime)
Date: 2018-4-7
Tags: aws, google cloud, rds, cloud sql, mysql
Summary: The following guide performs cloud-to-cloud replication from [Amazon Relational Database Service (RDS)](https://aws.amazon.com/rds/) to [Google Cloud SQL](https://cloud.google.com/sql/docs/).

## Overview

The following guide performs cloud-to-cloud replication from [Amazon Relational Database Service (RDS)](https://aws.amazon.com/rds/) to [Google Cloud SQL](https://cloud.google.com/sql/docs/).

<p align="center">
<img src="images/logos/aws_rds.png" alt="RDS" hspace="50">
<img src="images/logos/gcp_cloudsql.png" alt="Cloud SQL" hspace="50">
</p>

#### Requirements

Replicating AWS RDS instances to Google Cloud SQL requires the following:

1. The AWS RDS master must have an Elastic (public) IP address which enables the instance to be reached from the Internet.  Both [VPC](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.Scenarios.html#USER_VPC.Scenario4) and [non-VPC](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.Scenarios.html#USER_VPC.Scenario6) networks are supported.
2. The AWS RDS database engine must be MySQL v5.5 or v5.6.  PostgreSQL is [not yet supported](https://cloud.google.com/sql/docs/postgres/replication/configure-external-master) in Cloud SQL.
3. Binary logging format must be `ROW` on the RDS master requiring an instance restart*.
   -  *Creating a separate read-replica avoids downtime to the master instance.
4. The `server-id` option must be set to a value of 2 or larger.

There are a few [additional requirements](https://cloud.google.com/sql/docs/mysql/replication/tips#external-master) for Cloud SQL but the above addresses specifics to default configurations of AWS RDS.

#### Replication types

Google Cloud SQL supports [three replication types](https://cloud.google.com/sql/docs/mysql/replication/) to replicate a master instance to one or more read-replicas:

1. Read-Replica (Cloud SQL instances that replicate from a Cloud SQL master instance)
2. External Read-Replica (external MySQL instances that are replicating from a Cloud SQL master)
3. **External master (External MySQL instance to Cloud SQL)**

#### External master

[External masters](https://cloud.google.com/sql/docs/mysql/replication/tips#external-master) are MySQL instances that are external to Cloud SQL (such as AWS RDS) and serve as masters to a Cloud SQL instance.

![image](https://cloud.google.com/sql/images/external-master.svg)

## AWS RDS MySQL Configuration

### AWS Credentials

Ensure AWS CLI credentials exist:

**~/.aws/credentials**

```sh
[default]
aws_access_key_id=AKIAIOSFODNN7EXAMPLE
aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[my-named-profile]
aws_access_key_id=AKIAI44QH8DHBEXAMPLE
aws_secret_access_key=je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
```

Use the correct named profile:

```sh
export AWS_PROFILE=my-named-profile
```

### Identify VPC

If the RDS instance exists within a VPC, we need to specify that VPC:

```sh
# default VPC
VPC_ID=$(aws ec2 describe-vpcs \
--output text \
--filters Name=isDefault,Values=true \
--query 'Vpcs[0].VpcId')

# by name
VPC_ID=$(aws ec2 describe-vpcs \
--output text \
--filters Name=tag:Name,Values="My Named VPC" \
--query 'Vpcs[0].VpcId')

# manually specify ID
VPC_ID=vpc-1a2b3c4d
```
### Create security groups

This allows TCP ingress on MySQL port 3306 from specific IPs using CIDR notation.

##### Allow access from specific IPs
```sh
SECURITY_GROUP_NAME=rds-mysql
IPS="10.35.19.31/32 10.88.52.130/32 10.26.47.1/32 10.24.172.83/32"
aws ec2 create-security-group \
--group-name $SECURITY_GROUP_NAME \
--description "Allow ingress on 3306 for MySQL" \
--vpc-id=$VPC_ID
for IP in $IPS
do
   aws ec2 authorize-security-group-ingress \
   --group-name $SECURITY_GROUP_NAME \
   --protocol tcp \
   --cidr $IP \
   --port 3306
done
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
--output text \
--filters Name=group-name,Values="$SECURITY_GROUP_NAME" \
--query 'SecurityGroups[0].GroupId')
```

##### Allow access from local IP
```sh
SECURITY_GROUP_NAME=rds-mysql-local
CIDR=$(curl -s ifconfig.co)/32
aws ec2 create-security-group \
--group-name $SECURITY_GROUP_NAME \
--description "Allow ingress on 3306 for MySQL from local IP" \
--vpc-id=$VPC_ID
aws ec2 authorize-security-group-ingress \
--group-name $SECURITY_GROUP_NAME \
--protocol tcp \
--cidr $CIDR \
--port 3306
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
--output text \
--filters Name=group-name,Values="$SECURITY_GROUP_NAME" \
--query 'SecurityGroups[0].GroupId')
```

##### Allow access from anywhere*

> *Not recommended in production.  Use only for testing.
 
```sh
SECURITY_GROUP_NAME=rds-mysql-anywhere
CIDR=0.0.0.0/0
aws ec2 create-security-group \
--group-name $SECURITY_GROUP_NAME \
--description "Allow ingress on 3306 for MySQL from anywhere" \
--vpc-id=$VPC_ID
aws ec2 authorize-security-group-ingress \
--group-id $SECURITY_GROUP_ID \
--protocol tcp \
--cidr $CIDR \
--port 3306
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
--output text \
--filters Name=group-name,Values="$SECURITY_GROUP_NAME" \
--query 'SecurityGroups[0].GroupId')
```

### Create custom parameter group

It is a requirement for Cloud SQL to have binary logging enabled on the master as well as setting the config `binlog_format=ROW`.  Enabling binary logging [impacts the master](https://cloud.google.com/sql/docs/mysql/replication/tips#bin-log-impact) by requiring an instance restart.  Existing database connections are lost and must be reestablished.  To avoid instance restart, you would create an RDS read-replica using the following parameter group.

```sh
DB_PARAMETER_GROUP=custom-mysql5-6
aws rds create-db-parameter-group \
--db-parameter-group-name $DB_PARAMETER_GROUP \
--db-parameter-group-family MySQL5.6 \
--description "Parameter: binlog_format=ROW"
aws rds modify-db-parameter-group \
--db-parameter-group-name $DB_PARAMETER_GROUP \
--parameters "ParameterName=binlog_format,ParameterValue=ROW,ApplyMethod=immediate"
```

## RDS MySQL instance : testing

Follow these steps to create a test RDS instance as a *proof-of-concept*.  If you already have an RDS instance running, skip to [RDS MySQL instance : production](#rds-mysql-instance-:-production).

### Create MySQL DB instance
```sh
DB_INSTANCE_IDENTIFIER=mysql-instance1
DB_NAME=mytestdb
ENGINE=mysql
ENGINE_VERSION=5.6.36
AVAILABILITY_ZONE=us-east-1d
MASTER_USERNAME=root
MASTER_USER_PASSWORD=myrootpass
AVAILABILITY_ZONE=us-east-1a
DB_SUBNET_GROUP=default-vpc-1a2b3c4d
aws rds create-db-instance \
--db-instance-identifier $DB_INSTANCE_IDENTIFIER \
--db-instance-class db.t2.micro \
--storage-type gp2 \
--allocated-storage 20 \
--availability-zone $AVAILABILITY_ZONE \
--engine $ENGINE \
--db-name $DB_NAME \
--master-username $MASTER_USERNAME \
--master-user-password $MASTER_USER_PASSWORD \
--vpc-security-group-ids=$SECURITY_GROUP_ID \
--db-parameter-group-name $DB_PARAMETER_GROUP \
--db-subnet-group-name=$DB_SUBNET_GROUP
```

### Wait until instance is available
```sh
aws rds wait db-instance-available \
--db-instance-identifier $DB_INSTANCE_IDENTIFIER
```

### Insert test data into database
```sh
RDS_MASTER_HOSTNAME=$(aws rds describe-db-instances \
--db-instance-identifier $DB_INSTANCE_IDENTIFIER \
--output text \
--query DBInstances[0].Endpoint.Address)

# create table
curl -s "https://api.mockaroo.com/api/57b951e0?count=0&key=3666cca0" | mysql -h $RDS_MASTER_HOSTNAME -u $MASTER_USERNAME -p$MASTER_USER_PASSWORD $DB_NAME

# insert data
curl -s "https://api.mockaroo.com/api/1cf77ef0?count=1000&key=3666cca0" | mysql -h $RDS_MASTER_HOSTNAME -u $MASTER_USERNAME -p$MASTER_USER_PASSWORD $DB_NAME
```

## RDS MySQL instance : production

### Export data with mysqldump

See [Google Cloud SQL requirements](https://cloud.google.com/sql/docs/mysql/import-export/creating-sqldump-csv) for creating a SQL dump file.

> NOTE:  Using the `mysqldump --master-data` option is necessary to find the precise binlog coordinates where the backup begins.  This requires `SUPER` privileges which RDS does NOT allow.  See [https://stackoverflow.com/a/20645291/9370950](https://stackoverflow.com/a/20645291/9370950)
> 
> The workaround is to:
> 
1. Create an RDS read-replica of the RDS master
2. Stop replication on the RDS read-replica
3. Note the replica's binlog coordinates
4. Create logical backup using `mysqldump` on the RDS read-replica
5. Inject the binlog coordinates into the backup file

### Create RDS read-replica
```sh
DB_INSTANCE_IDENTIFIER=mysql-instance1
REPLICA_INSTANCE_IDENTIFIER="${DB_INSTANCE_IDENTIFIER}-replica"
aws rds create-db-instance-read-replica \
--db-instance-identifier $REPLICA_INSTANCE_IDENTIFIER \
--source-db-instance-identifier $DB_INSTANCE_IDENTIFIER
```

### Wait until instance is available
```sh
aws rds wait db-instance-available \
--db-instance-identifier $REPLICA_INSTANCE_IDENTIFIER
aws rds describe-db-instances \
--db-instance-identifier $REPLICA_INSTANCE_IDENTIFIER \
--output text \
--query DBInstances[0].StatusInfos
```

### Stop replication
```sh
MASTER_USERNAME=root
MASTER_USER_PASSWORD=myrootpass
RDS_REPLICA_HOSTNAME=$(aws rds describe-db-instances \
--db-instance-identifier $REPLICA_INSTANCE_IDENTIFIER \
--output text \
--query DBInstances[0].Endpoint.Address)
mysql -h $RDS_REPLICA_HOSTNAME -u $MASTER_USERNAME -p$MASTER_USER_PASSWORD -e "CALL mysql.rds_stop_replication;"
```

### Note the master coordinates of the binlog

On the read-replica, run `SHOW SLAVE STATUS` to view the master coordinates, noting the following values:

- `Exec_Master_Log_Pos`
- `Relay_Master_Log_File`

```sh
EXEC_MASTER_LOG_POS=$(mysql -h $RDS_REPLICA_HOSTNAME -u $MASTER_USERNAME -p$MASTER_USER_PASSWORD -e "SHOW SLAVE STATUS\G" | grep "Exec_Master_Log_Pos" | awk '{ print $2 }')
RELAY_MASTER_LOG_FILE=$(mysql -h $RDS_REPLICA_HOSTNAME -u $MASTER_USERNAME -p$MASTER_USER_PASSWORD -e "SHOW SLAVE STATUS\G" | grep "Relay_Master_Log_File" | awk '{ print $2 }')
```

### Create backup of the RDS read-replica
```sh
BACKUP_FILE=rds_backup.sql
DB_NAME=myproddb
mysqldump --databases $DB_NAME -h $RDS_REPLICA_HOSTNAME -u $MASTER_USERNAME -p$MASTER_USER_PASSWORD \
--flush-privileges \
--hex-blob \
--skip-triggers \
--default-character-set=utf8 \
--order-by-primary \
--single-transaction > $BACKUP_FILE
```

### Add binlog coordinates to backup file
```sh
echo "\n\n-- Position to start replication or point-in-time recovery from\nCHANGE MASTER TO MASTER_LOG_FILE='$RELAY_MASTER_LOG_FILE', MASTER_LOG_POS=$EXEC_MASTER_LOG_POS;" >> $BACKUP_FILE
```

### Add RDS specific tables to backup file

Add the following to the backup file

```sh
-- RDS tables

CREATE TABLE `rds_configuration` (  
  `name` varchar(100) NOT NULL,
  `value` varchar(100) DEFAULT NULL,
  `description` varchar(300) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1

CREATE TABLE `rds_global_status_history` (  
  `collection_end` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `collection_start` timestamp NULL DEFAULT NULL,
  `variable_name` varchar(64) NOT NULL,
  `variable_value` varchar(1024) NOT NULL,
  `variable_delta` int(20) NOT NULL,
  PRIMARY KEY (`collection_end`,`variable_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

 CREATE TABLE `rds_global_status_history_old` (
  `collection_end` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `collection_start` timestamp NULL DEFAULT NULL,
  `variable_name` varchar(64) NOT NULL,
  `variable_value` varchar(1024) NOT NULL,
  `variable_delta` int(20) NOT NULL,
  PRIMARY KEY (`collection_end`,`variable_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

 CREATE TABLE `rds_heartbeat2` (
  `id` int(11) NOT NULL,
  `value` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `rds_history` (  
  `action_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `called_by_user` varchar(50) NOT NULL,
  `action` varchar(20) NOT NULL,
  `mysql_version` varchar(50) NOT NULL,
  `master_host` varchar(255) DEFAULT NULL,
  `master_port` int(11) DEFAULT NULL,
  `master_user` varchar(16) DEFAULT NULL,
  `master_log_file` varchar(50) DEFAULT NULL,
  `master_log_pos` mediumtext,
  `master_ssl` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `rds_replication_status` (  
  `action_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `called_by_user` varchar(50) NOT NULL,
  `action` varchar(20) NOT NULL,
  `mysql_version` varchar(50) NOT NULL,
  `master_host` varchar(255) DEFAULT NULL,
  `master_port` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `rds_sysinfo` (  
  `name` varchar(25) DEFAULT NULL,
  `value` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `host` (  
  `Host` char(60) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Db` char(64) COLLATE utf8_bin NOT NULL DEFAULT '',
  `Select_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Insert_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Update_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Delete_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Drop_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Grant_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `References_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Index_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Alter_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_tmp_table_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Lock_tables_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_view_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Show_view_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Create_routine_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Alter_routine_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Execute_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  `Trigger_priv` enum('N','Y') CHARACTER SET utf8 NOT NULL DEFAULT 'N',
  PRIMARY KEY (`Host`,`Db`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Host privileges;  Merged with database privileges';
```

### Create replication user on RDS master

Normally in production, you would limit the replication user to be from the read-replica (slave) machine. For example, `'$REPLICATION_USER'@'my-read-replica.gcp.googlehost.com'`.  Since the read-replica hasn't been created and the host address is unknown at this point, temporarily allow the replication user from anywhere.  Alternatively you could [reserve a static external IP address](https://cloud.google.com/compute/docs/ip-addresses/reserve-static-external-ip-address) within the Google Cloud console and then attach it to the read-replica instance after creation.

```sh
REPLICATION_USER='repl'
REPLICATION_USER_PASSWORD='slavepass'
mysql -h $RDS_MASTER_HOSTNAME -u $MASTER_USERNAME -p$MASTER_USER_PASSWORD -e "CREATE USER '$REPLICATION_USER' IDENTIFIED BY '$REPLICATION_USER_PASSWORD'; GRANT REPLICATION SLAVE ON *.* TO '$REPLICATION_USER'@'%';"
```

## Configure Google Cloud SQL External Master

This follows [Google's guidelines](https://cloud.google.com/sql/docs/mysql/replication/configure-external-master) on how to configure an external master.

### Google Cloud credentials

##### Create Google Cloud service account
```sh
PROJECT_NAME=gcp-project
PROJECT_ID=gcp-project-id
SERVICE_ACCOUNT_NAME=default
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME
gcloud projects add-iam-policy-binding $PROJECT_ID --member "serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"  --role "roles/owner"
gcloud iam service-accounts keys create ~/.google-cloud-credentials.json --iam-account $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com
```

##### Set environment variable
```sh
export GOOGLE_APPLICATION_CREDENTIALS=~/.google-cloud-credentials.json
```

##### (Optional) Add to bash profile
```sh
echo -e "\n# Google Cloud\nexport GOOGLE_APPLICATION_CREDENTIALS=~/.google-cloud-credentials.json\n" >> ~/.bash_profile
```

### Create Cloud Storage bucket

This bucket will be used to store the `mysqldump` backup file.

```sh
STORAGE_CLASS=regional
BUCKET_LOCATION=us-east1
BUCKET_NAME=my-gcp-bucket
gsutil mb -p $PROJECT_NAME \
-c $STORAGE_CLASS \
-l $BUCKET_LOCATION gs://$BUCKET_NAME/
```

### Upload mysqldump file
```sh
BUCKET_PATH=cloudsql/mysqldump/$DB_INSTANCE_IDENTIFIER
gsutil cp $BACKUP_FILE gs://$BUCKET_NAME/$BUCKET_PATH/
```

### Create internal master instance

The internal master instance (Cloud SQL virtual IP address) and the external master instance (AWS RDS IP address) together make up the master instance for the Cloud SQL replica.  See [external master configuration](https://cloud.google.com/sql/docs/mysql/replication/tips#external-master) for more details.

```sh
INTERNAL_MASTER_INSTANCE_NAME=$DB_INSTANCE_IDENTIFIER
RDS_MASTER_IP=$(resolveip -s $RDS_MASTER_HOSTNAME)
REGION_NAME=us-east1
EXTERNAL_MASTER_DATABASE_VERSION=MYSQL_5_6
PORT=3306
ACCESS_TOKEN="$(gcloud auth application-default print-access-token)"

# Internal master
curl --header "Authorization: Bearer ${ACCESS_TOKEN}" --header 'Content-Type: application/json' \
--data '{"name": "'"$INTERNAL_MASTER_INSTANCE_NAME"'", "region": "'"$REGION_NAME"'", "databaseVersion": "'"$EXTERNAL_MASTER_DATABASE_VERSION"'", "onPremisesConfiguration": {"hostPort": "'"$RDS_MASTER_IP:$PORT"'"}}' \
-X POST https://www.googleapis.com/sql/v1beta4/projects/$PROJECT_ID/instances
```

### Create replica instance

Cloud SQL First generation instance

```sh
REPLICA_NAME=$REPLICA_INSTANCE_IDENTIFIER
TIER=D4

# Replica
curl --header "Authorization: Bearer ${ACCESS_TOKEN}" --header 'Content-Type: application/json' \
--data '{"replicaConfiguration": {"mysqlReplicaConfiguration": {"username": "'"$REPLICATION_USER"'", "password": "'"$REPLICATION_USER_PASSWORD"'", "dumpFilePath": "'"gs://$BUCKET_NAME/$BUCKET_PATH/$BACKUP_FILE"'"}}, "settings": {"tier": "'"$TIER"'","activationPolicy": "ALWAYS"}, "databaseVersion": "'"$EXTERNAL_MASTER_DATABASE_VERSION"'", "masterInstanceName": "'"$INTERNAL_MASTER_INSTANCE_NAME"'", "name": "'"$REPLICA_NAME"'", "region": "'"$REGION_NAME"'"}' \
-X POST https://www.googleapis.com/sql/v1beta4/projects/$PROJECT_ID/instances
```

### Wait until instance is available
```sh
# Wait for CREATE operation
OPERATION_ID=$(gcloud sql operations list --instance=$REPLICA_NAME --filter=operationType:"CREATE" --format="value(name)")
gcloud sql operations wait $OPERATION_ID

# Wait for all operations
gcloud sql operations wait $(gcloud sql operations list --instance=$REPLICA_NAME --uri)
```

### Patch replica

Assign IPv4 address, change to synchronous replication, and add CIDR ingress network (IP address of RDS master), then restart

```sh
gcloud sql instances patch $REPLICA_NAME \
--assign-ip \
--replication=SYNCHRONOUS \
--authorized-networks=$RDS_MASTER_IP/32
gcloud sql instances restart $REPLICA_NAME
```

You should now limit the replication user on the RDS master to be from the read-replica (slave) machine. 

```sh
GCP_REPLICA_IP=$(gcloud sql instances describe $REPLICA_NAME --format=json | jq -r '.ipAddresses[0].ipAddress')
mysql -h $RDS_MASTER_HOSTNAME -u $MASTER_USERNAME -p$MASTER_USER_PASSWORD -e "RENAME USER '$REPLICATION_USER'@'%' TO '$REPLICATION_USER'@'$GCP_REPLICA_IP';"
```

### Check replication status
```sh
gcloud sql instances describe $REPLICA_NAME 
gcloud sql instances describe $INTERNAL_MASTER_INSTANCE_NAME
```

### Accessing the read-replica

Cloud SQL prevents creating users on read-replicas.  Creating a user on the external master propagates down to the replica, allowing access to the read-replica.

```sh
REPLICA_USER=myreplica
REPLICA_PASSWORD=myreplicapass
mysql -h $RDS_MASTER_HOSTNAME -u $MASTER_USERNAME -p$MASTER_USER_PASSWORD -e "CREATE USER '$REPLICA_USER' IDENTIFIED BY '$REPLICA_PASSWORD'; GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$REPLICA_USER'@'%';"
```

### Configure SSL
Configure SSL for the connections from Cloud SQL to external masters.  See:  [https://cloud.google.com/sql/docs/mysql/configure-ssl-instance](https://cloud.google.com/sql/docs/mysql/configure-ssl-instance)


## Next steps for full migration to GCP

The following describe the steps to take to fully migrate off AWS and onto GCP

#### 1. Stop AWS RDS read/write services

#### 2. Promote the Cloud SQL replica
Promoting a replica to a stand-alone Cloud SQL instance is an irreversible action. Once promoted, an instance cannot be converted back to a read-replica.

#### 3. (Optional) Migrate and Upgrade Google Cloud SQL
 Migrating to a Google Cloud SQL Second Generation instance offers higher performance and storage capacity at a lower cost.  Additionally upgrade the version of MySQL to 5.6 or 5.7 all in the same migration step.

#### 4. Point read/write applications to the GCP Cloud SQL instance and start services
