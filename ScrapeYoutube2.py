#Selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

#other
import re
import csv
import json
import time
import datetime

#Google API
import os
import googleapiclient.discovery
from googleapiclient.errors import HttpError

class ScrapeYoutube2:

    driver = None
    csv_file = None
    csv_writer = None
    csvName = ''
    url = None
    data = []
    wait = None
    fullSearch = False
    userID = ''
    currentTimeStamp = ''
    ff_prof = None
    chrome_ops = None

    Choice_Chrome = False
    Choice_FF = False

    youtube = None
    DEVELOPER_KEY = ''

    resume = False
    resume_json = None
    videoCategories = {
        2 : 'Autos & Vehicles',
        1 :  'Film & Animation',
        10 : 'Music',
        15 : 'Pets & Animals',
        17 : 'Sports',
        18 : 'Short Movies',
        19 : 'Travel & Events',
        20 : 'Gaming',
        21 : 'Videoblogging',
        22 : 'People & Blogs',
        23 : 'Comedy',
        24 : 'Entertainment',
        25 : 'News & Politics',
        26 : 'Howto & Style',
        27 : 'Education',
        28 : 'Science & Technology',
        29 :' Nonprofits & Activism',
        30 : 'Movies',
        31 : 'Anime/Animation',
        32 : 'Action/Adventure',
        33 : 'Classics',
        34 : 'Comedy',
        35 : 'Documentary',
        36 : 'Drama',
        37 : 'Family',
        38 : 'Foreign',
        39 : 'Horror',
        40 : 'Sci-Fi/Fantasy',
        41 : 'Thriller',
        42 : 'Shorts',
        43 : 'Shows',
        44 : 'Trailers'
    }

    def __init__(self, *args, **kwargs):
        
        key = open('key.json', 'r')
        self.DEVELOPER_KEY = json.load(key)
        key.close()


        api_service_name = "youtube"
        api_version = "v3"

        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey = self.DEVELOPER_KEY)

        self.checkRestart()
        if self.resume:
            try:
                restartFile = open('resume.json', 'r')
            except FileNotFoundError:
                print('resume.json does not exist, exiting...')
                raise
            self.resume_json = json.load(restartFile)
            self.csvName = self.resume_json['csv']
            self.currentTimeStamp = self.resume_json['currentTime']
            self.userID = self.resume_json['userID']

            print('Reopening %s...' % self.csvName)
            self.csv_file = open(self.csvName, 'a', newline="")
            self.csv_writer = csv.writer(self.csv_file)

        else:
            self.url = self.getUrlInput()
            self.fullSearch = self.theDanger()

            #Driver starter
            self.chooseBrowser()
            self.loadBrowser()
            
            print('Opening %s...' % self.url)
            self.driver.get(self.url)
            print('Open complete.')
            time.sleep(1)

            #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

            api_service_name = "youtube"
            api_version = "v3"

            self.youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey = self.DEVELOPER_KEY)

            currentDateTime = datetime.datetime.now()    
            currentYear = str(currentDateTime.year)
            currentMonth = str(currentDateTime.month)
            currentDay = str(currentDateTime.day)
            currentHour = str(currentDateTime.hour)
            currentMinute = str(currentDateTime.minute)
            self.currentTimeStamp = currentYear + currentMonth + currentDay + currentHour + currentMinute


            self.userID = self.getCsvName(self.url)
            self.csvName = self.userID + '_' + self.currentTimeStamp +'_scrape.csv'
            print('Creating %s...' % self.csvName)
            self.csv_file = open(self.csvName, 'w', newline="")
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow([
                                    'Video',
                                    'Tags',
                                    'Likes',
                                    'Dislikes',
                                    'Like/Dislike Ratio',
                                    'Date Published',
                                    'Time Published',
                                    'Views',
                                    'Category',
                                    'NumComments',
                                    'URL'
                                    ])

    def processPageInfo(self, url, count):
        print("\nScanning page #%d, %s" % (count, url))

        video = self.apiGetVideo(url)

        #vidname
        vidName = self.getVideoName(video)
        print("NAME:\t\t%s" % vidName)

        #vidTags
        vidTags = self.getVideoTags(video)
        print("TAGS:\t\t" + str(vidTags))

        #vidLikes
        vidLikes = self.getVideoLikes(video)
        print("LIKES:\t\t%d" % vidLikes)
        
        #vidDislikes
        vidDislikes = self.getVideoDislikes(video)
        print("DISLIKES:\t%d" % vidDislikes)

        vidLiked = vidLikes / vidDislikes
        vidLiked = round(vidLiked, 2)
        print("RATIO:\t\t%.2f" % vidLiked)

        #vidDatePub
        vidDatePub = self.getDatePublished(video)
        print("DATE:\t\t%s" % vidDatePub['date'])
        print("TIME:\t\t%s" % vidDatePub['time'])

        #vidNumViews
        vidNumViews = self.getVideoViews(video)
        print("VIEWS:\t\t%d" % vidNumViews)
        
        #vidNumViews
        vidCategory = self.getVideoCategory(video)
        print("CATEGORY:\t%s" % vidCategory)  

        #vidNumComments
        vidNumComments = self.getNumComments(video)
        print("COMMENTS:\t%d" % vidNumComments)

        
        #csv output
        try:
            self.csv_writer.writerow([
            vidName,
            vidTags, 
            vidLikes,
            vidDislikes,
            vidLiked,
            vidDatePub['date'],
            vidDatePub['time'],
            vidNumViews,
            vidCategory,
            vidNumComments,
            url])
        except Exception as e:
            print(e)
            self.csv_writer.writerow(['ERROR'])
        
        #json output
        self.data.append({
                    'Video': vidName,
                    'Tags' : vidTags,
                    'Likes': vidLikes,
                    'Dislikes': vidDislikes,
                    'Like/Dislike Ratio': vidLiked,
                    'Date Published': vidDatePub['date'],
                    'Time Published': vidDatePub['time'],
                    'Views': vidNumViews,
                    'Category': vidCategory,
                    'NumComments': vidNumComments,
                    'URL': url
                    })
        
    def apiGetVideo(self, url):
        vidId = re.match('https://www.youtube.com/watch\?v=(.*)', url).group(1)
        request = self.youtube.videos().list(
            part="snippet,statistics",
            id=vidId
        )
        response = request.execute()
        return response['items'][0]

    def getVideoName(self, video):
        return video['snippet']['title']
    
    def getVideoTags(self, video):
        return video['snippet']['tags']

    def getVideoLikes(self, video):
        return int(video['statistics']['likeCount'])

    def getVideoDislikes(self, video):
        dislikesCount = video['statistics']['dislikeCount']
        if (dislikesCount == 0):
            return 1
        return int(dislikesCount)

    def getDatePublished(self, video):
        date = video['snippet']['publishedAt']
        datePublished = re.match('(.*)T(.*)', date)
        timePublished = re.match('([0-9]{2}:[0-9]{2}:[0-9]{2})(.*)',
                        datePublished.group(2)).group(1)
        published = {'date' : datePublished.group(1), 'time' : timePublished}
        return published

    def getVideoViews(self, video):
        return int(video['statistics']['viewCount'])

    def getVideoCategory(self, video):
        catId =  int(video['snippet']['categoryId'])
        return self.videoCategories[catId]

    def getNumComments(self, video):
        return int(video['statistics']['commentCount'])

    def getUrlInput(self):
        defaultUrl = 'https://www.youtube.com/user/LinusTechTips/videos'
        print('Welcome!\nPlease enter a valid Youtube channel.')
        userUrl = input("Example: %s\n:" % defaultUrl)
        if (re.match("https://www.youtube.com/user/.*/videos", userUrl) or
            re.match("https://www.youtube.com/channel/.*/videos", userUrl)):
            print("Good URL")
        elif (re.match("https://www.youtube.com/user/.*", userUrl) or
            re.match("https://www.youtube.com/channel/.*", userUrl)):
            userUrl += '/videos'
            print("Good URL")
        elif (userUrl == ""):
            print("Defaulting to %s" % defaultUrl)
            userUrl = defaultUrl
        else:
            print("Bad URL\nDefaulting to %s" % defaultUrl)
            userUrl = defaultUrl
        return userUrl

    def theDanger(self):
        choice = False
        checkOne = input("Do you want to enable full channel searching? y/n: ")
        if (checkOne.lower() == 'y'):
            choice = True
        return choice

    def getMaxItems(self):
        check = input("Would you like to set a cap on the number of times the page is scrolled down? y/n: ")
        if (check == 'y'):
            max = input("Enter max: ")
            try:
                value = int(max)
            except ValueError:
                print("Invalid number, defaulting to 10")
                value = 10
        else:
            value = -1
        return value

    def loadFullPage(self, cap):
        end = False
        count = 0
        while(not end):
            if (cap != -1):
                if (count >= cap):
                    break
            height = self.driver.execute_script("return document.documentElement.scrollHeight")
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight)")
            print('scrolled down... %d' % count)
            time.sleep(1)
            newHeight = self.driver.execute_script("return document.documentElement.scrollHeight")

            if (height == newHeight):
                #if reached the bottom, wait 3 seconds and make sure
                time.sleep(3)
                height = self.driver.execute_script("return document.documentElement.scrollHeight")
                self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight)")
                time.sleep(1)
                newHeight = self.driver.execute_script("return document.documentElement.scrollHeight")
                if (height == newHeight):
                    end = True
            count += 1
            
        time.sleep(5)
    
    def getCsvName(self, url):
        return re.match("https://www.youtube.com/user/(.*)/videos", url).group(1)

    def getPageURL(self):
        return self.driver.current_url
    
    def chooseBrowser(self):
        """choice = input('Enter \'C\' for Google Chrome (Recommended) or \'F\' for Mozilla Firefox: ')
        choice = choice.lower()

        if choice == 'c':
            self.Choice_Chrome = True
        elif choice == 'f':
            self.Choice_FF = True
        else:
            self.Choice_Chrome = True
        """
        self.Choice_FF = True

    def loadBrowser(self):
    
        self.driver = None
        self.wait = None

        if self.Choice_Chrome:
            print('loading Chrome...')
            #Chrome options
            chrome_ops = webdriver.ChromeOptions()
            chrome_ops.add_argument('--headless')
            chrome_ops.add_argument('--disable-gpu')
            chrome_ops.add_argument('log-level=3')
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_ops.add_experimental_option("prefs", prefs)

            self.driver = webdriver.Chrome(options=chrome_ops)

        elif self.Choice_FF:
            print('loading Firefox...')
            #Firefox options
            ff_ops = Options()
            ff_ops.headless = True
            ff_prof = webdriver.FirefoxProfile()
            ff_prof.set_preference('permissions.default.image', 2)
            ff_prof.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
            ff_prof.set_preference('media.autoplay.enabled', 'false')

            self.driver = webdriver.Firefox(firefox_profile=ff_prof, options=ff_ops)

        self.wait = WebDriverWait(self.driver, 30)

    def checkRestart(self):
        check = input('Restart from previous scrape? y/n: ')
        check = check.lower()
        if check == 'y':
            self.resume = True

    def run(self):
        if (self.fullSearch):
            cap = self.getMaxItems()
            self.loadFullPage(cap)
        
        userVideoList = self.driver.find_elements_by_xpath('//*[@id="video-title"]')
        print("Found %d videos..." % len(userVideoList))
        videoLinks = []
        if (len(userVideoList) > 0):
            try:
                print('Aquiring URLs...')
                for i in userVideoList:
                    #try:
                    videoLinks.append(i.get_attribute('href'))
                    #except Exception as e:
                    #print('element\n' + i + '\nHas no href.')            
                count = 0
                try:
                    self.driver.quit()
                except Exception as e:
                    print(e)
                    print('Couldn\'t close driver')

                print('Starting...')
                for i in videoLinks:
                    try:
                        self.processPageInfo(i, count)
                    except googleapiclient.errors.HttpError as h:
                        with open('resume.json', 'w') as outfile:
                            json.dump({
                                    'csv' : self.csvName,
                                    'currentTime' : self.currentTimeStamp,
                                    'userID' : self.userID, 
                                    'index' : count,
                                    'videos' : videoLinks
                                    }, outfile)
                            print('MAX API CALLS REACHED')
                            print('Dumped index and video list to resume.json...')
                            print('exiting...')
                            break
                    except Exception as e:
                        print(e)
                        print('An error has occurred, continuing...')    
                    count += 1
            except Exception as e:
                print(e)
                print('An error has occured, exiting...')

        print('Pausing for 5 seconds...')
        time.sleep(5)

        jsonName = self.userID + '_' + self.currentTimeStamp +'_scrape.json'
        print('Dumping %d data entires to json %s...' % (len(self.data), jsonName))
        with open(jsonName, 'w') as outfile:
            json.dump(self.data, outfile)
        print('Done!')

    def runResume(self):
        videoLinks = self.resume_json['videos']
        count = self.resume_json['index']
        print('Resuming from a list of %d videos from %s at index %d...' % (len(videoLinks), self.userID, count))
        time.sleep(2)

        apiLimit = False

        if (len(videoLinks) > 0):
            try:           
                print('Starting...')
                for i in range(len(videoLinks)):
                    if i < count:
                        continue
                    try:
                        self.processPageInfo(videoLinks[i], count)
                    except googleapiclient.errors.HttpError as h:
                        with open('resume.json', 'w') as outfile:
                            json.dump({
                                    'csv' : self.csvName,
                                    'currentTime' : self.currentTimeStamp,
                                    'userID' : self.userID, 
                                    'index' : count,
                                    'videos' : videoLinks
                                    }, outfile)
                            print('MAX API CALLS REACHED')
                            print('Dumped index and video list to resume.json...')
                            print('exiting...')
                            apiLimit = True
                            break
                    except Exception as e:
                        print(e)
                        print('An error has occurred, continuing...')    
                    count += 1
            except Exception as e:
                print(e)
                print('An error has occured, exiting...')

        if (not apiLimit):
            os.remove('resume.json')

        print('Pausing for 5 seconds...')
        time.sleep(5)

        jsonName = self.userID + '_' + self.currentTimeStamp +'_scrape.json'
        print('Dumping %d data entires to json %s...' % (len(self.data), jsonName))
        with open(jsonName, 'a') as outfile:
            json.dump(self.data, outfile)
        print('Done!')

    def main(self):
        if (self.resume):
            self.runResume()
        else:
            self.run()
        self.csv_file.close()

if __name__ == '__main__':
    try:
        scraper = ScrapeYoutube2()
        scraper.main()
    except FileNotFoundError:
        print('Goodbye')
