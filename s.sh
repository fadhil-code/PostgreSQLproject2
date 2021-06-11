#!/bin/bash
# Allow traffic on port 5432
iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
iptables -A INPUT -p tcp --sport 5432 -j ACCEPT
iptables -A OUTPUT -p tcp --sport 5432 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 5432 -j ACCEPT
# Installing Postgres files...
apt-get update
apt-get install -y curl gnupg2
echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" >> /etc/apt/sources.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt-get update
apt-get install -y postgresql
service postgresql stop #postgresql stop
sed -i "s/#listen_addresses = 'localhost'/ listen_addresses = '*'/" /etc/postgresql/12/main/postgresql.conf
rm -R /var/lib/postgresql/12/main/ #Delete data from PostgreSQL
su - postgres -c "pg_basebackup -P -R -X stream -c fast -h 192.168.0.2 -U replicacant -D /var/lib/postgresql/12/main/"
# Create recovery.conf file
echo " standby_mode = 'on'" | tee -a /var/lib/postgresql/12/main/recovery.conf
echo "primary_conninfo = 'user=replicant password=123456 host=192.168.0.2 port=5432 sslmode=prefer sslcompression=0 krbsrvname=postgres target_session_attrs=any'" | tee -a /var/lib/postgresql/12/main/recovery.conf
echo "trigger_file = '/tmp/to_master'" | tee -a /var/lib/postgresql/12/main/recovery.conf
sed  -i '/host    replication/d' /etc/postgresql/12/main/pg_hba.conf # Edit the pg_hba.conf file
echo "host    replication     replica             192.168.0.1/24                 md5" | tee -a /etc/postgresql/12/main/pg_hba.conf
service postgresql start
