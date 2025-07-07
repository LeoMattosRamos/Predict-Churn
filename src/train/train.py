#%%

import mlflow.sklearn
import pandas as pd
import sqlalchemy
from sklearn import model_selection
from sklearn import metrics
from sklearn import pipeline
from sklearn import ensemble
from sklearn import tree
import scikitplot as skplt
import mlflow



CREATE_ENGINE = sqlalchemy.create_engine("sqlite:///../../data/feature_store.db")

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment (experiment_id="113942948431477804")

def import_query(path):
    with open(path, "r") as open_file:
         return(open_file.read())
    

query = import_query("../train/ABT.sql")


df = pd.read_sql(query, CREATE_ENGINE)
df.sort_values(by = "Dt_ref", ascending=False)


# %%

# Sample

df_oot = df[df['Dt_ref']==df['Dt_ref'].max()] # Base out of time
df_train = df[df['Dt_ref']<df['Dt_ref'].max()] # Separando base modelo da base out of time

y = 'flag_churn'
X = df_train.columns[3:]



X_train, X_test, y_train, y_test = model_selection.train_test_split(df_train[X], df_train[y],
                                                                    train_size= 0.8,
                                                                    random_state=42,
                                                                    stratify=df_train[y])
                                                                

# Explore
X_train_tmp = X_train.copy()

X_train_tmp['flag'] = y_train

X_analise = X_train_tmp.groupby(by="flag").agg(["mean"]).T


X_analise['diff'] = X_analise[0] - X_analise[1]
X_analise['diff_%'] = X_analise[0] / X_analise[1]

X_analise.sort_values("diff_%", ascending=False)

# Modify/Model

model = ensemble.RandomForestClassifier(random_state=42)

params = {"model__min_samples_leaf":[10,20,30,40,50,100,200],
          "model__max_depth": [2,4,5,6,8,10,15,20],
          "model__criterion": ["gini", "entropy"],
          "model__n_estimators": [10,20,50,100,200,300]
          }


model_pipeline = pipeline.Pipeline(
     steps=[
          ('model', model)
     ]
)
                                
grid = model_selection.GridSearchCV(model_pipeline,
                                    param_grid=params,
                                    cv=3,
                                    n_jobs= 8,
                                    scoring='recall')

## Métrica escolhida foi recall, pois para esse problema de negócio, queremos captar a maior quantidade de clientes com previsão de churn.

mlflow.sklearn.autolog()
with mlflow.start_run():

    

     grid.fit(X_train, y_train)

     best_model = grid.best_estimator_

     y_pred_train = grid.predict(X_train)
     y_pred_test = grid.predict(X_test)
     y_predict_proba = grid.predict_proba(X_test)[:,1]
     y_pred_proba_oot = grid.predict_proba(df_oot[df_oot.columns[3:]])[:,1]
     y_pred_oot = grid.predict(df_oot[df_oot.columns[3:]])

     acc_treino = metrics.accuracy_score(y_train, y_pred_train)
     acc_test = metrics.accuracy_score(y_test, y_pred_test)
     acc_oot = metrics.accuracy_score(df_oot[y],y_pred_oot )
     precision_test = metrics.precision_score(y_test, y_pred_test)
     precision_oot = metrics.precision_score(df_oot[y], y_pred_oot)
     roc = metrics.roc_auc_score(y_test, y_predict_proba)
     roc_oot = metrics.roc_auc_score(df_oot[y], y_pred_proba_oot)
     recall_teste = metrics.recall_score(y_test, y_pred_test)
     recall_oot = metrics.recall_score(df_oot[y],y_pred_oot )

     mlflow.log_metrics(
          {"acc_treino": acc_treino,
           "acc_teste": acc_test,
           "acc_oot": acc_oot,
           "precision_test": precision_test,
           "precision_oot": precision_oot,
           "recall_teste": recall_teste,
           "recall_oot": recall_oot}
     )

print(f"acc_treino: {acc_treino}")
print(f"acc_test: {acc_test}")
print(f"roc: {roc}")
print(f"recall: {recall_teste}")
print(f"precision_teste: {precision_test}")
print(f"roc_oot: {roc_oot}")
print(f"acc_oot: {acc_oot}")
print(f"recall_oot: {recall_oot}")
print(f"precision_oot: {precision_oot}")


