
# coding: utf-8

# In[9]:


import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost.sklearn import XGBClassifier
import pickle

modelName="xgbModel"
dummyFileName='test_x.pickle'
inputFileName="sampleInput.csv"

model= xgb.Booster()
model.load_model(modelName)

dummyData=pickle.load(open(dummyFileName, "rb"))
dataToPredict=pd.read_csv(inputFileName,header = 0, na_values = 'NaN')



# x is the dataFrame
def predict(x):
    test_x=dummyData.sample(x.shape[0])
    dmatrix=xgb.DMatrix(test_x)
    y=model.predict(dmatrix)
    return y
    
    

