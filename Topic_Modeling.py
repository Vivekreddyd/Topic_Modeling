from bs4 import BeautifulSoup
import gensim
import pprint
from googleapiclient.discovery import build
import json as m_json
import spacy
import requests
import operator
from sklearn.feature_extraction.text import TfidfVectorizer
# from operator import itemgetter, attrgetter, methodcaller
# data=open('/media/vivek/Personal/Vivek/Interview Prep/Crawl_Bot/patent.html','r').read()
# soup=BeautifulSoup(data)
# foi=soup.find('h-0001')
soup = BeautifulSoup(open("./patent.html",encoding = "ISO-8859-1"),"lxml")
nlp=spacy.load('en_core_web_sm')
# for city in soup.find_all('span', {'class' : 'city-sh'}):
#     print(city)
# plot=[]
documents=[]
documents_list=["Master"]

dict_pat_details={}
dict_pat_details["Master"]="Original Document: No Assignee"
mark = soup.find(id="h-0001")
master_foi,master_dd,master_sod,query='','','',''
# query_start,query_end=0,0
search_results=10
# walk through the siblings of the parent (H2) node
# until we reach the next H2 node
for elt in mark.parent.nextSiblingGenerator():
    if elt.name == "heading":
        # break
        mark=elt
    if hasattr(elt, "text"):
        if(mark.contents[0]=='FIELD OF THE INVENTION'):
            master_foi += elt.text
        elif (mark.contents[0] == 'SUMMARY OF DISCLOSURE'):
            master_sod += elt.text
        elif (mark.contents[0] == 'DETAILED DESCRIPTION'):
            master_dd += elt.text
documents.append(master_foi+' '+master_sod+' '+master_dd)
# enjoy
# print("".join(plot))
# model = gensim.models.Word2Vec.load('/local/vivek/keras/keras/datasets/cnn-text-classification-tf-master/data/rt-polaritydata/Word2Vec_GoogleNews-vectors-negative300.txt')
model = gensim.models.KeyedVectors.load_word2vec_format('/local/vivek/Word2vec/GoogleNews-vectors-negative300.bin.gz', binary=True)#, unicode_errors='ignore')
dict_sub_topic={}
# Topic Modeling
foi_arr=master_foi.split('.')
doc=nlp(foi_arr[0])
# topic=(word.text for word in doc if(word.tag_=='NNS'))
# indx=0
for word in doc:
    if(word.tag_=='NNS'):
        topic=word.text
doc1=nlp(foi_arr[1])
sub_topics=[]
for indx,word1 in enumerate(doc1):
    # indx+=1
    sub_topics.append(word1.text)
    if (word1.tag_ == 'NN'):
        # topic = word.text
        # dict_sub_topic[word1.text]=[(model.wv.similarity(topic,word1.text),indx)]
        # print((model.wv.similarity(topic,word1.text)))
        li = model.wv.similarity(topic,word1.text).item()
        # print(li)
        dict_sub_topic[word1.text]=[li]
        dict_sub_topic[word1.text].append(indx)
query_range=list(sorted(dict_sub_topic.values(), key=operator.itemgetter(0), reverse=True)[:2])

# test=operator.itemgetter
if(query_range[0][1]>query_range[1][1]):
    query=' '.join(sub_topics[query_range[1][1]:query_range[0][1]])
else:
    query=' '.join(sub_topics[query_range[0][1]:query_range[1][1]])

# for i in foi_arr[1]:
#         sim_score=
# topic="orthopedics"
# sentences=[['The','present']]
# model=gensim.models.Word2Vec(sentences,min_count=1)
# model = gensim.models.KeyedVectors.load_word2vec_format('/media/vivek/Personal/Vivek/Interview Prep/Crawl Bot/GoogleNews-vectors-negative300.bin.gz', binary=True)
# print(model.wv.similarity('woman', 'man'))


# def main():
# Build a service object for interacting with the API. Visit
# the Google APIs Console <http://code.google.com/apis/console>
# to get an API key for your own application.
api_key = "AIzaSyAD0UzPyyBnhcIPOyuhPiJ_7jQCldtj9FY "

service = build("customsearch", "v1",
        developerKey=api_key)