confusion_matrix_teste = skplt.metrics.plot_confusion_matrix(y_test, y_pred_test)

confusion_matrix_oot = skplt.metrics.plot_confusion_matrix(df_oot[y], y_pred_oot)

#%%
y_pred_proba_oot_ = grid.predict_proba(df_oot[df_oot.columns[3:]])
y_predict_proba_ = grid.predict_proba(X_test)
ROC = skplt.metrics.plot_ks_statistic(df_oot[y],y_pred_proba_oot_ )
lift = skplt.metrics.plot_lift_curve(df_oot[y],y_pred_proba_oot_ )
cumulative_gain = skplt.metrics.plot_cumulative_gain(df_oot[y],y_pred_proba_oot_)
ks = skplt.metrics.plot_ks_statistic(y_test, y_predict_proba_)

#%%

import numpy as np

## Teste de alteração de threshold com base em F1 para verificar performance

y_predict_proba_treino = grid.predict_proba(X_train)[:,1]

precision, recall, thresholds = metrics.precision_recall_curve(y_test, y_predict_proba)

f1_scores = 2 * (precision * recall) / (precision + recall)

optimal_f1_idx = np.argmax(f1_scores)
optimal_thresh_f1 = thresholds[optimal_f1_idx]


#testando novas classificacoes com o novo threshold:

y_pred_ajusted_test = (y_predict_proba >= optimal_thresh_f1).astype(int) 
y_pred_ajusted_oot = (y_pred_proba_oot>= optimal_thresh_f1).astype(int)
y_pred_ajusted_treino = (y_predict_proba_treino >= optimal_thresh_f1).astype(int)

Acc_ajusted_teste = metrics.accuracy_score(y_test, y_pred_ajusted_test)
Acc_ajusted_treino = metrics.accuracy_score(y_train, y_pred_ajusted_treino)
Acc_ajusted_oot = metrics.accuracy_score(df_oot[y], y_pred_ajusted_oot)
Precision_ajusted_teste = metrics.precision_score(y_test, y_pred_ajusted_test)
Precision_ajusted_oot = metrics.precision_score(df_oot[y],y_pred_ajusted_oot)
Precision_ajusted_treino = metrics.precision_score(y_train, y_pred_ajusted_treino)
Recall_ajusted_teste = metrics.recall_score(y_test, y_pred_ajusted_test)
Recall_ajusted_oot = metrics.recall_score(df_oot[y], y_pred_ajusted_oot)


print(f"acc_treino: {acc_treino}")
print(f"acc_justado_treino:{Acc_ajusted_treino}")
print(f"precision_ajustado_treino:{Precision_ajusted_treino}")


print(f"acc_test: {acc_test}")
print(f"acc_ajustado_teste:{Acc_ajusted_teste}")
print(f"recall_teste: {recall_teste}")
print(f"recall_ajustado: {Recall_ajusted_teste}")
print(f"precisao_teste: {precision_test}")
print(f"precision_ajustado_teste:{Precision_ajusted_teste}")



print(f"acc_oot: {acc_oot}")
print(f"acc_justado_oot:{Acc_ajusted_oot}")
print(f"recall_teste: {recall_oot}")
print(f"recall_ajustado: {Recall_ajusted_oot}")
print(f"precisao: {precision_oot}")
print(f"precision_ajustado_oot:{Precision_ajusted_oot}")


# Com alteracao do threshold otimizando F1, temos aumento de recall na base teste e OOT, porém perdemos precisão.
# A decisão de alterar ou não o threshold vai depender do negócio e do custo de abordagem de clientes que iremos realizar. 
# Por exemplo, se o método de abordagem de clientes é barato/escalável, podemos considerar threshold com maior recall.
# Isso pq garantimos que vamos abordar mais clientes que tem maior prob de churn, mesmo que acabamos abordando mais clientes falso positivos (que não devem deixar de consumir o produto)
# Outra alternativa seria criar 2 campanhas: 1 campanha massiva e automática consideranos threshold menor (0,4 que obtemos com F1) e outra mais estratégica/crítica para clientes com prob > 0,7 por exemplo.
# Nesse caso como não temos essas informacoes, vamos seguir com threshold padrão de 0.5 para o projeto.

