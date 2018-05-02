
# coding: utf-8

# # Prediction of Liver Transplantation Success Rate

# Team: Liver Longer

# ## 1. Introduction

# ### 1.1 Helper Fuctions & Libraries

# In[98]:

# libraries and helper function
import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost.sklearn import XGBClassifier
from sklearn import cross_validation, metrics   #Additional scklearn functions
from sklearn.grid_search import GridSearchCV   #Perforing grid search


# show pearson correlation diagram
def showPearsonCorr(df):
    mask = np.zeros_like(df, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    f, ax = plt.subplots(figsize=(9, 9))
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    sns.heatmap(df, mask=mask, cmap=cmap, vmax=1, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})

# show bar chart
def showBarChart(data, x_label, y_label, x_names):
    plt.figure(figsize=(13,6))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(range(len(x_names)),x_names, rotation=80)
    plt.bar(range(len(x_names)), data )  
    plt.show() 

# get missing value rate according to the dataframe
def getMissingRate(data):
    result=pd.DataFrame( data.isnull().sum()/len(data)*100 )
    result.columns=["MissingRate"]
    result=result[result["MissingRate"]>0]
    return result

# get y labels according to dataset
def getXandY(df, day, PorG):
    if PorG=="PTIME":
        tmp=df[ (df.PTIME>=day) | (df.PSTATUS==1) ].copy()
        tmp.loc[: , "label"]= tmp.apply(lambda x: x.PIME<day, axis=1).astype(int)
        tmp.drop( columns=["GTIME", "GSTATUS"], inplace=True )
        tmp.drop( columns=["PTIME", "PSTATUS"], inplace=True )
        y=tmp.label
        x=tmp.iloc[:,:-1]
        return x,y
    elif PorG=="GTIME":
        tmp=df[(df.GTIME>=day) | (df.GSTATUS==1) ].copy()
        tmp.loc[:, "label"] = tmp.apply(lambda x: x.GTIME<day, axis=1).astype(int)
        tmp.drop(columns=["GTIME", "GSTATUS"], inplace=True)
        tmp.drop(columns=["PTIME", "PSTATUS"], inplace=True)
        y=tmp.label
        x=tmp.iloc[:,:-1]
        return x,y
    else:
        return None, None

# plot feature importances using XGBoost model		
def plotFeatureImportance(xgbModel, importanceType="weight", featureNum=80):
    tmp=xgbModel.get_score(importance_type=importanceType)
    kv=list(tmp.items())
    kv.sort(key=lambda x: -x[1])
    kv=kv[:featureNum]
    kv=list(zip(*kv))
    names=kv[0]
    values=kv[1]
    plt.figure(figsize=(20,10))
    plt.xlabel("Feature")
    plt.ylabel(importanceType)
    plt.xticks(range(len(names)),names, rotation=80)
    plt.bar(range(len(names)), values )  
    plt.show() 
    
# train XGBoost    
def modelfit(alg, dtrain, predictors,useTrainCV=True, cv_folds=5, early_stopping_rounds=50):
    if useTrainCV:
        xgb_param = alg.get_xgb_params()
        xgtrain = xgb.DMatrix(dtrain[predictors].values, label=dtrain[target].values)
        cvresult = xgb.cv(xgb_param, xgtrain, num_boost_round=alg.get_params()['n_estimators'], nfold=cv_folds,
            metrics='auc', early_stopping_rounds=early_stopping_rounds, show_progress=False)
        alg.set_params(n_estimators=cvresult.shape[0])
    
    #Fit the algorithm on the data
    alg.fit(dtrain[predictors], dtrain['Disbursed'],eval_metric='auc')
        
    #Predict training set:
    dtrain_predictions = alg.predict(dtrain[predictors])
    dtrain_predprob = alg.predict_proba(dtrain[predictors])[:,1]
        
    #Print model report:
    print("\nModel Report")
    print("Accuracy : %.4g" % metrics.accuracy_score(dtrain['Disbursed'].values, dtrain_predictions))
    print("AUC Score (Train): %f" % metrics.roc_auc_score(dtrain['Disbursed'], dtrain_predprob))
                    
    feat_imp = pd.Series(alg.booster().get_fscore()).sort_values(ascending=False)
    feat_imp.plot(kind='bar', title='Feature Importances')
    plt.ylabel('Feature Importance Score')


