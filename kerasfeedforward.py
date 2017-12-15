#Need tensorflow for keras

from sqlalchemy import create_engine
import matplotlib.pyplot as plt

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
df.fillna(value=0,inplace=True)
y=df["retweets"]
del df['retweets']

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split

num=120
#vecT = CountVectorizer(stop_words=read_file_stopwords(filepath),max_features=num)
vecT = TfidfVectorizer(stop_words=read_file_stopwords(filepath),max_features=num)
textVecT = vecT.fit_transform(df["textfilterednohashtagsats"]).toarray()
print(textVecT.shape)

others=np.column_stack((textVecT,df["followers"]))

others=pd.DataFrame(others)
#others=pd.DataFrame(textVecT)
X=pd.concat([others], axis=1)


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=20)
print(X_train.shape)


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


# define base model
def baseline_model():
    # create model
    model = Sequential()
    model.add(Dense(250, input_dim=121, kernel_initializer='normal', activation='softmax'))
    model.add(Dense(100,  kernel_initializer='normal', activation='softmax'))
    model.add(Dense(50, kernel_initializer='normal', activation='softmax'))
    model.add(Dense(25, kernel_initializer='normal', activation='softmax'))
    model.add(Dense(10, kernel_initializer='normal', activation='softmax'))
    model.add(Dense(1, kernel_initializer='normal', activation='softmax'))
    # Compile model
    model.compile(optimizer='adam',
              loss='mse')
    return model




model = baseline_model()

X_t=X_train.values
y_t=y_train.values
model.fit(X_t, y_t,epochs=75,batch_size=128)
import matplotlib.pyplot as plt
y_predict=np.squeeze(model.predict(X_test.values))
r2=r2_score(y_test,y_predict)
print(r2)
adjusted_r_squared = 1 - (1-r2)*(len(y)-1)/(len(y)-X.shape[1]-1)
print(adjusted_r_squared)
print(mse(y_test,y_predict))
z=(y_test-y_predict)
plt.hist(z,bins=500)
plt.show()
print("DONE")
