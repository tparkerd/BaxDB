FROM postgres:9.6

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y make postgresql-contrib-9.6 postgresql-server-dev-9.6 libpq-dev gcc sudo
RUN mkdir /app
ADD ./gwas_database /app
WORKDIR /app

# Install extentions into PostgreSQL
# Verify that pg_config is accessible to the user
RUN command -v pg_config > /dev/null 2>&1 || { printf "Command 'pg_config' is required but not found in path. Make sure PostgreSQL client tools are installed. Aborting.\n" 1>&2; exit 1; }

# Compile TINYINT extention and install it into PostgreSQL
ENV PG_INSTALLDIR /usr/lib/postgresql/9.6/lib/baxdb
RUN mkdir -p -m 755 "$PG_INSTALLDIR" || { printf "Unable to create directory '$PG_INSTALLDIR' for installation into PostgreSQL. Aborting.\n" 1>&2; exit 1; }

# Copy the postgres headers into common include directory
RUN cp -r /usr/include/postgresql/9.6/server/* /usr/local/include

WORKDIR /app/c 
RUN make 
RUN cp array_multi_index.so imputed_genotype.so summarize_variant.so "$PG_INSTALLDIR" 
RUN chmod -R 755 "$PG_INSTALLDIR" 

WORKDIR /app/lib/tinyint-0.1.1
RUN make
RUN sed -i -e '1i\\\connect baxdb' -e 's|$libdir\/tinyint|$libdir/baxdb/tinyint|g' tinyint.sql
RUN cp tinyint.so "$PG_INSTALLDIR"
RUN chmod -R 755 "$PG_INSTALLDIR"
RUN cp tinyint.sql "$PG_INSTALLDIR" # move the tinyint.sql into a location accessible by postgres user

WORKDIR /app/ddl
# Move the remaining SQL scripts to a location accessible by postgres user
# RUN cp  createtables.sql updatepermissions.sql "$PG_INSTALLDIR"

COPY ./ddl/setup.sql /docker-entrypoint-initdb.d/10-setup.sql
COPY ./lib/tinyint-0.1.1/tinyint.sql /docker-entrypoint-initdb.d/20-tinyint.sql
COPY ./createtables.sql /docker-entrypoint-initdb.d/30-createtables.sql
COPY ./ddl/updatepermissions.sql /docker-entrypoint-initdb.d/40-updatepermissions.sql

USER postgres

# # Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# # Set the default command to run when starting the container
# CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]