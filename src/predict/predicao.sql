with tb_churn AS (


SELECT 
    Dt_ref,
    idCustomer
FROM fs_geral 
WHERE Dt_ref = (SELECT MAX(Dt_ref) FROM fs_geral)

)
SELECT 
    A.*,
    B.Recencia_21,
    B.Frequencia_21,
    B.Pontos_21,
    B.idade_base,
    B.avg_transact_day,
    B.avg_points_day,
    C.PontosAcum_21,
    C.PontosAcum_14,
    C.PontosAcum_7,
    C.PontosResg_21,
    C.PontosResg_14,
    C.PontosResg_7,
    D.ChatMessage,
    D.Resgatar_Ponei,
    D.Lista,
    D.Presenca_Streak,
    D.Chatmessage_per_live,
    E.Qtd_transacao_21,
    E.Qtd_transacao_14,
    E.Qtd_transacao_7,
    E.Qtd_dias_interacao_21,
    E.Qtd_dias_interacao_14,
    E.Qtd_dias_interacao_7,
    COALESCE(E.intervalo_days_transactions,-1) AS intervalo_days_transactions,
    CASE WHEN E.intervalo_days_transactions IS NULL THEN 0 ELSE 1 END AS Mais_de_uma_compra
    
FROM tb_churn A
LEFT JOIN fs_geral B
ON A.idCustomer = B.idCustomer
AND A.Dt_ref = B.Dt_ref
LEFT JOIN fs_points C
ON A.idCustomer = C.idCustomer
AND A.Dt_ref = C.Dt_ref
LEFT JOIN fs_produtos D
ON A.idCustomer = D.idCustomer
AND A.Dt_ref = D.Dt_ref
LEFT JOIN fs_transacoes E
ON A.idCustomer = E.idCustomer
AND A.Dt_ref = E.Dt_ref
GROUP BY A.Dt_ref,
      A.idCustomer

