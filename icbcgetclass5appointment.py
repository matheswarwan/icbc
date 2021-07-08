import requests, json, time, datetime, os
from time import sleep
from datetime import datetime, timedelta

# Execution time config
totalRunTime = 60 #mins
gapBetweenRuns = 5*60 #seconds
alertMonth = 9 # alert for slots available before 'September'
alertYear = 2021

# Login details 
driverLastName = ""
licenceNumber = ""
keyword = ""
examType = "5-R-1" #Class 5 Road Test 1st Attempt 
examDate = (datetime.now() + timedelta(days=1) ).strftime('%Y-%m-%d') # Tomorrow
# datetime.today().strftime('%Y-%m-%d') #Today

# Alert tone details 
alertMP3Location="/System/Library/Sounds/Funk.aiff"

#Global variable
class AccessToken:
    accessToken = ''

# position Ids are for Surrey & surrounding areas
# Get more Ids by calling https://onlinebusiness.icbc.com/deas-api/v1/web/getNearestPos (put)
# {
# 	"lng": -122.3291667,
# 	"lat": 49.0522222,
# 	"examType": "5-R-1",
# 	"startDate": "2021-07-01"
# }

posIds = [1,2,3,6,8,9,11,73,93,153,269,270,271,272,274,275,276,277]
posLocs = {
            1 : "31935 S Fraser Way #150, Abbotsford, BC V2T 5N7",
            2 : "3880 Lougheed Hwy, Burnaby, BC V5C 6N4",
            3 : "46052 Chilliwack Central Rd, Chilliwack, BC V2P 1J6",
            6 : "22470 Dewdney Trunk Rd #175, Maple Ridge, BC V2X 5Z6",
            8 : "1331 Marine Dr, North Vancouver, BC V7P 3E5",
            9 : "4126 Macdonald St, Vancouver, BC V6L 2P2",
            11 : "13426 78 Ave, Surrey, BC V3W 8J6",
            73 : "1930 Oxford Connector, Port Coquitlam, BC V3C 0A4",
            93 : "5300 No 3 Rd #402, Richmond, BC V6X 2X9",
            153 : "19950 Willowbrook Dr j7, Langley, BC V2Y 1K9",
            226 : "226 - unknown location",
            269 : "10262 152A Street, Surrey, BC V3R 6T8",
            270 : "6000 Production Way, Langley City, BC V3A 6L5",
            271 : "13665 68 Avenue, Surrey, BC V3W 0Y6", 
            272 : "100 Blue Mountain Street, Coquitlam, BC V3K 1A2",
            274 : "4399 Wayburne Drive, Burnaby, BC V5G 3X7",
            275 : "999 Kingsway, Vancouver, BC V5V 4Z7",
            276 : "1320 3rd Avenue, New Westminster, BC V3M 5T4",
            277 : "2885 Trethewey Street, Abbotsford, BC V2T 3R2"
        }

# Functions
def getAccessToken():
    sleep(3) # if token is generated often, service returns error
    loginURL = 'https://onlinebusiness.icbc.com/deas-api/v1/webLogin/webLogin'
    loginbody = {"drvrLastName":driverLastName,"licenceNumber":licenceNumber,"keyword":keyword}
    loginheaders = { 'content-type': 'application/json' }
    resLogin = requests.put(loginURL, data = json.dumps(loginbody), headers= loginheaders )
    print('Login successful and received below auth token..')
    print(resLogin.headers['Authorization'])
    return resLogin.headers['Authorization'] 
    
if driverLastName != "" and licenceNumber != "" and keyword != "":
    AccessToken.accessToken = getAccessToken()
else:
    raise ValueError('***Please enter Driver last name, license number and keyword in line# 12 - 14***')

def getAvailableAppointments(accessToken):
    url = 'https://onlinebusiness.icbc.com/deas-api/v1/web/getAvailableAppointments'
    method = 'post'
    headers =   {
                'content-type': 'application/json',
                'Authorization' : accessToken
                }   
    reqJson = {
                "aPosID": posId,
                "examType": examType,
                "examDate": examDate,
                "ignoreReserveTime": False,
                "prfDaysOfWeek": "[0,1,2,3,4,5,6]",
                "prfPartsOfDay": "[0,1]",
                "lastName": driverLastName,
                "licenseNumber": licenceNumber
            }
    x = requests.post(url, data=json.dumps(reqJson), headers=headers)
    # print(x.status_code)
    # Regenerate access token 
    if x.status_code < 200 or x.status_code > 299:
        AccessToken.accessToken = getAccessToken()
        return None
    return x.json()

#Loop through all posIDs for 2 mintues with 10 seconds gap between each request
timeout = time.time() + totalRunTime * 60   # Run for these many seconds
while True:
    if time.time() < timeout:
        print('------------START : Checking for appointment at ' + time.ctime() + '---------')
        for posId in posIds:
            print("[Checking]: Location - " + posLocs[posId] + ".")
            resp = getAvailableAppointments(AccessToken.accessToken)
            if resp:
                print("Appointment FOUND ") 
                for r in resp:    
                    print("x-x-x-x-x-x-x-x")
                    print("Location: " + posLocs[r['posId']])
                    print("Day: " + r['appointmentDt']['dayOfWeek'])
                    print("Date: " + r['appointmentDt']['date'])
                    print("StartTime: " + r['startTm'])
                    print("EndTime: " + r['endTm'])
                    print("x-x-x-x-x-x-x-x")
                    # Alert sound
                    if datetime.strptime(r['appointmentDt']['date'], '%Y-%m-%d').month <= alertMonth and datetime.strptime(r['appointmentDt']['date'], '%Y-%m-%d').year <= alertYear :
                        os.system('afplay '+alertMP3Location)
                # sendEmail(posLocs[posId], json.dumps(resp))
        print('------------END : Checking for appointment at ' + time.ctime() + '---------')                
        sleep(gapBetweenRuns) # Wait for these many seconds before checking again
    else:
        break #Exit once the timeout completes
