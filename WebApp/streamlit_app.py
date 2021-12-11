import streamlit as st
import pickle
import time
import os
import requests
import pandas as pd
from urllib.parse import urlparse, urlencode
import ipaddress
import re
from bs4 import BeautifulSoup
import urllib
import urllib.request
import plotly.express as px
from datetime import datetime
import pickle

# Functions to determine the features of the URL

def checkIP(url):
    try:
        ipaddress.ip_address(url)
        return 1
    except:
        return 0

def checkAtSymbol(url):
    if ("@" in url):
        return 1
    else:
        return 0

def lengthUrl(url):
    if(len(url) >= 54):
        return 1
    else:
        return 0

def depthUrl(url):
    depth = 0
    urlSplit = urlparse(url).path.split('/')
    for i in range(len(urlSplit)):
        if(len(urlSplit[i]) != 0):
            depth += 1
    return depth

def checkRedirUrl(url):
    pos = url.rfind("//")
    if(pos > 6):
        return 1
    else:
        return 0

def checkHttpDomain(url):
    domain = urlparse(url).netloc
    if("http" in domain or "https" in domain):
        return 1
    else: 
        return 0

all_shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|" \
                      r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|" \
                      r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|" \
                      r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|" \
                      r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|" \
                      r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|" \
                      r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|" \
                      r"tr\.im|link\.zip\.net"
                      
def checkShortUrl(url):
    if re.search(all_shortening_services, url):
        return 1
    else:
        return 0

def checkPrefSuff(url):
    if "-" in urlparse(url).netloc:
        return 1
    else:
        return 0

def checkWebTraffic(url):
  try:
    url = urllib.parse.quote(url)
    rank = BeautifulSoup(urllib.request.urlopen("http://data.alexa.com/data?cli=10&dat=s&url=" + url).read(), "xml").find(
        "REACH")['RANK']
    rank = int(rank)
  except TypeError:
        return 1
  if rank < 100000:
    return 1
  else:
    return 0

def checkDomainAge(domain_name):
  if(type(domain_name) == str):
      return 1
  creation_date = domain_name.creation_date
  expiration_date = domain_name.expiration_date
  if (isinstance(creation_date,str) or isinstance(expiration_date,str)):
    try:
      creation_date = datetime.strptime(creation_date,'%Y-%m-%d')
      expiration_date = datetime.strptime(expiration_date,"%Y-%m-%d")
    except:
      return 1
  if ((expiration_date is None) or (creation_date is None)):
      return 1
  elif ((type(expiration_date) is list) or (type(creation_date) is list)):
      return 1
  else:
    ageofdomain = abs((expiration_date - creation_date).days)
    if ((ageofdomain/30) < 6):
      return 1
    else:
      return 0
  
def checkDomainEnd(domain_name):
  if(type(domain_name) == str):
      return 1
  expiration_date = domain_name.expiration_date
  if isinstance(expiration_date,str):
    try:
      expiration_date = datetime.strptime(expiration_date,"%Y-%m-%d")
    except:
      return 1
  if (expiration_date is None):
      return 1
  elif (type(expiration_date) is list):
      return 1
  else:
    today = datetime.now()
    end = abs((expiration_date - today).days)
    if ((end/30) < 6):
      return 0
    else:
      return 1

def checkIframe(response):
  if response == "":
      return 1
  else:
      if re.findall(r"[<iframe>|<frameBorder>]", response.text):
          return 0
      else:
          return 1

def checkMouseOver(response): 
  if response == "" :
    return 1
  else:
    if re.findall("<script>.+onmouseover.+</script>", response.text):
      return 1
    else:
      return 0
  
def checkRightClick(response):
  if response == "":
    return 1
  else:
    if re.findall(r"event.button ?== ?2", response.text):
      return 0
    else:
      return 1

def checkForwarding(response):
  if response == "":
    return 1
  else:
    if len(response.history) <= 2:
      return 0
    else:
      return 1
  
def featureExtraction(url):
#     print(url)

    dns = 0
    domainName = ""
    try:
        domainName = whois.whois(urlparse(url).netloc)
 #         print(domainName)
    except:
        dns = 1
    
    try:
        response = requests.get(url, timeout=5)
    except:
        response = ""
        
    featuresDict = {
    
    #  Address Bar based Features
    "Have_IP" :  checkIP(url),
    "Have_At" : checkAtSymbol(url),
    "URL_Length" : lengthUrl(url),  
    "URL_Depth" : depthUrl(url),
    "Redirection" : checkRedirUrl(url),
    "https_Domain" : checkHttpDomain(url),
    "TinyURL" : checkShortUrl(url),
    "Prefix/Suffix" : checkPrefSuff(url),
    
    #  Domain based Features
    "DNS_Record" : dns,
    "Web_Traffic" : checkWebTraffic(url),
    "Domain_Age": checkDomainAge(domainName),
    "Domain_End": checkDomainEnd(domainName),
    
    #   HTML and JavaScript based Features
    "iFrame" : checkIframe(response),
    "Mouse_Over" : checkMouseOver(response),
    "Right_Click" : checkRightClick(response),
    "Web_Forwards" : checkForwarding(response),
}
           
    return featuresDict

# load model from file
loaded_model = pickle.load(open("../XGBoostClassifier.pickle.dat", "rb"))

# Frontend

# Title
st.markdown("<h1 style = 'color:Gold; Text-align: Center; font-size: 40px;'>Phishing Website Detection by Machine Learning</h1>", unsafe_allow_html=True)

# progress = 0

with st.form(key='my_form'):
    url = st.text_input(label='Enter URL')
    col1, col2, col3 , col4, col5 = st.beta_columns(5)

    with col1:
        pass
    with col2:
        pass
    with col4:
        pass
    with col5:
        pass
    with col3 :
        submit_button = st.form_submit_button(label='Submit')
    

if submit_button:
    # while progress != 100:
    #     progress += 10
    df = pd.DataFrame(featureExtraction(url), index=[0])
    prediction = loaded_model.predict_proba(df)
    prediction_label = loaded_model.predict(df)
    # print(prediction)
    # print(prediction_label)
    st.text("")
    st.text("")
    st.dataframe(df)
    st.text("")
    if(prediction_label[0] == 0):
        st.success("This is legitimate URL, you are safe to proceed")
    else:
        st.warning("This is phishing URL, you are NOT safe to proceed")
        
    fig = px.pie(prediction, values=prediction[0][:], names=[
                 "Legitimate URL", "Phishing URL"])
    # , title='Phishing Website Detection percentage for both the Teams'
    st.plotly_chart(fig)
    
    
        
# st.progress(progress)
    # col1, col2, col3 , col4, col5 = st.beta_columns(5)
    # with col1:
    #     pass
    # with col2:
    #     pass
    # with col4:
    #     pass
    # with col5:
    #     pass
    # with col3 :
    # #    st.dataframe(my_dataframe)
       
       
       
