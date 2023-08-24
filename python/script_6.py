import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="db",
    database="TechTest",
    user="admin",
    password="admin"
)

sql_query = """
    WITH CLAP_ULTIMO_ESTADO_PAGADA AS (
        SELECT
            CODIGO_AUTORIZACION
        FROM (
            SELECT
                CODIGO_AUTORIZACION,
                TIPO_TRX,
                ROW_NUMBER() OVER (PARTITION BY CODIGO_AUTORIZACION ORDER BY FECHA_TRANSACCION DESC) AS RN
            FROM CLAP
        ) AS SUB
        WHERE RN = 1 AND TIPO_TRX = 'PAGADA'
    )
    SELECT
        ROW_NUMBER() OVER () AS CONCILIACION_ID,
        C.INICIO6_TARJETA::VARCHAR,
        C.FINAL4_TARJETA::VARCHAR,
        B.TARJETA AS BANSUR_TARJETA,
        C.TIPO_TRX AS CLAP_TIPO_TRX,
        B.TIPO_TRX AS BANSUR_TIPO_TRX,
        C.MONTO AS CLAP_MONTO,
        B.MONTO AS BANSUR_MONTO,
        C.FECHA_TRANSACCION AS CLAP_FECHA,
        B.FECHA_TRANSACCION AS BANSUR_FECHA,
        CASE
            WHEN B.CODIGO_AUTORIZACION IS NOT NULL AND U.CODIGO_AUTORIZACION IS NOT NULL THEN 'Cruzó'
            ELSE 'No Cruzó'
        END AS ESTADO_CONCILIACION
    FROM CLAP C
    LEFT JOIN BANSUR B
    ON C.CODIGO_AUTORIZACION = B.CODIGO_AUTORIZACION
      AND C.INICIO6_TARJETA::VARCHAR = LEFT(B.TARJETA::VARCHAR, 6)
      AND C.FINAL4_TARJETA::VARCHAR = RIGHT(B.TARJETA::VARCHAR, 4)
      AND ABS(C.MONTO - B.MONTO) <= 0.99
      AND C.FECHA_TRANSACCION::DATE = B.FECHA_TRANSACCION
    LEFT JOIN CLAP_ULTIMO_ESTADO_PAGADA U
    ON C.CODIGO_AUTORIZACION = U.CODIGO_AUTORIZACION;
"""
# todo: idealmente esto se 

# Lee los datos en un DataFrame de pandas
df = pd.read_sql(sql_query, conn)

# Calcula el número total de transacciones que no cruzaron (estado 'No Cruzó')
total_no_cruzaron = len(df[df['estado_conciliacion'] == 'No Cruzó'])

# Calcula el número total de transacciones
total_transacciones = len(df)

# Calcula el porcentaje de transacciones de BANSUR que no cruzaron contra CLAP
porcentaje_no_cruzado = (total_no_cruzaron / total_transacciones) * 100

print(f"Porcentaje de transacciones de BANSUR que no cruzaron contra CLAP: {porcentaje_no_cruzado:.2f}%")

# Cierra la conexión
conn.close()
