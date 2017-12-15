from sqlalchemy import create_engine
import matplotlib.pyplot as plt

import seaborn as sns; sns.set(color_codes=True)
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import make_scorer
import pandas as pd
import numpy as np
from sklearn.linear_model import  LinearRegression 
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestRegressor
import time
#from textblob import TextBlob

# see sqlalchemy docs for how to write this url for your database type:
filepath="C:\\Users\\pkavikon\\Desktop\\stopwords2.txt"

def read_file_stopwords(filepath):
    words=[]
    with open(filepath) as f:
        for line in f:
            words.append(line.strip().replace("'",""))
    return words

def func_auc(model,y, X):
    Y_pred=model.predict(X)
    r2=r2_score(y,Y_pred)
    adjusted_r_squared = 1 - (1-r2)*(len(y)-1)/(len(y)-X.shape[1]-1)
    print(adjusted_r_squared)
    
    return (r2,mse(y,Y_pred))

    






def makestringfromlist(li):
    return ' '.join(li)





stop=read_file_stopwords(filepath)

engine = create_engine('postgresql+psycopg2://postgres:password@localhost/TweetsDatabase')
df = pd.read_sql_query("select  t.* ,f.followers from tweetsTable as t inner join followerstable as f ON t.postdate = f.date order by postdate desc", engine)
df.fillna(value=0, inplace=True)
y=df["favorites"]
del df['favorites']

#df['hashtagcollection']=df['hashtagcollection'].apply(lambda x: len(x))
    #df['hashtagcollection']=df['hashtagcollection'].apply(lambda x: ' '.join(x))
    #vecHash=TfidfVectorizer(stop_words=stop,max_features=5)
    #vecHashMat = vecT.fit_transform(df["hashtagcollection"]).toarray()

#df['atcollection']=df['atcollection'].apply(lambda x: len(x))
    #df['atcollection']=df['atcollection'].apply(lambda x: ' '.join(x))
    #vecAt=TfidfVectorizer(stop_words=stop,max_features=5)
    #vecAtMat = vecT.fit_transform(df["atcollection"]).toarray()
print("Done ")
df.fillna(value=0, inplace=True)
#for x in range(200,2000,100):
    #findBest(df,y,stop,x)
    
    





from sklearn.linear_model import Lasso

linReg=Lasso()
#linReg=RandomForestRegressor()

vecT = TfidfVectorizer(stop_words=stop,max_features=100)

textVecT = vecT.fit_transform(df["textfiltered"]).toarray()

    #print("Combining")
    

print("DONE")
 
    
#    df['sentiment']=0.0
#    df['polarity']=0.0


#    for index, row in df.iterrows():
#        tweet=TextBlob(row['textfiltered'])
#        df.set_value(index,'sentiment',tweet.sentiment.subjectivity)
#        df.set_value(index,'polarity',tweet.sentiment.polarity)
        
        
        
#others=np.column_stack((textVecT))

others=pd.DataFrame(textVecT)
X=pd.concat([df["followers"],others], axis=1)
X=X.fillna(0)
    
    
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=20)
print("SPLITTED")
linReg.fit(X_train,y_train)
print("DOne traiing")
t=func_auc(linReg,y_test,X_test)
print(t[0])
print(t[1]) 
