WITH transacoes AS (
SELECT 
    DATE('2024-07-04') AS Dt_ref,
    idCustomer,
    COUNT(idTransaction) AS Qtd_transacao_21,
    COUNT(CASE WHEN dtTransaction >=DATE('2024-07-04','-14 DAY')
        THEN idTransaction END) AS Qtd_transacao_14,
    COUNT(CASE WHEN dtTransaction >=DATE('2024-07-04','-7 DAY')
        THEN idTransaction END) AS Qtd_transacao_7,
    
    COUNT(DISTINCT(DATE(dtTransaction))) AS Qtd_dias_interacao_21,
    COUNT(DISTINCT CASE WHEN dtTransaction >=DATE('2024-07-04','-14 DAY')
        THEN DATE(dtTransaction) END) AS Qtd_dias_interacao_14,
    COUNT(DISTINCT CASE WHEN dtTransaction >=DATE('2024-07-04','-07 DAY')
        THEN DATE(dtTransaction) END) AS Qtd_dias_interacao_7

FROM transactions
WHERE dtTransaction < '2024-07-04'
AND dtTransaction >= DATE('2024-07-04','-21 DAY')
GROUP BY idCustomer
),

intervalo AS (

SELECT idCustomer, dtTransaction, idTransaction,
       ROW_NUMBER() OVER (PARTITION BY idCustomer, DATE(dtTransaction) ORDER BY DATE(dtTransaction) ASC) AS N_transacao_dia
FROM transactions

),

lag_data AS (

SELECT 
    idCustomer,
    dtTransaction,
    LAG(DATE(dtTransaction)) OVER (PARTITION BY idCustomer ORDER BY DATE(dtTransaction) ASC) AS Dt_anterior
FROM intervalo
WHERE N_transacao_dia = 1 
),

Media_transacao_dias AS (

SELECT *, ROUND(AVG(julianday(DATE(dtTransaction)) - julianday (Dt_anterior)),2) as intervalo_days_transactions

FROM lag_data
WHERE Dt_anterior IS NOT NULL
GROUP BY idCustomer
)

SELECT 
    A.Dt_ref,
    A.idCustomer,
    A.Qtd_transacao_21,
    A.Qtd_transacao_14,
    A.Qtd_transacao_7,
    A.Qtd_dias_interacao_21,
    A.Qtd_dias_interacao_14,
    A.Qtd_dias_interacao_7,
    B.intervalo_days_transactions

FROM transacoes A
LEFT JOIN Media_transacao_dias B
ON A.idCustomer = B.idCustomer
WHERE B.intervalo_days_transactions IS NOT NULL


