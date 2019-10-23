import numpy as np
import pandas as pd
import re
import sys
from re import error
from matplotlib import pyplot as plt
from matplotlib import figure
from scipy.stats import gaussian_kde


fileName = input('Enter name of file: ')
try:
    df = pd.read_csv(fileName, encoding = 'ISO-8859-1')
except FileNotFoundError:
    print('\'' + fileName + '\' not found. Exiting...')
    sys.exit()

df.dropna(inplace=True)
df.is_copy = False

def splitTag(tag):
    tag = re.match('\[(.*)\]', tag).group(1).replace('\'', '').split(', ')
    for i in range(len(tag)):
        tag[i] = tag[i].replace(' ', '_')
    return(tag)

def getTagDF():
    index = 0
    tagVals = pd.DataFrame()
    print('Creating Tag dataframe...')
    for tag in tagSet:
        try:
            if tag.find('|') >= 0:
                continue
            dz = df[df['Tags'].astype(str).str.contains('\''+tag+'\'')] 
        except re.error as e:
            print('re.error on tag: ' + tag)
            continue
        if len(dz) is not 0: 
            sumViews = sum(dz['Views'])
            sumLikes = sum(dz['Likes'])
            sumDislikes = sum(dz['Dislikes'])
            sumComments = sum(dz['NumComments'])
            count = len(dz)      
            rowi = {
                    'Tag': tag, 
                    'SumViews': sumViews,
                    'AvgViews': sumViews/count,
                    'SumLikes': sumLikes,
                    'AvgLikes': sumLikes/count,
                    'SumDislikes': sumDislikes,
                    'AvgDislikes': sumDislikes/count,
                    'SumComments': sumComments,
                    'AvgComments': sumComments/count, 
                    'Count': len(dz)
                   }
            rowi = pd.DataFrame(data=rowi, index=[index])
            tagVals = tagVals.append(rowi)
        index = index + 1
        tagVals = tagVals[tagVals['Tag'].astype(str).str.len() > 1]
    print('Finished!')
    return tagVals

try:
    dataName = re.match('(.*)(_scrape\.csv)', fileName).group(1) + '_tagData.csv'
    tagDataFile = pd.read_csv(dataName)
except FileNotFoundError:
    for i in range(len(df)):
        try:
            df['Tags'].loc[i] = splitTag(df['Tags'][i])
        except KeyError:
            continue

    tagList = []

    for i in df['Tags']:
        for k in i:
            tagList.append(k)

    tagSet = set(tagList)
    tagList = list(tagSet)
    tagDataFile = getTagDF()
    tagDataFile.to_csv(dataName)

df = df[df['NumComments'] < 50001] 


x = df['Date Published']
dislikes = df['Dislikes']
likes = df['Likes']
views = df['Views']
comments = df['NumComments']



#likes vs dislikes filled plot
plt.figure(0, figsize=(15,7))

plt.plot(x, likes, color='green')
plt.plot(x, dislikes, color='red')
plt.fill_between(x, 0, dislikes, color='red', alpha='1')
plt.fill_between(x, dislikes, likes, color='green', alpha='1')
plt.gca().invert_xaxis()
xRange = list(dict.fromkeys(x))
mid = len(xRange)//2
halfMid = mid//2
plt.xticks([0, halfMid, mid, mid+halfMid, len(xRange)-1],
        [xRange[0], xRange[halfMid], xRange[mid], xRange[mid + halfMid], xRange[len(xRange)-1]])
plt.yticks(rotation=45)
plt.ylabel('Likes & Dislikes')
plt.xlabel('Time')
plt.title('Likes vs Dislikes')
plt.legend(['Likes','Dislikes'])

plt.savefig('LikesDislikesTime.png')



#views vs likes vs dislikes filled plot
plt.figure(3, figsize=(15,7))

plt.plot(x, likes, color='green')
plt.plot(x, dislikes, color='red')
plt.plot(x, views, color='#6088c9')
plt.fill_between(x, 0, dislikes, color='red', alpha='1')
plt.fill_between(x, dislikes, likes, color='green', alpha='1')
plt.fill_between(x, likes, views, color='#6088c9', alpha='1')
plt.gca().invert_xaxis()
plt.ticklabel_format(style='plain', axis='y')
xRange = list(dict.fromkeys(x))
id = len(xRange)//2
halfMid = mid//2
plt.xticks([0, halfMid, mid, mid+halfMid, len(xRange)-1],
        [xRange[0], xRange[halfMid], xRange[mid], xRange[mid + halfMid], xRange[len(xRange)-1]])
