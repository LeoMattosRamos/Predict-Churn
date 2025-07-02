WITH Geral AS (
    
    SELECT A.idCustomer,
       MAX(julianday('{date}') - julianday(DATE(dtTransaction))) AS idade_base,
       B.flEmail,
       COUNT(A.idTransaction)/COUNT(DISTINCT(DATE(A.dtTransaction))) AS avg_transact_day,
       SUM(CASE WHEN A.pointsTransaction > 0 THEN A.pointsTransaction ELSE 0 END) * 1.0
       / COUNT(DISTINCT(DATE(A.dtTransaction))) AS avg_points_day
FROM transactions A
LEFT JOIN customers B
ON A.idCustomer = B.idCustomer
GROUP BY A.idCustomer 
),

Base_ativa AS (
    SELECT idCustomer,
    MIN(julianday('{date}') - julianday(DATE(dtTransaction))) AS Recencia_21,
    COUNT(DISTINCT(DATE(dtTransaction))) AS Frequencia_21,
    SUM(CASE WHEN pointsTransaction > 0 THEN pointsTransaction ELSE 0 END) as Pontos_21
    FROM transactions
    WHERE dtTransaction < '{date}'
    AND dtTransaction >= DATE('{date}','-21 DAY')
    GROUP BY idCustomer
)

SELECT DATE('{date}') AS Dt_ref,
    A.idCustomer, 
    A.Recencia_21,
    A.Frequencia_21,
    A.Pontos_21,
    B.idade_base,
    B.avg_transact_day,
    B.avg_points_day
FROM Base_ativa A
LEFT JOIN Geral B
ON A.idCustomer = B.idCustomer