res = service.cse().list(
  q=query,
  cx='010311747624857012761:ljplje0wi9m',
    num=search_results
).execute()
# data=m_json.loads(res)
# print(res['items'][1]['link'])
for result in range(search_results):
    foi, dd, sod = '', '', ''
    try:
        r = requests.get(res['items'][result]['link'])
        data = r.text
        assignee_array = []
        soup = BeautifulSoup(data,'lxml')
        # text = soup.find('p').getText()
        # text=[x.contents[0] for x in soup.findAllNext("p")]
        # print (''.join(text.strip() for text in soup.p.find_all(text=True, recursive=False)))
        # text = ["".join(x.findAll(text=True)) for x in soup.findAllNext("p")]
        # print(text)
        for link in soup.find_all('meta'):
            if(link.get('scheme')=="assignee"):
                assignee_array.append(link.get('content'))
            if(link.get("name")=="citation_patent_number"):
                pat_id=link.get('content')
        # print(assignee_array[-1])
        # print(pat_id)

        # pprint.pprint(res)
        divs=soup.find_all("div",attrs={"class":"description"})
        # print(divs)
        text_temp=[]
        foi,summ,desc='','',''
        mark = soup.find("heading")
        for elt in mark.parent.contents:
            if elt.name == "heading":
                # break
                mark = elt
            if hasattr(elt, "text"):
                if ("field of the invention" in mark.contents[0].lower()):
                    foi += elt.text
                elif ("summary" in mark.contents[0].lower()):
                    sod += elt.text
                elif ("description" in mark.contents[0].lower()):
                    dd += elt.text

        documents.append(foi + ' ' + sod + ' ' + dd)
        documents_list.append(pat_id)
        dict_pat_details[pat_id] = assignee_array[-1]
        # divs=soup.find("div",{"class":"description"}).findAll('p')
        # for div in divs:
        #     text_temp.append(' '.join(div.findAll(text=True)))
        # for indx,text in enumerate(text_temp):
        #     if("field of the invention" in text.lower() and len(text.split())<=6):
        #         foi=text_temp[indx+1]
        #     elif("summary" in text.lower().split()[0:5] and len(text.split())<=6):
        #         summ=text_temp[indx+1]
        #     elif ("description" in text.lower().split()[0:5] and len(text.split())<=6):
        #         desc = text_temp[indx + 1]
    except:
        print()
vect = TfidfVectorizer(min_df=1)
# tfidf = vect.fit_transform(["I'd like an apple","An apple a day keeps the doctor away","Never compare an apple to an orange","I prefer scikit-learn to Orange"])
# tfidf=vect.fit_transform()
tfidf = vect.fit_transform(documents)
final_arr=(tfidf * tfidf.T).A[0]
final_arr=final_arr.tolist()
for doc in sorted(final_arr,reverse=True):
    print("Patent ID: "+documents_list[final_arr.index(doc)].zfill(20)+"\t"+"Document Relevance: "+ str(doc).zfill(12)+'\t'+"Assignee: "+ dict_pat_details[documents_list[final_arr.index(doc)]].zfill(12))
        # print(text)
    # print(foi)
    # print(summ)
    # print(desc)
        # if()
    # for div in divs:
        # print(div.findAllNext('p').text)
        # text_list = [text for text in div.stripped_strings]
        # print(div.find('p').text)
    # print(text_list)
    # print (''.join(text.strip() for text in soup.p.find_all(text=True, recursive=False)))

    # for row in soup.find_all("div", attrs={"class":"description"}):
    #     print (row.find('p').text)

# if __name__ == '__main__':
#     main()
# from urllib.request import urlopen
# # import urllib2
# import urllib
# import json
# # from simplejson import loads
#
# url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&"
#
# query = input("What do you want to search for ? >> ")
#
# query = urllib.parse.urlencode( {'q' : query } )
#
# response = urlopen (url + query ).read()
#
# data = json.loads ( response )
#
# results = data [ 'responseData' ] [ 'results' ]
#
# for result in results:
#     title = result['title']
#     url = result['url']
#     print ( title + '; ' + url )

# import urllib
# import json as m_json
# query = raw_input ( 'Query: ' )
# query = urllib.urlencode ( { 'q' : query } )
# response = urllib.urlopen ( 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&' + query ).read()
# json = m_json.loads ( response )
# results = json [ 'responseData' ] [ 'results' ]
# for result in results:
#     title = result['title']
#     url = result['url']   # was URL in the original and that threw a name error exception
#     print ( title + '; ' + url )