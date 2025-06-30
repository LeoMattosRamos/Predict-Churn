SELECT 
    A.idCustomer,
    SUM(CASE WHEN B.NameProduct = 'ChatMessage' THEN A.pointsTransaction ELSE 0 END)*1.0/SUM(A.pointsTransaction) AS ChatMessage,
    SUM(CASE WHEN B.NameProduct = 'Resgatar Ponei' THEN A.pointsTransaction ELSE 0 END) AS Resgatar_Ponei,
    SUM(CASE WHEN B.NameProduct = 'Lista de presença' THEN A.pointsTransaction ELSE 0 END) AS Lista_de_presenca,
    SUM(CASE WHEN B.NameProduct = 'Presença Streak' THEN A.pointsTransaction ELSE 0 END) AS Presenca_Streak,
    SUM(A.pointsTransaction) AS Total
FROM transactions A
LEFT JOIN transactions_product B
ON A.idTransaction = B.idTransaction
WHERE B.NameProduct IN ('ChatMessage','Resgatar Ponei','Lista de presença','Presença Streak')
GROUP BY 1




