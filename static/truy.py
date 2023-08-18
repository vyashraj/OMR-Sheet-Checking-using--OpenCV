import pandas as pd

database=pd.read_csv('static/mp1.csv')
emails=list(database['Email'])
passwords=list(database['Password'])
# (emails,passwords).map(dict())
di=map(dict,[emails,passwords])
print(di)