# ### 1.2 Load Data
data = pd.read_csv('dataset/liver_data_inf560.csv',header = 0, na_values = 'NaN')


# ### 1.3 Data Preprocessing
data= data.drop(data[data.PTIME < data.GTIME].index)
tmp= data.drop(data[data["FINAL_MELD_OR_PELD"]=="PELD"].index )
tmp= tmp.drop(columns=["FINAL_MELD_OR_PELD"])
data= tmp
originalData=data.copy()


tmp= data.replace("Unknown", np.nan)


# Drop post transplant features 
allPostFeatures=["BILIARY", "COD","COD_OSTXT","COD2","COD2_OSTXT","COD3","COD3_OSTXT","GRF_FAIL_CAUSE_OSTXT","GRF_STAT",
              "HEP_DENOVO",
              "HEP_RECUR",
              "INFECT",
              "PRI_GRF_FAIL",
              "RECUR_DISEASE",
              "REJ_ACUTE",
              "VASC_THROMB",
              "FUNC_STAT_TRF",
              "PX_NON_COMPL",
              "REJ_CHRONIC",
              "DIFFUSE_CHOLANG",
              "HEPATIC_ART_THROM",
              "HEPATIC_OUT_OBS",
              "OTHER_VASC_THROMB",
              "PORTAL_VEIN_THROM",
              "PRI_NON_FUNC",
              "PX_STAT",
              "LOS",
              "ACUTE_REJ_EPI",
              "DIS_ALKPHOS",
              "DIS_SGOT",
              "COMPOSITE_DEATH_DATE",
              "DEATH_DATE",
              "DISCHARGE_DATE",
              "GRF_FAIL_DATE",
              "END_DATE"] 

postFeatures=[]
allFeatures=data.columns.values
for each in allPostFeatures:
    if each in allFeatures:
        postFeatures.append(each)

#["ACUTE_REJ_EPI", "GRF_STAT", "LOS"]

unrelatedFeatures=["WL_ID_CODE","DONOR_ID", "TRR_ID_CODE","CTR_CODE","OPO_CTR_CODE", "TRR_ID_CODE", "LISTING_CTR_CODE"]
                   # ["DATA_WAITLIST", "DATA_TRANSPLANT", "LT_ONE_WEEK_DON", "TX_MELD", "LIST_MELD"]
data.drop(columns=unrelatedFeatures, inplace=True)
# LOS: RECIPIENT LENGTH OF STAY POST TX
data.drop(columns=postFeatures, inplace=True)


# encode categorical features
categoricalFeatures=data.select_dtypes(include=["object"]).columns
singleValueFeatures=[]
tooManyCategories=[]
for feature in categoricalFeatures:
    num=data[feature].nunique()
    if num==2:
        mid=pd.get_dummies(data, columns=[feature], drop_first=True)
        mid.loc[data[feature].isnull(), mid.columns.str.startswith(feature)]=np.nan
        data=mid
    elif num==1:
        singleValueFeatures.append(feature)
    elif num>=3 and num<=10:
        data=pd.get_dummies(data, columns=[feature], dummy_na=True)
    else:
        tooManyCategories.append(feature)


# drop single value features
singleValueFeatures=[]
for feature in data.columns.values:
    num=data[feature].nunique()
    if num==1:
        singleValueFeatures.append(feature)
        
data.drop(columns=singleValueFeatures, inplace=True)

singleValueFeatures


# transform other features

sns.distplot(data[data.PH_DON.notnull()].PH_DON)
data.loc[np.abs(data.PH_DON- data.PH_DON.mean())>(3*data.PH_DON.std()), "PH_DON"]=np.nan


# process nan
data=data.replace(999, np.nan)
data=data.replace(998, np.nan)
data=data.replace(997, np.nan)
data=data.replace(996, np.nan)


