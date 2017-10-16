from bs4 import BeautifulSoup
import gensim
import pprint
from googleapiclient.discovery import build
import json as m_json
import spacy
import requests
# data=open('/media/vivek/Personal/Vivek/Interview Prep/Crawl_Bot/patent.html','r').read()
# soup=BeautifulSoup(data)
# foi=soup.find('h-0001')
soup = BeautifulSoup(open("/media/vivek/Personal/Vivek/Interview_Prep/Crawl_Bot/patent.html",encoding = "ISO-8859-1"),"lxml")
nlp=spacy.load('en')
# for city in soup.find_all('span', {'class' : 'city-sh'}):
#     print(city)
# plot=[]
mark = soup.find(id="h-0001")
master_foi,master_dd,master_sod='','',''
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
# enjoy
# print("".join(plot))
model = gensim.models.KeyedVectors.load_word2vec_format('/media/vivek/Personal/Vivek/Interview_Prep/Crawl Bot/GoogleNews-vectors-negative300.bin.gz', binary=True)
dic_sub_topic={}
# Topic Modeling
foi_arr=master_foi.split('.')
doc=nlp(foi_arr[0])
for word in doc:
    if(word.tag_=='NNS'):
        topic=word.text
doc1=nlp(foi_arr[1])
sub_topics=[]
for word1 in doc1:
    if (word1.tag_ == 'NNS'):
        # topic = word.text
        dic_sub_topic[word1.text]=sub_topics.append(word1.text)
# for i in foi_arr[1]:
        model.wv.similarity(topic,word1.text)
# topic="orthopedics"
# sentences=[['The','present']]
# model=gensim.models.Word2Vec(sentences,min_count=1)
# model = gensim.models.KeyedVectors.load_word2vec_format('/media/vivek/Personal/Vivek/Interview Prep/Crawl Bot/GoogleNews-vectors-negative300.bin.gz', binary=True)
# print(model.wv.similarity('woman', 'man'))


def main():
    # Build a service object for interacting with the API. Visit
    # the Google APIs Console <http://code.google.com/apis/console>
    # to get an API key for your own application.
    api_key = "AIzaSyAD0UzPyyBnhcIPOyuhPiJ_7jQCldtj9FY "

    service = build("customsearch", "v1",
            developerKey=api_key)
    res = service.cse().list(
      q='interventional technique and an implant for altering biomechanics of the spine',
      cx='010311747624857012761:ljplje0wi9m',
    ).execute()
    # data=m_json.loads(res)
    # print(res['items'][1]['link'])
    r = requests.get(res['items'][2]['link'])
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
    print(assignee_array[-1])
    print(pat_id)
    # pprint.pprint(res)
    divs=soup.find_all("div",attrs={"class":"description"})
    # print(divs)
    text_temp=[]
    foi,summ,desc='','',''
    divs=soup.find("div",{"class":"description"}).findAll('p')
    for div in divs:
        text_temp.append(' '.join(div.findAll(text=True)))
    for indx,text in enumerate(text_temp):
        if("field of the invention" in text.lower()):
            foi=text_temp[indx+1]
        elif("summary" in text.lower().split()[0:5]):
            summ=text_temp[indx+1]
        elif ("description" in text.lower().split()[0:5]):
            desc = text_temp[indx + 1]
        print(text)
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

if __name__ == '__main__':
    main()
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