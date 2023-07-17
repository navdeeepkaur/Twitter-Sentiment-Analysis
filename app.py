from flask import Flask, render_template, request, url_for, Response
from flask_bootstrap import Bootstrap
from textblob import TextBlob, Word
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import time
import random
import getpass
import pandas as pd
pd.options.display.max_colwidth=1000
import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from wordcloud import WordCloud
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
import matplotlib.pyplot as plt
#import seaborn as sns

app=Flask(__name__)
Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyse', methods=['POST'])
def analyse():
    my_user="" #your username here
    my_pass="" #your password here
    sleep(3)
    if request.method=='POST':
        search_item=request.form['rawtext']
    #search_item="Liz Truss"
    PATH="C\\Users\hp\Downloads\chromedriver_win32"
    driver=webdriver.Chrome(PATH)
    driver.get("http://twitter.com/i/flow/login")
    sleep(3)
    user_id=driver.find_element(By.XPATH,"//input[@type='text']")
    user_id.send_keys(my_user)
    user_id.send_keys(Keys.ENTER)
    sleep(3)
    password=driver.find_element(By.XPATH,"//input[@type='password']")
    password.send_keys(my_pass)
    password.send_keys(Keys.ENTER)
    sleep(3)
    search_box=driver.find_element(By.XPATH,"//input[@data-testid='SearchBox_Search_Input']")
    search_box.send_keys(search_item)
    search_box.send_keys(Keys.ENTER)
    all_tweets=set()
    tweets=driver.find_elements(By.XPATH,"//div[@data-testid='tweetText']")
    while True:
        for tweet in tweets:
            all_tweets.add(tweet.text)
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        sleep(3)
        tweets=driver.find_elements(By.XPATH,"//div[@data-testid='tweetText']")
        if len(list(all_tweets))>50:
            break
    all_tweets=list(all_tweets)
    stp_words=list(stopwords.words('english'))
    df=pd.DataFrame(all_tweets,columns=['tweets'])
    def TweetCleaning(tweet):
        cleanTweet=re.sub(r"@[a-zA-Z0-9]+","",tweet)
        cleanTweet=re.sub(r"#[a-zA-Z0-9\s]+","",cleanTweet)
        cleanTweet=cleanTweet.lower()
        cleanTweet=' '.join(word for word in cleanTweet.split() if word not in stp_words)
        return cleanTweet
    df['cleanedTweets']=df['tweets'].apply(TweetCleaning)
    def calPolarity(tweet):
        return TextBlob(tweet).sentiment.polarity
    def calSubjectivity(tweet):
        return TextBlob(tweet).sentiment.subjectivity
    df['tpolarity']=df['cleanedTweets'].apply(calPolarity)
    df['tsubjectivity']=df['cleanedTweets'].apply(calSubjectivity)
    def segmentation(tweet):
        if tweet>0:
            return "positive"
        elif tweet==0:
            return "neutral"
        else:
            return "negative"
    df['segmentation']=df['tpolarity'].apply(segmentation)
    df.pivot_table(index=['segmentation'],aggfunc={'segmentation':'count'})
    positive=round(len(df[df.segmentation=='positive'])/len(df)*100,1)
    negative=round(len(df[df.segmentation=='negative'])/len(df)*100,1)
    neutral=round(len(df[df.segmentation=='neutral'])/len(df)*100,1)
    return render_template('index.html', positive=positive, negative=negative, neutral=neutral, search_item=search_item)

if __name__ == '__main__':
	app.run(debug=True)
        
