
SELECT 
    A.Dt_ref,
    A.idCustomer,
    CASE WHEN B.Dt_ref IS NOT NULL THEN 0 ELSE 1 END AS flag_churn

FROM fs_geral A

LEFT JOIN fs_geral B
ON A.idCustomer = B.idCustomer
AND A.Dt_ref = DATE(B.Dt_ref, "-21 DAY")

WHERE A.Dt_ref < DATE("2024-06-01","-21 DAY") /* Garantir base maturada (data mais recente -21 dias)*/
AND strftime("%d", A.Dt_ref) = '01' /* Diminuir viés de usuários com muita interação - considearar as features 1 vez no mês para cada usuário - considera apenas dia 01 de cada mês)