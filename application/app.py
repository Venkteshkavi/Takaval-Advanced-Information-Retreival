# -*- coding: utf-8 -*-
# bootcamp.xobin.com
from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from flask import Flask
from flask import render_template, flash, redirect, session, url_for,send_from_directory, request, json, make_response, g
from decorators import isloggedin
from flask.json import jsonify
from flask_assets import Environment, Bundle
from urlparse import urlparse, urlunparse
import string,os
import MySQLdb,datetime,ast,time,random,gc
from MySQLdb import escape_string as thwart
from datetime import date, timedelta
import json
import csv

import pandas, pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier

import nltk
import re
from nltk.corpus import stopwords as stemStops
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer as ss

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer_1
from sumy.summarizers.lex_rank import LexRankSummarizer as Summarizer_2
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from afinn import Afinn

from string import punctuation
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_lg
import en_core_web_sm
import requests
import json

import datefinder
import datetime

from newsplease import NewsPlease

class User(object):

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, phash, password):
        return check_password_hash(phash, password)

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config.from_envvar('TAKAVAL_CONFIG',silent=True)
angular_assets = Environment(app)

bundles = {
    'angular_js': Bundle(
        'angular/ang/mainAng.js',
        'angular/ang/controllers.js',
        'angular/ang/services.js',
        'angular/ang/filters.js',
        output='opt/ang.js',filters='jsmin'),

    'angular_css': Bundle(
        'assets/css/custom.css',
        output='opt/ang.css',filters='cssmin')
}
angular_assets.register(bundles)

loaded_vec = CountVectorizer(vocabulary=pickle.load(open("models/count_vector.pkl", "rb")))
loaded_tfidf = pickle.load(open("models/tfidf.pkl","rb"))
loaded_model = pickle.load(open("models/nb_model.pkl","rb"))
clf_neural = pickle.load(open("models/softmax.pkl","rb"))
category_list = ["Riots", "Protests", "Violence against civilians", "Others"]
election_roots = ['elect', 'poll', 'ballot', 'by-elect', 'vote', 'soapbox', 'teller']
nlp = en_core_web_lg.load()
stopwords = spacy.lang.en.stop_words.STOP_WORDS
weekdays = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
search_to_category = {
    'Riots': 'riot',
    'Protests': 'protest',
    'Violence against civilians': 'violence',
    'Others': ''
}

@app.route('/')
def home():
    return render_template('main/index.html')

@app.route('/data')
def the_data():
    return render_template('main/data.html')

@app.route('/get/india-today', methods=['POST'])
def get_indiaTopNews():
    # today = "2019-05-04"
    today = "detikRiot_new"
    data = pandas.read_csv("crawled_articles/"+today+".csv")
    resp = []
    contents = data.content.tolist()[1:]
    titles = data.title.tolist()[1:]
    url = data.url.tolist()[1:]
    for c, t, u in zip(contents, titles, url):
        if c is None or t is None or url is None or isinstance(c, float):
            continue
        r = {}
        summary = summarizer_lsa(c,u)
        # summary = summary.decode('utf-8').strip()
        sentiment = detect_sentiment(summary)
        topic = topic_classify(summary)
        r['election'] = isElection(summary)
        r['content'] = c
        r['summary'] = summary
        r['topic'] = topic
        r['title'] = t
        r['sentiment'] = sentiment
        resp.append(r)
    return jsonify(news=resp)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('main/404.html'), 404