# DIAG (May use binary encoding instead) 
categoricalNumeric=["DIAB"]
             # ["DIAG","LITYP"]

for each in categoricalNumeric:  
    data=pd.get_dummies(data, columns=[each], dummy_na=True)


# FUNC_STAT_TRR
# column_name = 'FUNC_STAT_TRR'
# df = data
# df.loc[df.FUNC_STAT_TRR == 1.0, column_name] = 10
# df.loc[df.FUNC_STAT_TRR == 2.0, column_name] = 5
# df.loc[df.FUNC_STAT_TRR == 3.0, column_name] = 1
# df.loc[df.FUNC_STAT_TRR == 2010, column_name] = 1
# df.loc[df.FUNC_STAT_TRR == 2020, column_name] = 2
# df.loc[df.FUNC_STAT_TRR == 2030, column_name] = 3
# df.loc[df.FUNC_STAT_TRR == 2040, column_name] = 4
# df.loc[df.FUNC_STAT_TRR == 2050, column_name] = 5
# df.loc[df.FUNC_STAT_TRR == 2060, column_name] = 6
# df.loc[df.FUNC_STAT_TRR == 2070, column_name] = 7
# df.loc[df.FUNC_STAT_TRR == 2080, column_name] = 8
# df.loc[df.FUNC_STAT_TRR == 2090, column_name] = 9
# df.loc[df.FUNC_STAT_TRR == 2100, column_name] = 10
# df.loc[df.FUNC_STAT_TRR == 4010, column_name] = 1
# df.loc[df.FUNC_STAT_TRR == 4020, column_name] = 2
# df.loc[df.FUNC_STAT_TRR == 4030, column_name] = 3
# df.loc[df.FUNC_STAT_TRR == 4040, column_name] = 4
# df.loc[df.FUNC_STAT_TRR == 4050, column_name] = 5
# df.loc[df.FUNC_STAT_TRR == 4060, column_name] = 6
# df.loc[df.FUNC_STAT_TRR == 4070, column_name] = 7
# df.loc[df.FUNC_STAT_TRR == 4080, column_name] = 8
# df.loc[df.FUNC_STAT_TRR == 4090, column_name] = 9
# df.loc[df.FUNC_STAT_TRR == 4100, column_name] = 10
# data = df




data.TX_PROCEDUR_TY=data.TX_PROCEDUR_TY-700



data.shape




data.describe()



getMissingRate(data)


# ## 2. Data Visualization

# GTIME vs PTIME

sample=data.sample(2000)


sns.regplot(x=sample["GTIME"], y=sample["PTIME"])


# GTIME distribution
tmp=data[data.GSTATUS==1]
sns.distplot(tmp[tmp.GTIME.notnull()].GTIME)


# Log(GTIME)
tmp=data[ (data.GSTATUS==1)].GTIME
tmp=tmp[tmp.notnull()]
tmp=tmp.map(lambda x: x+1)
tmp=np.log(tmp)
tmp.name="log(GTIME)"
sns.distplot(tmp)

tmp=data[data.PSTATUS==1].PTIME
sns.distplot(tmp[tmp.notnull()])

sns.regplot(x=sample["PTIME"], y=sample["PH_DON"])


# Waitime
sns.regplot(x=sample["DAYSWAIT_CHRON"], y=sample["GTIME"])
sns.regplot(x=sample["DAYSWAIT_CHRON"], y=sample["PTIME"])


# state
tmp=originalData.groupby(["PERM_STATE_TRR"])["PERM_STATE_TRR", "DAYSWAIT_CHRON"].median()
showBarChart(tmp.DAYSWAIT_CHRON, "State", "waiting time", tmp.index.values)
tmp=originalData.groupby(["ABO_MAT"])["ABO_MAT", "GTIME"].median()
tmp=originalData.groupby(["ABO_MAT"])["ABO_MAT", "PTIME"].median()
tmp



