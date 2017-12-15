#Need tensorflow for keras

from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import seaborn as sns; sns.set(color_codes=True)
from sklearn.metrics import mean_squared_error as mse
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score


# see sqlalchemy docs for how to write this url for your database type:
filepath="C:\\Users\\pkavikon\\Desktop\\stopwords.txt"

def read_file_stopwords(filepath):
    words=[]
    with open(filepath) as f:
        for line in f:
            words.append(line.strip().replace("'",""))
    return words


engine = create_engine('postgresql+psycopg2://postgres:password@localhost/TweetsDatabase')
print("Started")
df = pd.read_sql_query("select  t.*,f.followers from tweetsTable as t inner join followerstable as f ON t.postdate = f.date order by postdate desc", engine)
df.fillna(value=0, inplace=True)
y=df["retweets"]
del df['retweets']




from gensim.models import doc2vec
from collections import namedtuple

# Load data

doc1 = df["textfiltered"]

# Transform data (you can add more data preprocessing steps) 

docs = []
analyzedDocument = namedtuple('AnalyzedDocument', 'words tags')
for i, text in enumerate(doc1):
    words = text.lower().split()
    tags = [i]
    docs.append(analyzedDocument(words, tags))

# Train model (set min_count = 1, if you want the model to work with the provided example data set)

model = doc2vec.Doc2Vec(docs, size = 200, window = 350, min_count = 5, workers = 4)


import numpy as np
X=df['followers'].values


notSet=True

for index, row in df.iterrows():
    if notSet:
        notSet=False
        newAr=model.infer_vector(row["textfiltered"].split())
    else:
        newAr=np.vstack((newAr,model.infer_vector(row["textfiltered"].split())))

X=np.column_stack((X,newAr))


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=20)







from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.utils import np_utils
from keras.datasets import imdb
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers.convolutional import Convolution1D
from keras.layers.convolutional import MaxPooling1D
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence













def model2():
    # create model
    model = Sequential()
    model.add(Dense(100, input_dim=201, kernel_initializer='normal', activation='linear'))
    model.add(Dense(75,  kernel_initializer='normal', activation='linear'))
    model.add(Dense(50, kernel_initializer='normal', activation='linear'))
    model.add(Dense(10, kernel_initializer='normal', activation='linear'))
    model.add(Dense(1, kernel_initializer='normal', activation='linear'))
    # Compile model
    model.compile(optimizer='adam',
              loss='mse')
    return model

modelDoc=model2()
X_t=X_train
y_t=y_train.values
modelDoc.fit(X_t, y_t,epochs=50,batch_size=128)

y_predict=np.squeeze(modelDoc.predict(X_test))
r2=r2_score(y_test,y_predict)
adjusted_r_squared = 1 - (1-r2)*(len(y)-1)/(len(y)-X.shape[1]-1)
print(r2)
print(mse(y_test,y_predict))
print(adjusted_r_squared)
print("DONE")
