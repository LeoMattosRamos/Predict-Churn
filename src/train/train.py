#%%

import pandas as pd
import sqlalchemy
from sklearn import model_selection
from sklearn import metrics
from sklearn import pipeline
from sklearn import ensemble
from sklearn import tree
import scikitplot as skplt



CREATE_ENGINE = sqlalchemy.create_engine("sqlite:///../../data/feature_store.db")

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
                                                                

X_train_tmp = X_train.copy()

X_train_tmp['flag'] = y_train

X_analise = X_train_tmp.groupby(by="flag").agg(["mean"]).T


X_analise['diff'] = X_analise[0] - X_analise[1]
X_analise['diff_%'] = X_analise[0] / X_analise[1]

X_analise.sort_values("diff_%", ascending=False)

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
                                    scoring='roc_auc')



grid.fit(X_train, y_train)

best_model = grid.best_estimator_




y_pred_train = grid.predict(X_train)
y_pred_test = grid.predict(X_test)
y_predict_proba = grid.predict_proba(X_test)[:,1]
y_pred_proba_oot = grid.predict_proba(df_oot[df_oot.columns[3:]])[:,1]
y_pred_oot = grid.predict(df_oot[df_oot.columns[3:]])



acc_treino = metrics.accuracy_score(y_train, y_pred_train)
acc_test = metrics.accuracy_score(y_test, y_pred_test)
roc = metrics.roc_auc_score(y_test, y_predict_proba)
roc_oot = metrics.roc_auc_score(df_oot[y], y_pred_proba_oot)
acc_oot = metrics.accuracy_score(df_oot[y],y_pred_oot )
recall = metrics.recall_score(y_test, y_pred_test)
recall_oot = metrics.recall_score(df_oot[y],y_pred_oot )

print(f"acc_treino: {acc_treino}")
print(f"acc_test: {acc_test}")
print(f"roc: {roc}")
print(f"recall: {recall}")
print(f"roc_oot: {roc_oot}")
print(f"acc_oot: {acc_oot}")
print(f"recall_oot: {recall_oot}")


confusion_matrix_teste = skplt.metrics.plot_confusion_matrix(y_test, y_pred_test)

confusion_matrix_oot = skplt.metrics.plot_confusion_matrix(df_oot[y], y_pred_oot)

#%%
y_pred_proba_oot_ = grid.predict_proba(df_oot[df_oot.columns[3:]])
y_predict_proba_ = grid.predict_proba(X_test)
# ROC = skplt.metrics.plot_ks_statistic(df_oot[y],y_pred_proba_oot_ )
# lift = skplt.metrics.plot_lift_curve(df_oot[y],y_pred_proba_oot_ )
cumulative_gain = skplt.metrics.plot_cumulative_gain(df_oot[y],y_pred_proba_oot_)
ks = skplt.metrics.plot_ks_statistic(y_test, y_predict_proba_)

#%%

import numpy as np

y_predict_proba_treino = grid.predict_proba(X_train)[:,1]

fpr, tpr, thresholds = metrics.roc_curve(y_test, y_predict_proba)
youden = tpr - fpr
optimal_idx = np.argmax(youden)
optimal_thresh = thresholds[optimal_idx]

y_pred_ajusted_test = (y_predict_proba >= optimal_thresh).astype(int) #testando outro threshold (youden = KS)
y_pred_ajusted_oot = (y_pred_proba_oot>= optimal_thresh).astype(int)
y_pred_ajusted_treino = (y_predict_proba_treino >= optimal_thresh).astype(int)

Acc_ajusted_teste = metrics.accuracy_score(y_test, y_pred_ajusted_test)
Acc_ajusted_treino = metrics.accuracy_score(y_train, y_pred_ajusted_treino)
Acc_ajusted_oot = metrics.accuracy_score(df_oot[y], y_pred_ajusted_oot)

print(f"acc_test: {acc_test}")
print(f"Ajustado_teste{Acc_ajusted_teste}")

print(f"acc_treino: {acc_treino}")
print(f"Ajustado_treino{Acc_ajusted_treino}")

print(f"acc_oot: {acc_oot}")
print(f"Ajustado_oot{Acc_ajusted_oot}")


## Nao obtivemos aumento de acc na base teste e OOT, apenas no treino. Portanto manterei o threshold padrão.

