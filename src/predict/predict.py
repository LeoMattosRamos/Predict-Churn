#%%

import mlflow.sklearn
import pandas as pd
import sqlalchemy
import mlflow
from sqlalchemy import exc

CREATE_ENGINE = sqlalchemy.create_engine("sqlite:///../../data/feature_store.db")

mlflow.set_tracking_uri("http://127.0.0.1:5000")

model = mlflow.sklearn.load_model("models:/Churn_modelo/1")

features = model.feature_names_in_



def import_query(path):
    with open(path, 'r') as open_file:
        return(open_file.read())

query = import_query("../predict/predicao.sql")


df = pd.read_sql(query, CREATE_ENGINE)


proba = model.predict_proba(df[features])[:,1]
df_proba = df[['Dt_ref', 'idCustomer']].copy()

df_proba['proba_churn'] = proba

with CREATE_ENGINE.connect() as con:
    state = f"DELETE FROM tb_churn WHERE Dt_ref = '{df_proba['Dt_ref'].min()}';"

    try:
        state = sqlalchemy.text(state)
        con.execute(state)
        con.commit()
    except exc.OperationalError as err:
        print("Tabela ainda não existe...")


df_proba.to_sql("tb_churn", CREATE_ENGINE,if_exists='append', index=False)





