from bs4 import BeautifulSoup
import gensim
import pprint
from googleapiclient.discovery import build
import json as m_json
import spacy
import requests
import operator
from sklearn.feature_extraction.text import TfidfVectorizer

# load the challenge page (converted to HTML for convienience)
soup = BeautifulSoup(open("./patent.html",encoding = "ISO-8859-1"),"lxml")

#### Initializations
nlp=spacy.load('en_core_web_sm') # Spacy tool for Language processing
documents=[]
documents_list=["Master"]
dict_pat_details={}
dict_pat_details["Master"]="Original Document: No Assignee"

master_foi,master_dd,master_sod,query='','','',''
search_results=10
#### Initializations


### Using BeautifulSoup extrating context from the Source Document
mark = soup.find(id="h-0001")
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
### Using BeautifulSoup extrating context from the Source Document


###Loading Google word2Vec documents
model = gensim.models.KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300.bin.gz', binary=True)#, unicode_errors='ignore')
###Loading Google word2Vec documents


# Topic Modeling, Extracting Topic from the source document and also building query using google word embeddings
dict_sub_topic={}
foi_arr=master_foi.split('.')
doc=nlp(foi_arr[0])
for word in doc:
    if(word.tag_=='NNS'):
        topic=word.text
doc1=nlp(foi_arr[1])
sub_topics=[]
for indx,word1 in enumerate(doc1):
    sub_topics.append(word1.text)
    if (word1.tag_ == 'NN'):
        li = model.wv.similarity(topic,word1.text).item()
        dict_sub_topic[word1.text]=[li]
        dict_sub_topic[word1.text].append(indx)
query_range=list(sorted(dict_sub_topic.values(), key=operator.itemgetter(0), reverse=True)[:2])
if(query_range[0][1]>query_range[1][1]):
    query=' '.join(sub_topics[query_range[1][1]:query_range[0][1]])
else:
    query=' '.join(sub_topics[query_range[0][1]:query_range[1][1]])
# Topic Modeling, Extracting Topic from the source document and also building query using google word embeddings


### Using Google custom API, query wwww and get top 10 results and scrap using beautifulsoup
api_key = "AIzaSyAD0UzPyyBnhcIPOyuhPiJ_7jQCldtj9FY "
service = build("customsearch", "v1",
        developerKey=api_key)
res = service.cse().list(
  q=query,
  cx='010311747624857012761:ljplje0wi9m',
    num=search_results
).execute()
for result in range(search_results):
    foi, dd, sod = '', '', ''
    try:
        r = requests.get(res['items'][result]['link'])
        data = r.text
        assignee_array = []
        soup = BeautifulSoup(data,'lxml')
        for link in soup.find_all('meta'):
            if(link.get('scheme')=="assignee"):
                assignee_array.append(link.get('content'))
            if(link.get("name")=="citation_patent_number"):
                pat_id=link.get('content')
        divs=soup.find_all("div",attrs={"class":"description"})
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
    except:
        pass
### Using Google custom API, query wwww and get top 10 results and scrap using beautifulsoup


###Using TFIDF get the relevance, sort and print the results
vect = TfidfVectorizer(min_df=1)
tfidf = vect.fit_transform(documents)
final_arr=(tfidf * tfidf.T).A[0]
final_arr=final_arr.tolist()
for doc in sorted(final_arr,reverse=True):
    if(not documents_list[final_arr.index(doc)]=='Master'):
        print("Patent ID: "+documents_list[final_arr.index(doc)].zfill(20)+"\t"+"Document Relevance: "+ str(doc).zfill(12)+'\t'+"Assignee: "+ dict_pat_details[documents_list[final_arr.index(doc)]].zfill(12))