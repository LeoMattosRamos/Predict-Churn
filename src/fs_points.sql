SELECT 
    DATE('{date}') AS Dt_ref,
    idCustomer,
    SUM(CASE WHEN pointsTransaction > 0 THEN pointsTransaction ELSE 0 END) AS PontosAcum_21,
    SUM(CASE WHEN pointsTransaction > 0
    AND dtTransaction >= DATE('{date}','-14 DAY')
     THEN pointsTransaction ELSE 0 END) AS PontosAcum_14,
    SUM(CASE WHEN pointsTransaction > 0
    AND dtTransaction >= DATE('{date}','-7 DAY')
     THEN pointsTransaction ELSE 0 END) AS PontosAcum_7,

    SUM(CASE WHEN pointsTransaction < 0 THEN pointsTransaction ELSE 0 END) AS PontosResg_21,
    SUM(CASE WHEN pointsTransaction < 0
    AND dtTransaction >= DATE('{date}','-14 DAY')
     THEN pointsTransaction ELSE 0 END) AS PontosResg_14,
    SUM(CASE WHEN pointsTransaction < 0
    AND dtTransaction >= DATE('{date}','-7 DAY')
     THEN pointsTransaction ELSE 0 END) AS PontosResg_7


FROM transactions
WHERE dtTransaction < '{date}'
AND dtTransaction >= DATE('{date}','-21 DAY')
GROUP BY 2