plt.yticks(rotation=45)
plt.ylabel('Views/Likes/Dislikes')
plt.xlabel('Time')
plt.title('Views, Likes, and Dislikes over time')
plt.legend(['Likes','Dislikes', 'Views'])

plt.savefig('ViewsLikesDislikesTime.png')



#scatter plot
#referenced material:
#https://stackoverflow.com/questions/20105364/how-can-i-make-a-scatter-plot-colored-by-density-in-matplotlib

plt.figure(1, figsize=(10,7))
likesAndDislikes = likes+dislikes

density = np.vstack([comments,likesAndDislikes])
z = gaussian_kde(density)(density)

plt.inferno()
plt.scatter(comments, likesAndDislikes, c=z, s=25, edgecolors='')
plt.xlabel('Comments')
plt.ylabel('Likes and Dislikes')
plt.title('Likes+Dislikes vs Comments (no outliers)')
plt.yticks(rotation=45)
plt.colorbar(orientation='horizontal')

plt.savefig('Likes+Dislikes_vs_Comments.png')


#boxplot
fig, ((ax1, ax2),(ax3, ax4)) = plt.subplots(2, 2)
fig.set_size_inches(10,7)
fig.suptitle('Boxplots', fontsize=16)

ax1.boxplot(views, notch=True, patch_artist=True)
ax1labels = ax1.get_yticklabels()
for tick in ax1labels:
        tick.set_rotation(45)
ax1.set_title('Views')
ax1.set_xticklabels([])
ax1.ticklabel_format(style='plain', axis='y')

ax2.boxplot(comments, notch=True, patch_artist=True)
ax2labels = ax2.get_yticklabels()
for tick in ax2labels:
        tick.set_rotation(45)
ax2.set_title('Comments')
ax2.set_xticklabels([])

ax3.boxplot(likes, notch=True, patch_artist=True)
ax3labels = ax3.get_yticklabels()
for tick in ax3labels:
        tick.set_rotation(45)
ax3.set_title('Likes')
ax3.set_xticklabels([])

ax4.boxplot(dislikes, notch=True, patch_artist=True)
ax4labels = ax4.get_yticklabels()
for tick in ax4labels:
        tick.set_rotation(45)
ax4.set_title('Dislikes')
ax4.set_xticklabels([])

fig.savefig('Boxplots.png')


#Top 20 tags by sum views
tagDataFile = tagDataFile.sort_values('SumViews')
plt.figure(5,figsize=(10,7))
x = tagDataFile[-20:]['Tag']
y = tagDataFile[-20:]['SumViews']
plt.scatter(x, y, color='#6088c9')
plt.xticks(rotation=-45)
plt.xlabel('Tag')
plt.ylabel('Sum Views')
plt.ticklabel_format(style='plain', axis='y')
plt.title('Top 20 Tags by Sum of Views')

plt.savefig('Top20TagViews.png')


#Top 20 tags by sum likes
tagDataFile = tagDataFile.sort_values('SumLikes')
plt.figure(7,figsize=(10,7))
x2 = tagDataFile[-20:]['Tag']
y2 = tagDataFile[-20:]['SumLikes']
plt.scatter(x2, y2, color='green')
plt.xticks(rotation=-45)
plt.xlabel('Tag')
plt.ylabel('Sum Likes')
plt.ticklabel_format(style='plain', axis='y')
plt.title('Top 20 Tags by Sum of Likes')

plt.savefig('Top20TagLikes.png')


#Top 20 tags by sum dislikes
tagDataFile = tagDataFile.sort_values('SumDislikes')
plt.figure(9,figsize=(10,7))
x3 = tagDataFile[-20:]['Tag']
y3 = tagDataFile[-20:]['SumDislikes']
plt.scatter(x3, y3, color='red')
plt.xticks(rotation=-45)
plt.xlabel('Tag')
plt.ylabel('Sum Dislikes')
plt.ticklabel_format(style='plain', axis='y')
plt.title('"Top" 20 Tags by Sum of Dislikes')

plt.savefig('Top20TagDislikes.png')

plt.show()
