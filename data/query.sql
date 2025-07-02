with tb_churn AS (

SELECT 
    A.Dt_ref,
    A.idCustomer,
    CASE WHEN B.Dt_ref IS NOT NULL THEN 0 ELSE 1 END AS flag_churn

FROM fs_geral A

LEFT JOIN fs_geral B
ON A.idCustomer = B.idCustomer
AND A.Dt_ref = DATE(B.Dt_ref, "-21 DAY")

WHERE A.Dt_ref < DATE("2024-06-01","-21 DAY") /* Garantir base maturada (data mais recente -21 dias)*/
AND strftime("%d", A.Dt_ref) = '01' /* Diminuir viés de usuários com muita interação - considearar as features 1 vez no mês para cada usuário - considera apenas dia 01 de cada mês)*/
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
    E.intervalo_days_transactions

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





