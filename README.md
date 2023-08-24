
## Respuestas

1. Escriba el código de SQL que le permite conocer el monto y la cantidad de las transacciones que SIMETRIK considera como conciliables para la base de CLAP

_

    SELECT
        COUNT(*) AS CANTIDAD_CONCILIABLES,
        SUM(MONTO) AS MONTO_CONCILIABLES
    FROM (
        SELECT
            CODIGO_AUTORIZACION,
            MONTO,
            ROW_NUMBER() OVER (PARTITION BY CODIGO_AUTORIZACION ORDER BY FECHA_TRANSACCION DESC) AS RN
        FROM CLAP
        WHERE TIPO_TRX = 'PAGADA'
    ) AS CONCILIABLES
    WHERE RN = 1;


Resultado de query: 
- cantidad: 116225
- monto: 49081658.54


2. Escriba el código de SQL que le permite conocer el monto y la cantidad de las transacciones que SIMETRIK considera como conciliables para la base de BANSUR

_

    SELECT
        COUNT(*) AS CANTIDAD_CONCILIABLES,
        SUM(MONTO) AS MONTO_CONCILIABLES
    FROM BANSUR
    WHERE TIPO_TRX = 'PAGO';


Resultado de query:
- cantidad: 132338
- monto: 54053911.94


3. ¿Cómo se comparan las cifras de los puntos anteriores respecto de las cifras totales en las fuentes desde un punto de vista del negocio?

Teniendo en cuenta que para CLAP :
- Cantidad total 163549 versus 116225 conciliable
- Monto total: 73736800.92 versus 49081658.54 conciliable

y que para BANSUR el total es :
- cantidad total: 132396 versus 132338 conciliable
- monto total: 53977030.03 versus 54053911.94 conciliable

Se percibe que hay un 30 % de transacciones de CLAP que "se pierden", y pocas son por estado cancelado, ya que lo que se ve reflejado en BANSUR es alto grado de conciabilidad, por lo que habría que ver en detalle para entender las anomalías
En segunda instancia se aprecia que el monto total de BANSUR es menor a su monto conciliable, por lo que puede haber error en los datos cargados.



4. Teniendo en cuenta los criterios de cruce entre ambas bases conciliables, escriba una sentencia de SQL que contenga la información de CLAP y BANSUR; agregue una columna en la que se evidencie si la transacción cruzó o no con su contrapartida y una columna en la que se inserte un ID autoincremental para el control de la conciliación

_

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

El resultado de la query está en el archivo docs/results_query_4.csv

5. Diseñe un código que calcule el porcentaje de transacciones de la base conciliable de CLAP cruzó contra la liquidación de BANSUR.

El código está en el archivo python/script_5.py : resultado es 52.93%

6. Diseñe un código que calcule el porcentaje de transacciones de la base conciliable de BANSUR no cruzó contra la liquidación de CLAP.

El código está en el archivo python/script_6.py : resultado es 47.07%