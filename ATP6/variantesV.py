import pandas as pd
import glob
import os

archivos_txt = glob.glob("clinvar_result_*.txt")
df_ATP6 = pd.concat([pd.read_csv(archivo, sep="\t", engine="python", dtype=str).assign(archivo=archivo) 
                     for archivo in archivos_txt], ignore_index=True)

if not os.path.exists("ATP6_variantes.csv"):
    df_ATP6.to_csv("ATP6_variantes.csv", index=False)


df_ATP6.head(2)



# %%