tmp=originalData.groupby(["DIAG"])["DIAG", "GTIME"].median()
sns.set(rc={'figure.figsize':(15,9)})
sample=originalData.sample(5000)
plt.xticks(rotation=80)
tmp=sns.swarmplot(x="PERM_STATE_TRR", y="GTIME", data=sample)

sns.regplot(x=sample.DISTANCE, y=sample.GTIME)


# ## 3. XGBoost Modeling


#data.drop(columns=tooManyCategories, inplace=True)
data.drop(columns=["PERM_STATE", "PERM_STATE_TRR", "HOME_STATE_DON"],inplace=True)
x,y =getXandY(data, day=90, PorG="GTIME")

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test=train_test_split(x,y, test_size=0.2, random_state=1)
dtrain=xgb.DMatrix(x_train, label=y_train)
dtest= xgb.DMatrix(x_test, label=y_test)

# xgb_pars = {'min_child_weight': 50, 'eta': 0.3, 'colsample_bytree': 0.3, 'max_depth': 10,
#             'subsample': 0.8, 'lambda': 1., 'nthread': 4, 'booster' : 'gbtree', 'silent': 0,
#             'eval_metric': ["auc", "error"], 'objective': 'binary:logistic'}
xgb_pars = {'min_child_weight': 50, 'eta': 0.1, 'colsample_bytree': 0.3, 'max_depth': 10,
            'subsample': 0.8, 'lambda': 1., 'nthread': 4, 'booster' : 'gbtree', 'silent': 0,
            'eval_metric': "auc", 'objective': 'binary:logistic', "scale_pos_weight": 1}
watchlist=[(dtest, "eval"), (dtrain, "train")]

model=xgb.train(xgb_pars, dtrain, 60, watchlist, early_stopping_rounds=50, maximize=False, verbose_eval=10)



# Show Feature Importance
plotFeatureImportance(model, importanceType="weight", featureNum=50)


xgb_pars = {'min_child_weight': 50, 'eta': 0.1, 'colsample_bytree': 0.3, 'max_depth': 10,
            'subsample': 0.8, 'lambda': 1., 'nthread': 4, 'booster' : 'gbtree', 'silent': 0,
            'eval_metric': "auc", 'objective': 'binary:logistic', "scale_pos_weight": 1}

dtrain=xgb.DMatrix(x_train, label=y_train)
xgb.cv(xgb_pars, dtrain, 60, nfold=5, seed=0, callbacks=[xgb.callback.print_evaluation(show_stdv=True)])


fig, ax = plt.subplots(figsize=(12,18))
xgb.plot_importance(model, max_num_features=100, height=0.8, ax=ax)
plt.show()


# 3.1 Feature Importance-based Feature Selection
importance=model.get_score( importance_type="weight")
kv=list(importance.items())
kv.sort(key=lambda x: -x[1])
tmp=list(zip(*kv))
names=tmp[0]
values=tmp[1]


newx=x.loc[ :, names]

# retrain the model
x_train, x_test, y_train, y_test=train_test_split(newx,y, test_size=0.2, random_state=1)
dtrain=xgb.DMatrix(x_train, label=y_train)
dtest= xgb.DMatrix(x_test, label=y_test)

# xgb_pars = {'min_child_weight': 50, 'eta': 0.3, 'colsample_bytree': 0.3, 'max_depth': 10,
#             'subsample': 0.8, 'lambda': 1., 'nthread': 4, 'booster' : 'gbtree', 'silent': 0,
#             'eval_metric': ["auc", "error"], 'objective': 'binary:logistic'}
xgb_pars = {'min_child_weight': 50, 'eta': 0.02, 'colsample_bytree': 0.3, 'max_depth': 10,
            'subsample': 0.8, 'lambda': 1., 'nthread': 4, 'booster' : 'gbtree', 'silent': 0,
            'eval_metric': "auc", 'objective': 'binary:logistic', "scale_pos_weight": 1}
watchlist=[(dtest, "eval"), (dtrain, "train")]

model=xgb.train(xgb_pars, dtrain, 60, watchlist, early_stopping_rounds=50, maximize=False, verbose_eval=10)

