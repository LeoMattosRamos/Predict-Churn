#%%

import pandas as pd
import sqlalchemy
from sklearn import model_selection
from sklearn import metrics
from sklearn import pipeline
from sklearn import ensemble
from sklearn import tree


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


params = {"min_samples_leaf":[10,20,30,40,50,100,200],
          "max_depth": [2,4,5,6,8,10,15,20],
          "criterion": ["gini", "entropy"],
          "n_estimators": [10,20,50,100,200,300]
          }

model = ensemble.RandomForestClassifier(random_state=42)
                                
grid = model_selection.GridSearchCV(model,
                                    param_grid=params,
                                    cv=3,
                                    n_jobs= 8,
                                    scoring='roc_auc')

grid.fit(X_train, y_train)

best_model = grid.best_estimator_


importances = pd.Series(data=best_model.feature_importances_, index= X)
importances = importances.sort_values(ascending=False)
importances


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


print(f"acc_treino: {acc_treino}")
print(f"acc_test: {acc_test}")
print(f"roc: {roc}")
print(f"roc_oot: {roc_oot}")
print(f"acc_oot: {acc_oot}")

#%%
