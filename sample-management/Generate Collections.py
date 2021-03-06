
# coding: utf-8

# In[ ]:


get_ipython().system('pip install faker')
get_ipython().system('pip install names')
get_ipython().system('pip install uuid')
get_ipython().system('pip install python-dateutil')
get_ipython().system('pip install qrcode[pil]')


# In[7]:


import pickle
import json
import requests
import uuid
from faker import Factory
import names
import random
import time
import datetime
import qrcode

from datetime import date 
from datetime import datetime 
from dateutil.relativedelta import relativedelta


auth = ('api', 'Graz2018')
baseUrl='http://sample-managment.silicolab.bibbox/rest/ng'

DEFAULT_SIDE      = "LKHSW"
CP_ID             = 1
CP_TITLE          = "Blocks and Slides"
EVENT_ID          = 1

TISSUE_BLOCK_FORM = 86
TISSUE_BLOCK_CTX  = 31
PARTICIPANT_FORM  = 101
PARTICIPANT_CTX   = 37


def strTimeProp(start, end, format, prop):
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(format, time.localtime(ptime))

def randomDate(start, end, prop):
    return strTimeProp(start, end, '%Y-%m-%d', prop)


headers = {'content-type': "application/json", 'cache-control': "no-cache"}

print ("COLLECTIONS AVAILABLE")
r = requests.get(baseUrl+'/collection-protocols', auth=auth)
collections = json.loads (r.text)

print (json.dumps(collections, indent=4, sort_keys=True))

print ( date.today())

fake = Factory.create('de_AT')

