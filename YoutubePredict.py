import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import HuberRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
import matplotlib.pyplot as plt
import re

fileName = input('Enter File Name: ')
df = pd.read_csv(fileName, encoding = 'ISO-8859-1')
df.dropna(inplace=True)

def splitTag(tag):
    tag = re.match('\[(.*)\]', tag).group(1).replace('\'', '').split(', ')
    for i in range(len(tag)):
        tag[i] = tag[i].replace(' ', '_')
    return(str(tag))

for i in range(len(df)):
    try:
        df['Tags'].loc[i] = splitTag(df['Tags'][i])
    except KeyError:
        continue


tags = df['Tags']
titles = df['Video']
views = df['Views']
views_comments = df[['Views', 'NumComments']]
likes = df['Likes']
dislikes = df['Dislikes']
comments = df['NumComments']
likes_dislikes = df[['Likes', 'Dislikes']]

print('Views std:\t%f' % views.std())
print('Views Range:\t%f\n' % (views.max() - views.min()))
print('Likes std:\t%f' % likes.std())
print('Likes Range:\t%f\n' % (likes.max() - likes.min()))
print('Comments std:\t%f' % comments.std())
print('Comments Range:\t%f' % (comments.max() - comments.min()))



print('\n\n')
print('----------Start Prediction----------')



"""
Bag of words for view count from tags
"""
print('predicting view count from tags...')
tag_train, tag_test, view_train, view_test = train_test_split(tags, views, test_size=0.2, random_state=7951)
tag_train, tag_valid, view_train, view_valid = train_test_split(tag_train, view_train, test_size=0.25, random_state=7951)

count_vect = CountVectorizer()
count_vect.fit(tags)

tag_train = count_vect.transform(tag_train)
tag_valid = count_vect.transform(tag_valid)
tag_test = count_vect.transform(tag_test)

tsvd = TruncatedSVD(n_components=564)
tag_train = tsvd.fit_transform(tag_train)
tag_valid = tsvd.fit_transform(tag_valid)
tag_test = tsvd.fit_transform(tag_test)


lr = HuberRegressor(fit_intercept=True, epsilon=2.35)
lr.fit(X=tag_train, y=view_train)

view_hat = lr.predict(tag_train)
errTrain = ((view_hat - view_train)**2).mean()**(1/2)
print('training set root squared mean error:')
print(errTrain)

view_hat_valid = lr.predict(tag_valid)
errValid = ((view_hat_valid - view_valid)**2).mean()**(1/2)
print('validation set root squared mean error:')
print(errValid)

view_hat_valid_TEST = lr.predict(tag_test)
errValid = ((view_hat_valid_TEST - view_test)**2).mean()**(1/2)
print('test set root squared mean error:')
print(errValid)

print()

count_vect = None
tsvd = None
lr = None



"""
Bag of words for view count from title
"""
print('predicting view count from titles...')
titles_train, titles_test, view_train, view_test = train_test_split(titles, views, test_size=0.2, random_state=7951)
titles_train, titles_valid, view_train, view_valid = train_test_split(titles_train, view_train, test_size=0.25, random_state=7951)

count_vect = CountVectorizer()
count_vect.fit(titles)

titles_train = count_vect.transform(titles_train)
titles_valid = count_vect.transform(titles_valid)

tsvd = TruncatedSVD(n_components=256)

titles_train = tsvd.fit_transform(titles_train)
titles_valid = tsvd.fit_transform(titles_valid)

lr = LinearRegression(fit_intercept=True, normalize=False)
lr.fit(X=titles_train, y=view_train)

view_hat = lr.predict(titles_train)
errTrain = ((view_hat - view_train)**2).mean()**(1/2)
print('training set root squared mean error:')
print(errTrain)

view_hat_valid = lr.predict(titles_valid)
errValid = ((view_hat_valid - view_valid)**2).mean()**(1/2)
print('validation set root squared mean error:')
print(errValid)


print()

count_vect = None
tsvd = None
lr = None



"""
Polynomial model for predicting likes from views
"""
print('predicting likes from views...')
views_train, views_test, likes_train, likes_test = train_test_split(views_comments, likes, test_size=0.2, random_state=7951)
views_train, views_valid, likes_train, likes_valid = train_test_split(views_train, likes_train, test_size=0.25, random_state=7951)
poly = PolynomialFeatures(degree=3)
poly_VC_train = poly.fit_transform(views_train, likes_train)
poly_VC_valid = poly.fit_transform(views_valid)

lr = LinearRegression(fit_intercept=True, normalize=True)
lr = lr.fit(poly_VC_train, likes_train)


likes_train_hat = lr.predict(poly_VC_train)
errTrain = ((likes_train_hat - likes_train)**2).mean()**(1/2)
print('training set root squared mean error:')
print(errTrain)

likes_valid_hat = lr.predict(poly_VC_valid)
errValid = ((likes_valid_hat - likes_valid)**2).mean()**(1/2)
print('validation set root squared mean error:')
print(errValid)


print()

poly = None
lr = None


"""
Linear Regression model for predicting comments from likes and dislikes
"""
print('predicting comments from likes and dislikes...')
likes_dislikes_train, likes_dislikes_test, comments_train, comments_test = train_test_split(likes_dislikes, comments, test_size=0.2, random_state=7951)
likes_dislikes_train, likes_dislikes_valid, comments_train, comments_valid = train_test_split(likes_dislikes_train, comments_train, test_size=0.25, random_state=7951)

lr = LinearRegression(fit_intercept=True, normalize=True)
lr = lr.fit(likes_dislikes_train, comments_train)

comments_train_hat = lr.predict(likes_dislikes_train)
errTrain = ((comments_train_hat - comments_train)**2).mean()**(1/2)
print('training set root squared mean error:')
print(errTrain)

comments_valid_hat = lr.predict(likes_dislikes_valid)
errValid = ((comments_valid_hat - comments_valid)**2).mean()**(1/2)
print('validation set root squared mean error:')
print(errValid)
