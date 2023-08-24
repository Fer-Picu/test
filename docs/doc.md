# Requerimientos

- docker y docker compose https://docs.docker.com/engine/install/ubuntu/


## Levantar el proyecto
En la raiz del proyecto:
- docker compose up -d

## Para pasar guardar los csv en el docker container

- Entrar al container

        docker compose exec db bash

- Dentro del container:
  
        mkdir -p /opt/data_csv/

- fuera de el

        docker cp docs/CLAP.csv test-db-1:/opt/data_csv/
        docker cp docs/BANSUR.csv test-db-1:/opt/data_csv/

- Creación de tablas

        CREATE TABLE CLAP (
            INICIO6_TARJETA INT,
            FINAL4_TARJETA INT,
            TIPO_TRX VARCHAR(20),
            MONTO NUMERIC(10, 2),
            FECHA_TRANSACCION TIMESTAMP,
            CODIGO_AUTORIZACION VARCHAR(20),
            ID_BANCO BIGINT,
            FECHA_RECEPCION_BANCO DATE
        );

        CREATE TABLE BANSUR (
            TARJETA BIGINT,
            TIPO_TRX VARCHAR(20),
            MONTO NUMERIC(10, 2),
            FECHA_TRANSACCION DATE,
            CODIGO_AUTORIZACION INT,
            ID_ADQUIRIENTE BIGINT,
            FECHA_RECEPCION DATE
        );



- Script para cargar los csv


        COPY CLAP FROM '/opt/data_csv/CLAP.csv' DELIMITER ',' CSV HEADER;

        COPY BANSUR FROM '/opt/data_csv/BANSUR.csv' DELIMITER ',' CSV HEADER;


- Entrar al container

        docker compose exec script bash
- Dentro del container

        cd /opt/script && pip install -r requirements.txt
        python script_5.py
        python script_6.py