@app.route('/page-not-found')
def page_not_found():
    return render_template('main/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(error)
    return render_template('main/500.html'), 500

################################################################################
###############################Dashboard########################################
################################################################################

@app.route('/dashboard')
@app.route('/analytics')
@app.route('/crawl-index')
@app.route('/crawl')
def dashboard(**kwargs):
    return render_template('dash/dashboardBase.html')

@app.route('/get/dashboard-data', methods=['POST'])
def get_dashboardData():
    dbql,cursor = con()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data`"""
    cursor.execute(csql)
    totalCount = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `topic`='riot'"""
    cursor.execute(csql)
    totalRiotCount = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `topic`='protest'"""
    cursor.execute(csql)
    totalProtestCount = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `topic`='violence'"""
    cursor.execute(csql)
    totalViolenceCount = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `src`='thehindu'"""
    cursor.execute(csql)
    totalHinduCount = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `src`='timesofindia' OR `src`='timesofindia.indiatimes'"""
    cursor.execute(csql)
    totalTimesCount = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `src`='ndtv'"""
    cursor.execute(csql)
    totalNDTVCount = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `src`='detik'"""
    cursor.execute(csql)
    totalDetikCount = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE (`src`='thehindu' OR `src`='timesofindia' OR `src`='ndtv' OR `src`='timesofindia.indiatimes') AND `topic`='riot'"""
    cursor.execute(csql)
    totalIndiaRiot = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE (`src`='thehindu' OR `src`='timesofindia' OR `src`='ndtv' OR `src`='timesofindia.indiatimes') AND `topic`='protest'"""
    cursor.execute(csql)
    totalIndiaProtest = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE (`src`='thehindu' OR `src`='timesofindia' OR `src`='ndtv' OR `src`='timesofindia.indiatimes') AND `topic`='violence'"""
    cursor.execute(csql)
    totalIndiaViolence = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `src`='detik' AND `topic`='riot'"""
    cursor.execute(csql)
    totalIndonesiaRiot = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `src`='detik' AND `topic`='protest'"""
    cursor.execute(csql)
    totalIndonesiaProtest = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `src`='detik' AND `topic`='violence'"""
    cursor.execute(csql)
    totalIndonesiaiolence = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `classified_topic`='Riots'"""
    cursor.execute(csql)
    totalRiotCount_predicted = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `classified_topic`='Protests'"""
    cursor.execute(csql)
    totalProtestCount_predicted = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `classified_topic`='Violence against civilians'"""
    cursor.execute(csql)
    totalViolenceCount_predicted = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `sentiment`='True'"""
    cursor.execute(csql)
    totalSentiment_true = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `sentiment`='False'"""
    cursor.execute(csql)
    totalSentiment_false = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `classified_topic` IN ('Riots', 'Protests', 'Violence against civilians')"""
    cursor.execute(csql)
    totalCorrectClassified = cursor.fetchall()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data` WHERE `classified_topic` IN ('Others', '')"""
    cursor.execute(csql)
    totalInCorrectClassified = cursor.fetchall()
    counts = {
        'total':totalCount[0][0],
        'riot':totalRiotCount[0][0],
        'protest':totalProtestCount[0][0],
        'violence':totalViolenceCount[0][0],
        'hindu':totalHinduCount[0][0],
        'times':totalTimesCount[0][0],
        'ndtv':totalNDTVCount[0][0],
        'detik':totalDetikCount[0][0],
        'india':totalHinduCount[0][0]+totalNDTVCount[0][0]+totalTimesCount[0][0],
        'indonesia':totalDetikCount[0][0],
        'thailand': 0,
        'indiaRiot':totalIndiaRiot[0][0],
        'indiaProtest':totalIndiaProtest[0][0],
        'indiaViolence':totalIndiaViolence[0][0],
        'indonesiaRiot':totalIndonesiaRiot[0][0],
        'indonesiaViolence':totalIndonesiaiolence[0][0],
        'indonesiaProtest':totalIndonesiaProtest[0][0],
        'totalRC_pred': totalRiotCount_predicted[0][0],
        'totalPC_pred': totalProtestCount_predicted[0][0],
        'totalVC_pred': totalViolenceCount_predicted[0][0],
        'totalSent_true': totalSentiment_true[0][0],
        'totalSent_false': totalSentiment_false[0][0],
        'totalCorrect_class': totalCorrectClassified[0][0],
        'totalInCorrect_class': totalInCorrectClassified[0][0]
    }
    return jsonify(counts=counts)


@app.route('/get/crawl-index', methods=['POST'])
def get_crawlIndexData():
    data = json.loads(request.data.decode('utf-8'))
    startIndex = data['startIndex']
    limit = data['limit']
    dbql,cursor = con()
    csql = """SELECT COUNT(cid) FROM `takaval`.`takaval_data`"""
    cursor.execute(csql)
    totalCount = cursor.fetchall()
    gsql = """SELECT * FROM `takaval`.`takaval_data` ORDER BY `cid` ASC LIMIT %s, %s"""
    cursor.execute(gsql,[int(startIndex),int(limit)])
    cdata = cursor.fetchall()
    carray = []
    for c in cdata:
        cdict = {}
        cdict["id"] = c[0]
        cdict['title'] = c[1]
        cdict['url'] = c[2]
        cdict['topic'] = c[3]
        cdict['pubDate'] = c[4]
        cdict['dateObj'] = c[5]
        cdict['src'] = c[6]
        cdict['lang'] = c[7]
        cdict['og_title'] = c[8]
        
        carray.append(cdict)
    return jsonify(cdata = carray,totalCount=totalCount)


@app.route('/get/all-data', methods=['POST'])
def get_allData():
    data = json.loads(request.data.decode('utf-8'))
    startIndex = data['startIndex']
    limit = data['limit']
    country = data['country']
    fromDate = data['fromDate']
    toDate = data['toDate']
    topic = data['topic']
    election = data['election']
    fromDateObj = datetime.datetime.strptime(fromDate, '%Y-%m-%d')
    toDateObj = datetime.datetime.strptime(toDate, '%Y-%m-%d')

    if topic != 'all':
        topic = [topic]
    else:
        topic = ['Riots', 'Protests', 'Violence against civilians', 'Others']
    
    if country != 'all':
        country = [country]
    else:
        country = ['India', 'Indonesia', 'Thailand', '']    
    
    if election != 'all':
        election = [election]
    else:
        election = ['True', 'False'] 

    dbql,cursor = con()
    csql = """SELECT COUNT(`cid`) FROM `takaval`.`takaval_data` WHERE `isProcessed`=%s AND `classified_topic` IN %s AND `country` IN %s 
    AND `election` IN %s AND `dateObject` BETWEEN %s AND %s"""
    cursor.execute(csql,[1, topic, country, election, fromDateObj, toDateObj])
    totalCount = cursor.fetchall()
    gsql = """SELECT * FROM `takaval`.`takaval_data` WHERE `isProcessed`=%s AND `classified_topic` IN %s AND `country` IN %s 
    AND `election` IN %s AND `dateObject` BETWEEN %s AND %s ORDER BY `cid` DESC LIMIT %s, %s"""
    cursor.execute(gsql,[1, topic, country, election, fromDateObj, toDateObj, int(startIndex),int(limit)])
    cdata = cursor.fetchall()
    carray = []
    for c in cdata:
        try:
            cdict = {}
            cdict["id"] = c[0]
            cdict['title'] = c[1].decode('utf-8')
            cdict['url'] = c[2]
            cdict['topic'] = c[3].decode('utf-8')
            cdict['pubDate'] = c[4]
            cdict['dateObj'] = c[5]
            cdict['src'] = c[6]
            cdict['lang'] = c[7]
            cdict['og_title'] = c[8].decode('utf-8')
            cdict['content'] = c[9].decode('utf-8')
            cdict['summary'] = c[11].decode('utf-8')
            cdict['election'] = c[12]
            cdict['sentiment'] = c[13]
            cdict['event_date'] = c[14].decode('utf-8')
            cdict['org1'] = c[15].decode('utf-8')
            cdict['org2'] = c[16].decode('utf-8')
            cdict['actor1'] = c[17].decode('utf-8')
            cdict['actor2'] = c[18].decode('utf-8')
            cdict['country'] = c[19].decode('utf-8')
            cdict['admin1'] = c[20].decode('utf-8')
            cdict['admin2'] = c[21].decode('utf-8')
            cdict['admin3'] = c[22].decode('utf-8')
            cdict['admin4'] = c[23].decode('utf-8')
            cdict['classified_topic'] = c[24]
            carray.append(cdict)
        except:
            pass
    return jsonify(cdata = carray,totalCount=totalCount)

@app.route('/csvtodb')
def csvtodb():
    # files = [
    # {
    #     'name':'crawled_articles/detikRiot_new.csv',
    #     'topic':'riot',
    #     'src':'detik',
    #     'lang':'id'	 
    # },
    # {
    #     'name':'crawled_articles/ndtvRiot_new.csv',
    #     'topic':'riot',
    #     'src':'ndtv',
    #     'lang':'en'	 
    # },
    # {
    #     'name':'crawled_articles/timesRiot_new.csv',
    #     'topic':'riot',
    #     'src':'timesofindia',
    #     'lang':'en'	 
    # },
    # {
    #     'name':'crawled_articles/detikProtest_new.csv',
    #     'topic':'protest',
    #     'src':'detik',
    #     'lang':'id'	 
    # },
    # {
    #     'name':'crawled_articles/ndtvProtest_new.csv',
    #     'topic':'protest',
    #     'src':'ndtv',
    #     'lang':'en'	 
    # },
    # {
    #     'name':'crawled_articles/timesProtest_new.csv',
    #     'topic':'protest',
    #     'src':'timesofindia',
    #     'lang':'en'	 
    # },
    # {
    #     'name':'crawled_articles/detikViolence_new.csv',
    #     'topic':'violence',
    #     'src':'detik',
    #     'lang':'id'	 
    # },
    # {
    #     'name':'crawled_articles/ndtvViolence_new.csv',
    #     'topic':'violence',
    #     'src':'ndtv',
    #     'lang':'en'	 
    # },
    # {
    #     'name':'crawled_articles/timesViolence_new.csv',
    #     'topic':'violence',
    #     'src':'timesofindia',
    #     'lang':'en'	 
    # }]
    files = [{
        'name':'crawled_articles/manual.csv',
        'topic':'violence',
        'src':'timesofindia',
        'lang':'en'
    }]
    for f in files:
        filename = f['name']
        file = open(filename, "rU")
        reader = csv.reader(file)
        next(reader)
        dbql,cursor = con()
        for column in reader:
            title = column[0].strip()
            og_title = column[1].strip()
            url = column[2].strip()
            content = column[4].strip()
            if content == "" or title == "" or og_title == "" or url == "":
                continue
            lang = column[3].strip()
            pubDate =  column[5]
            dateObj = datetime.datetime.strptime(column[6], "%Y-%m-%d %H:%M:%S")
            topic = f['topic']
            # topic = ''
            src = column[7]
        #     msql = """INSERT INTO `takaval`.`takaval_data` ( `cid`, `title`,`url`, `topic`, `publishedDate`,`dateObject`,`src`, `lang`, `og_title`, `content`) VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        #     cursor.execute(msql,[title,url,topic,pubDate,dateObj,src,lang, og_title, content])
        #     dbql.commit()
        # dbql.close()
    return "done"

@app.route('/process-articles')
def process_articles():
    dbql,cursor = con()
    dbql.set_character_set('utf8')
    sql = """ SELECT * FROM `takaval_data` WHERE `isProcessed`=0 LIMIT 500"""
    cursor.execute(sql)
    crawl_data = cursor.fetchall()
    output = []
    for c in crawl_data:
        od = {}
        od['cid'] = c[0]
        od['content'] = c[9]
        od['title'] = c[1]
        od['url'] = c[2]
        od['search_term'] = c[3]
        od['published_date'] = c[4]
        od['source'] = c[6]
        od['language'] = c[7]
        summary = summarizer_lsa(c[9],c[2])
        od['summary'] = summary
        sentiment = detect_sentiment(summary)
        od['sentiment'] = sentiment
        topic = topic_classify(summary)
        od['classified_topic'] = topic
        if od['search_term'] == '':
            od['search_term'] = search_to_category[topic]
        od['election'] = isElection(summary)
        od['events'] = event_extraction_process(c[9], c[5], topic)
        event_date = ""
        event_org_1 = ""
        event_org_2 = ""
        event_country = ""
        event_actor_1 = ""
        event_actor_2 = ""
        event_admin_1 = ""
        event_admin_2 = ""
        event_admin_3 = ""
        event_admin_4 = ""

        if len(od['events']['date']) > 0:
            event_date = od['events']['date'][0]

        if len(od['events']['org1']) > 0:
            event_org_1 = od['events']['org1'][0].encode('utf-8').strip()

        if len(od['events']['org2']) > 0:
            event_org_2 = od['events']['org2'][0].encode('utf-8').strip()

        if len(od['events']['country']) > 0:
            event_country = od['events']['country'][0].encode('utf-8').strip()

        if len(od['events']['actor1']) > 0:
            event_actor_1 = od['events']['actor1'][0].encode('utf-8').strip()
        
        if len(od['events']['actor2']) > 0:
            event_actor_1 = od['events']['actor2'][0].encode('utf-8').strip()

        if len(od['events']['admin1']) > 0:
            event_admin_1 = od['events']['admin1'][0].encode('utf-8').strip()

        if len(od['events']['admin2']) > 0:
            event_admin_2 = od['events']['admin2'][0].encode('utf-8').strip()

        if len(od['events']['admin3']) > 0:
            event_admin_3 = od['events']['admin3'][0].encode('utf-8').strip()

        if len(od['events']['admin4']) > 0:
            event_admin_4 = od['events']['admin4'][0].encode('utf-8').strip()
        
        print(event_date, event_org_1, event_org_2, event_country, event_actor_1, event_actor_2, event_admin_1, event_admin_2, event_admin_3, event_admin_4)
        usql = """UPDATE `takaval_data` SET `topic`=%s, `summary`=%s, `election`=%s, `sentiment`=%s, `event_date`=%s, `org1`=%s, `org2`=%s, `country`=%s,
                `actor1`=%s, `actor2`=%s, `admin1`=%s, `admin2`=%s, `admin3`=%s, `admin4`=%s, `classified_topic`=%s, `isProcessed` = %s WHERE `cid` = %s"""
        cursor.execute(usql,[od['search_term'], summary, str(od['election']), str(sentiment), str(event_date), str(event_org_1), str(event_org_2), str(event_country),
                        str(event_actor_1), str(event_actor_2), str(event_admin_1), str(event_admin_2), str(event_admin_3), str(event_admin_4), str(topic), 1, int(c[0])])
        dbql.commit()
        output.append(od)
    return jsonify(data=output)

@app.route('/custom-crawl-articles')
def custom_crawl_articles():
    url_file = open('crawled_urlIndex/manual_urls.txt', 'r')
    urls = []
    counter = 0
    for line in url_file.readlines():
        counter += 1
        print(counter) 
        try:
            cdata = {}
            article = NewsPlease.from_url(line.strip())
            purl = urlparse(line)
            cdata['src'] = str(purl.netloc.replace("www.", "").replace(".com", ""))
            cdata['url'] = line.strip()
            cdata['title'] = article.title.encode('utf-8').strip()
            cdata['og_title'] = article.title.encode('utf-8').strip()
            cdata['content'] = article.text.encode('utf-8').strip()
            cdata['lang'] = article.language.encode('utf-8').strip()
            adate = article.date_publish
            if adate is None:
                continue
            dateObj = datetime.datetime.strptime(str(adate), "%Y-%m-%d %H:%M:%S")
            publisedDate = dateObj.strftime("%d %b %Y")
            cdata['dateObj'] = dateObj
            cdata['publishedDate'] = publisedDate
            urls.append(cdata)
        except:
            continue
    json_to_csv(urls)
    return jsonify(data=urls)


################################################################################
################################FUNCTIONS#######################################
################################################################################

def con():
    dbql = MySQLdb.connect(app.config['DB_SERVER_NAME'],app.config['DB_USER_NAME'],app.config['DB_PASS'],app.config['DB_NAME'])
    cursor = dbql.cursor()
    return dbql,cursor

def days_between_with_time_no_abs(d1,d2):
    from datetime import datetime
    d1 = datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
    return (d2 - d1).days

def getData():
    try:
        dbql,cursor = con()
        sql = """ SELECT * FROM `takaval_data` ORDER BY `cid` DESC"""
        cursor.execute(sql)
        crawl_data = cursor.fetchall()
        dbql.close()
        gc.collect()
        cdata = []
        for c in crawl_data:
            cdict = {}
            cdict['crawl_id'] = c[0]
            cdict['crawl_src'] = str(c[1])
            cdata.append(cdict)
        return cdata
    except:
        raise "Error while retrieving!"

def json_to_csv(jsondata):
    f = csv.writer(open("crawled_articles/manual.csv", "wb+"))
    f.writerow(["title", "og_title", "url", "lang", "content", "publishedDate", "dateObject", "src"])
    for j in jsondata:
        f.writerow([j["title"],
                    j["og_title"],
                    j["url"],
                    j["lang"],
                    j["content"],
                    j['publishedDate'],
                    j['dateObj'],
                    j['src']])
    return "success"
################################################################################

def stem(sentence):
    words = word_tokenize(sentence)
    final = []
    sb = ss("english")
    for w in words:
        if w not in stemStops.words('english'):
            root = sb.stem(w)
            final.append(root)
    return u" ".join(final)


def summarizer_lsa(text, url):
    LANGUAGE = "english"
    SENTENCES_COUNT = 3
    # parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    sum_output = u""
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer_1(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        sum_output += u" ".join(sentence.words)
        sum_output += u". "
    return sum_output

def detect_sentiment(text):
    af = Afinn()
    polarity = af.score(text)
    if(polarity < 0):
        outcome = True
    elif(polarity == 0):
        outcome = True
    else:
        outcome = False
    return outcome

def topic_classify(text):
    input_text = stem(text)
    input_text = [input_text]
    X_new_counts = loaded_vec.transform(input_text)
    X_new_tfidf = loaded_tfidf.transform(X_new_counts)
    predicted = clf_neural.predict(X_new_tfidf)
    topic = category_list[predicted[0]]
    return topic

def isElection(text):
    stems = stem(text)
    words = word_tokenize(stems)
    for e in election_roots:
        if e in words:
            return True
    return False

def get_full_text(token):
    full_text = ""
    for child_token in token.children:
        full_text = full_text + " "+child_token.text
    full_text = full_text + " "+ token.text
    text_tokens = full_text.split(" ")
    filterd_tokens = []
    for token in text_tokens:
        if(token not in stopwords):
            filterd_tokens.append(token)
    full_text = " ".join(filterd_tokens)
    return full_text

def extract_event_attribute(event, token, side):

    full_text = get_full_text(token)

    isLeft = (side == "left")
    ent_type = token.ent_type_
    if(ent_type == ""):
        extract_event_attribute_from_list(event, token.children, side)
    if(ent_type == 'DATE'):
        event['date'].add(full_text)
    elif(ent_type == 'LOC'):
#         print("Going to add token::"+token.text)
        event['location'].add(token.text)
    elif(ent_type == 'GPE'):
#         event['country'] = full_text
        event['location'].add(token.text)
    elif(ent_type == 'CARDINAL'):
        event['fatalities'] = full_text
    elif(ent_type == 'PERSON'):
        attribute_name = "actor2" if "actor1" in event else "actor1"
        event[attribute_name] = full_text
        for child in token.children:
            if(child.dep_ == 'nummod'):
                extract_event_attribute(event, child, side)
    elif(ent_type == 'ORG'):
#         attribute_name = "org2" if "org1" in event else "org1"
        event['org'].add(full_text)
#         event['org'].add(full_text)
        for child in token.children:
            if(child.dep_ == 'nummod'):
                extract_event_attribute(event, child, side)

def extract_event_attribute_from_list(event, tokens, side):
    
    entity_type=""
    full_text=""
    for token in tokens:
        extract_event_attribute(event, token, side)

def extract_event(doc):
    event = {}
    event['location']=set()
    event['date'] = set()
    event['org'] = set()
    for sent in doc.sents:
        short_doc = nlp(sent.text)
#         for ent in short_doc.ents:
#             print(ent.text+"::"+ent.label_)
        for token in short_doc:
            dependency = token.dep_
            if(dependency == "ROOT"):
                for left_token in token.lefts:
                    child_dep = left_token.dep_
                    if(child_dep in('nsubjpass', 'nsubj')):
                        extract_event_attribute(event, left_token,'left')
                    elif(child_dep == 'prep'):
                        extract_event_attribute_from_list(event, left_token.rights, 'left')

                for right_token in token.rights:
                    right_child_dep = right_token.dep_
                    full_text = get_full_text(right_token)
                    if(right_child_dep in('attr','dobj')):
                        extract_event_attribute(event, right_token,'right')
                    elif(right_child_dep == 'prep'):
                        extract_event_attribute_from_list(event, right_token.rights, 'right')
                    elif(right_child_dep == 'agent'):
                        extract_event_attribute_from_list(event, right_token.children, 'right')

            elif(dependency == "pobj"):
                extract_event_attribute(event,token,'right')
#         displacy.render(nlp(str(short_doc)), style='dep', jupyter = True, options = {'distance': 120})
    return event

def is_country_of_interest(addresses):
    for address in addresses:
        area_name = address['long_name']
        address_types = address['types']
        if ('country' in address_types):
            if(area_name in ['India','Indonesia','Thailand']):
                return True
            else:
                return False

def get_location_data(possible_locations):
    location_data = {}
    for location in possible_locations:
        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+location+'&key=AIzaSyAQ4fdgmwd5tNsjI50ZqTIO0LURkXccxzc')
        responseJson = json.loads(response.text)
        results = responseJson['results']
        if(len(results) > 0):
            firstResult = results[0]
            addresses = firstResult['address_components']
#             if the name is the same for admin_level_1, admin_level_2, admin_level_3, then take only admin_level_1
            for address in addresses:
                if(not is_country_of_interest(addresses)):
                    continue
#                 print(address)
                area_name = address['long_name']
                address_types = address['types']
                if ('country' in address_types):
                    location_data['country'] = area_name
                elif ('administrative_area_level_1' in address_types):
                    location_data['administrative_area_level_1'] = area_name
                elif ('administrative_area_level_2' in address_types 
                      and 'administrative_area_level_2' not in location_data):
                    location_data['administrative_area_level_2'] = area_name
                elif('locality' in address_types
                    and 'administrative_area_level_3' not in location_data):
                    location_data['administrative_area_level_3'] = area_name
                elif('sublocality' in address_types
                    and 'administrative_area_level_4' not in location_data):
                    location_data['administrative_area_level_4'] = area_name
#             print(location_data)
                if(len(location_data) == 5):
                   break
    return location_data

def get_organization_data(possible_organizations):
    organization_data = {}
    for org in possible_organizations:
        org = org.strip()
        org = "+".join(org.split(" "))
        response = requests.get('https://kgsearch.googleapis.com/v1/entities:search?query='+org+'&key=AIzaSyAQ4fdgmwd5tNsjI50ZqTIO0LURkXccxzc&limit=5&indent=True')
        responseJson = json.loads(response.text)
        if('itemListElement' in responseJson):
            items = responseJson['itemListElement']
            if(len(items) > 0):
                firstResult = items[0]['result']
                if('name' in firstResult):
                    org_name = firstResult['name']
                    types = firstResult['@type']
                    if('Organization' in types):
                        if(len(organization_data) == 0):
                            organization_data['org1'] = org_name
                        else: 
                            organization_data['org2'] = org_name
            if(len(organization_data) == 2):
                break
    return organization_data

def get_event_date(dates, published_date_str):
    
    published_date = datetime.datetime.strptime(published_date_str, "%Y-%m-%d")
    published_day_of_week = published_date.weekday()
    recent_date = None
    current_min = None
    for date_str in dates:
        event_date = None
        date_str = date_str.lower()
        for day in weekdays:
            if(day in date_str):
                given_day_of_week = weekdays.index(day)
                day_diff = abs(published_day_of_week - given_day_of_week)
                if(day_diff > 0):
                    day_diff = 7-day_diff
                event_date = published_date - datetime.timedelta(days = day_diff)
        if(event_date is None):
            dates = list(datefinder.find_dates(date_str))       
            if(len(dates) > 0):
                event_date = dates[0]
        if(event_date is not None):
            relative_day_diff = abs((published_date - event_date).days)
            if(relative_day_diff == 0):
                recent_date = event_date
                break
            else:
                if(current_min is None or relative_day_diff < current_min):
                    current_min = relative_day_diff
                    recent_date = event_date
    if(recent_date is None):
        recent_date = published_date
    return str(recent_date).split(" ")[0]

def event_extraction_process(text, dateObj, doc_topic):
    final_event_map = dict()
    final_event_map['org1']=[]
    final_event_map['org2']=[]
    final_event_map['actor1']=[]
    final_event_map['actor2']=[]
    final_event_map['date']=[]
    final_event_map['country']=[]
    final_event_map['admin1']=[]
    final_event_map['admin2']=[]
    final_event_map['admin3']=[]
    final_event_map['admin4']=[]
    text = text.decode('utf-8')
    doc = nlp(text)
    published_date_str = dateObj.strftime("%Y-%m-%d")
    if(doc_topic!="Others"):
        print("inside")
        event = extract_event(doc)
        if 'org' in event:
            org_data = get_organization_data(event['org'])
            if 'org1'in org_data:
                final_event_map['org1'].append(org_data['org1'])
            if 'org2' in org_data:
                final_event_map['org2'].append(org_data['org2'])
        if 'actor1' in event:
            final_event_map['actor1'].append(event['actor1'])
        if 'actor2' in event:
            final_event_map['actor2'].append(event['actor2'])
        if 'date' in event:
            final_event_map['date'].append(get_event_date(event['date'], published_date_str))
        if 'location' in event:
            location_data = get_location_data(event['location'])
            #do not process if country is not set, this will happen for events outside India, Thailand and Indonesia
            if('country' not in location_data):
                print("here")
                return final_event_map
            else:
                final_event_map['country'].append(location_data['country'])
            if('administrative_area_level_1' in location_data):
                final_event_map['admin1'].append(location_data['administrative_area_level_1'])
            if('administrative_area_level_2' in location_data):
                final_event_map['admin2'].append(location_data['administrative_area_level_2'])
            if('administrative_area_level_3' in location_data):
                final_event_map['admin3'].append(location_data['administrative_area_level_3'])
            if('administrative_area_level_4' in location_data):
                final_event_map['admin4'].append(location_data['administrative_area_level_4'])
    return final_event_map

if __name__ == '__main__':
    app.run(host='0.0.0.0')
