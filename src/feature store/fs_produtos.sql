SELECT 
    DATE('2024-07-04') AS Dt_ref,
    A.idCustomer,
    ROUND(SUM(CASE WHEN B.NameProduct = 'ChatMessage' THEN A.pointsTransaction ELSE 0 END)*1.0/SUM(A.pointsTransaction),2) AS ChatMessage,
    ROUND(SUM(CASE WHEN B.NameProduct = 'Resgatar Ponei' THEN A.pointsTransaction ELSE 0 END)*1.0/SUM(A.pointsTransaction),2)  AS Resgatar_Ponei,
    ROUND(SUM(CASE WHEN B.NameProduct = 'Lista de presença' THEN A.pointsTransaction ELSE 0 END)*1.0/SUM(A.pointsTransaction),2)  AS Lista_de_presenca,
    ROUND(SUM(CASE WHEN B.NameProduct = 'Presença Streak' THEN A.pointsTransaction ELSE 0 END)*1.0/SUM(A.pointsTransaction),2)  AS Presenca_Streak,
    ROUND(SUM(CASE WHEN B.NameProduct = 'ChatMessage' THEN A.pointsTransaction ELSE 0 END)*1.0/COUNT(DISTINCT(DATE(A.dtTransaction))),2) AS Chatmessage_per_live
FROM transactions A
LEFT JOIN transactions_product B
ON A.idTransaction = B.idTransaction
WHERE B.NameProduct IN ('ChatMessage','Resgatar Ponei','Lista de presença','Presença Streak')
      AND dtTransaction >= DATE('2024-07-04','-21 DAY')
      AND dtTransaction < '2024-07-04'
    
GROUP BY 2



