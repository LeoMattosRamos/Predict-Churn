SELECT 
    DATE("{date}") AS Dt_ref,
    A.idCustomer,
    ROUND(SUM(CASE WHEN B.NameProduct LIKE '%ChatMessage%' THEN A.pointsTransaction ELSE 0 END)*1.0/SUM(A.pointsTransaction),2) AS ChatMessage,
    ROUND(SUM(CASE WHEN B.NameProduct LIKE '%Resgatar Ponei%' THEN A.pointsTransaction ELSE 0 END)*1.0/SUM(A.pointsTransaction),2)  AS Resgatar_Ponei,
    ROUND(SUM(CASE WHEN B.NameProduct LIKE '%Lista de presen%' THEN A.pointsTransaction ELSE 0 END)*1.0/SUM(A.pointsTransaction),2)  AS Lista,
    ROUND(SUM(CASE WHEN B.NameProduct LIKE '%Presença Streak%' THEN A.pointsTransaction ELSE 0 END)*1.0/SUM(A.pointsTransaction),2)  AS Presenca_Streak,
    ROUND(SUM(CASE WHEN B.NameProduct LIKE '%ChatMessage%' THEN A.pointsTransaction ELSE 0 END)*1.0/COUNT(DISTINCT(DATE(A.dtTransaction))),2) AS Chatmessage_per_live
FROM transactions A
LEFT JOIN transactions_product B
ON A.idTransaction = B.idTransaction
WHERE dtTransaction >= DATE("{date}",'-21 DAY')
      AND dtTransaction < "{date}"
      AND pointsTransaction >= 0
     
    
GROUP BY 2