for patientindex in range(0, 100):
    
    p = fake.profile()
    print (p['sex'])
    if p['sex'] == 'F': 
        fn = fake.first_name_female()
        pr = fake.prefix_female()
        gender = "Female"
    else:
        fn = fake.first_name_male()
        pr = fake.prefix_male()
        gender = "Male"
    
    ln =  fake.last_name()
    
    email = fn + "." + ln + "@" + fake.free_email_domain()    
    visitDate = randomDate ("1984-1-1", "2009-12-31", random.random()) 
    vdt = datetime.strptime(visitDate, "%Y-%m-%d")
    earliestBirthDate = vdt - relativedelta(years=99)
    latesttBirthDate  = vdt - relativedelta(years=30)
    birthdate = randomDate (earliestBirthDate.strftime("%Y-%m-%d"), latesttBirthDate.strftime("%Y-%m-%d"), random.random())
    
    p['birthdate'] = birthdate
    
    bdt = datetime.strptime(p['birthdate'], "%Y-%m-%d")  
   
    age = relativedelta(date.today(), bdt.date()).years
    ageAtVisit = relativedelta(datetime.strptime(visitDate, "%Y-%m-%d").date(), bdt.date()).years
    # only patients above 25year get a title (name prefix)
    if (age < 25) or (random.random() < 0.75):   pr= ""
    print (pr, fn, ln, email)    
    print ("    birthdate =", p['birthdate'], "age=", age)
    print ("    visitdate =", visitDate, "age at visit =", ageAtVisit)

    vitalStatus = "Alive"
    
    if (random.random() < 0.20):
        vitalStatus = "Dead"
    if (age > 100):
        vitalStatus = "Dead"
    
    participant_protocol_identifer = str(uuid.uuid4())
    
    participantRegistration = {
        "participant": {
        "firstName": fn,
        "lastName": ln,
        "middleName": "",
        "birthDate": birthdate,
        "deathDate": None,
        "gender": gender,       
        "races": [],
        "vitalStatus": "Unknown",
        "pmis": [],
        "ethnicities": [],
        "activityStatus": "Active",
        "phiAccess": True,
        "registeredCps": [],
        "cpId": -1,
        "reqRegInfo": False,
        "forceDelete": False
        },
        "cpId": CP_ID ,
        "registrationDate": visitDate,
        "ppid":  participant_protocol_identifer 
    }
    
   
    
    visit_identifer = str(uuid.uuid4())
    visit_uuid = uuid.uuid4()

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=2,
    )
    qr.add_data(str(participant_protocol_identifer))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save ("visitcode.png", "PNG")

    #http://sample-managment.silicolab.bibbox/rest/ng/visits/105
    
   
    dummyVisit = {
            "name" :  str(visit_uuid),
            "ppid":  participant_protocol_identifer, 
            "cpTitle": CP_TITLE,
            "eventId": EVENT_ID,
            "eventLabel": "Initial Visit",
            "eventPoint": 0,
            "clinicalDiagnoses": [
                                 ],
            "site": DEFAULT_SIDE,
            "visitDate": visitDate,
            "status": "Complete",
            "surgicalPathologyNumber": ""
        }
 
    # Zewail Kurt
    dummyUser = {
      "id":6,
    }
    
  
    specimenBlock =  {
      "lineage":"New",
      "visitId":1,
      "status":"Collected",
      "availableQty":"10",
      "storageLocation":{},
      "collectionEvent":{
        "user":dummyUser,
        "time":visitDate,
        "container":"Not Specified",
        "procedure":"Not Specified"
      },
      "receivedEvent":{
        "user": dummyUser,
        "time": visitDate,
        "receivedQuality":"Acceptable"
      },
      "initialQty":"10",
      "concentration":"",
      "label": "",
      "specimenClass":"Tissue",
      "type":"Fixed Tissue Block",
      "pathology":"Not Specified",
      "anatomicSite":"Colon, NOS",
      "laterality":"Not Specified"
    }
    specimenSlide =  {
      "lineage":"Derived",
      "visitId":1,
      "parentId" : -1,  
      "status":"Collected",
      "availableQty":"10",
      "storageLocation":{},
      "collectionEvent":{
        "user":dummyUser,
        "time":visitDate,
        "container":"Not Specified",
        "procedure":"Not Specified"
      },
      "receivedEvent":{
        "user": dummyUser,
        "time": visitDate,
        "receivedQuality":"Acceptable"
      },
      "initialQty":"10",
      "concentration":"",
      "label": "",
      "specimenClass":"Tissue",
      "type":"Fixed Tissue Slide",
      "pathology":"Not Specified",
      "anatomicSite":"Colon, NOS",
      "laterality":"Not Specified"
    }

    generatePatient = False
    if (ageAtVisit > 40 ):
        generatePatient = True
 
    generatePatient = True
 
    
    if generatePatient:
    
        r = requests.request("POST", baseUrl+'/collection-protocol-registrations/', data = json.dumps(participantRegistration), auth=auth, headers = headers )
        participant = json.loads (r.text)
        print ("====  PARTICIPANT GENERATED ==========")
        print (json.dumps(participant, indent=4, sort_keys=True))

        #form 94 is hard coded here, thats the Particpatant Extension        
        participantID = participant["id"]     
        filename = str(participant_protocol_identifer) + ".png"
        
        multiple_files = [('file', (filename, open('visitcode.png', 'rb'), 'image/png'))]
        r = requests.post(baseUrl+'/form-files', files=multiple_files, auth=auth)
        files = json.loads (r.text)
        print ("====  FILES UPLOADED  ==========")
        print (json.dumps(files, indent=4, sort_keys=True))
        
        participantExtensions = {
            "FU2": {
                "filename": filename,
                "contentType": "image/jpeg",
                "fileId": files['fileId']
                  },
            "ST3" :  str(ageAtVisit),
            "appData": {
                "formCtxtId": PARTICIPANT_CTX,
                "objectId": participantID
            }
        }
        
        url = baseUrl+'/forms/' + str(PARTICIPANT_FORM ) + '/data'
      
        
        r = requests.request("POST", url, data = json.dumps(participantExtensions), auth=auth, headers = headers )
        extensions = json.loads (r.text)
        print ("====  PARTICIPANT EXTENSIONS GENERATED ==========")
        print (json.dumps(extensions, indent=4, sort_keys=True))
        
        r = requests.request("POST", baseUrl+'/visits/', data = json.dumps(dummyVisit), auth=auth, headers = headers )
        visit = json.loads (r.text)
        print ("====  VISIT GENERATED ==========")
        print (json.dumps(visit, indent=4, sort_keys=True))
        
        numberOfBlocks = int (5 + 10.0*random.random())
        specimenBlock['visitId'] = visit ['id']
        specimenSlide['visitId'] = visit ['id']
        for blockindex in range(0, numberOfBlocks):
          
          specimenBlock['label']  = str(uuid.uuid4())
          r = requests.request("POST", baseUrl+'/specimens', data = json.dumps(specimenBlock), auth=auth, headers = headers )
          specimen = json.loads (r.text)
          print ("====  SPECIMEN GENERATED ==========")
          print (json.dumps(specimen, indent=4, sort_keys=True))
    
    
          TissueLabel = "non specified" 
          rl = 5.0 * random.random()
          if (rl>1.0):  TissueLabel = "TU" 
          if (rl>2.0):  TissueLabel = "POLY" 
          if (rl>3.0):  TissueLabel = "LY" 
    
          url = baseUrl+'/forms/' + str(TISSUE_BLOCK_FORM ) + '/data'
          specimenExtension ={
            "MLB5": [ TissueLabel],
            "TA6": "FFPE",
             "appData": {
                "formCtxtId": TISSUE_BLOCK_CTX,
                "objectId": specimen ['id']
              }
          }
          r = requests.request("POST", url, data = json.dumps(specimenExtension), auth=auth, headers = headers )
          extensions = json.loads (r.text)
          print ("====  PARTICIPANT EXTENSIONS GENERATED ==========")
          print (json.dumps(extensions, indent=4, sort_keys=True))
    
          specimenSlide['label']  = str(uuid.uuid4())
          specimenSlide['parentId'] = specimen ['id']
           
          r = requests.request("POST", baseUrl+'/specimens', data = json.dumps(specimenSlide), auth=auth, headers = headers )
          slides = json.loads (r.text)
          print ("====  SPECIMEN GENERATED ==========")
          print (json.dumps(slides, indent=4, sort_keys=True))
        
        
        

