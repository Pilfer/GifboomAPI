import os

#For HTTP shit
import requests
import json

#For some encryption stuff
import hashlib
import random
import string

class Gifboom:
    def __init__(self):
        print "GifBoom Instance Initialized"
        
        #Technical variables for this object
        self.id = None
        self.cookies = None
        self.proxies = None
    
        #Gifboom-specific variables for this object
        self.base = "http://api.gifboom.com/v1"
        self.useragent = "GifBoom (Android)";
        self.clientVersion = "2.4.3.3606";
        
        #Account-specific variables
        self._id = None
        self.authToken = ""
        self.deviceId = ""
        self.email = ""
        self.password = ""
        
        self.info = None

    #How fucking lazy am I? :[
    def setId(self,id):
        self._id = id

    #Generates a new DeviceID (I kinda hacked this together lol)
    def genDeviceId(self):
        x = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
        m = hashlib.md5()
        m.update(x)
        return str(m.hexdigest())[0:16]

    #Sets the deviceID for this object - only used to fool GifBoom for the sake of consistency
    def setDeviceId(self,deviceId):
        self.deviceId = deviceId
    
    #Sets the authorization_token - Only use this if we've logged in previously so we don't have to login for future requests
    def setAuthToken(self,token):
        self.authToken = token
    
    #Get the gender of the user - Note: Must be called AFTER self.login()
    def getGender(self):
        if self.info is None:
            return False
        else:
            if self.info['gender'] == 0:
                return "Male"
            else:
                return "Female"
    
    #Requests HTTP GET wrapper
    def get(self,url,headerz):
        if headerz == None:
            if self.proxies == None:
                r = requests.get(url)
            else:
                r = requests.get(url,proxies=self.proxies)
        else:
            if self.proxies == None:
                r = requests.get(url,headers = headerz)
            else:
                r = requests.get(url,headers=headerz,proxies=self.proxies)
            
        if r.status_code == requests.codes.ok:
            return r.text
        else:
            return False

    #Requests HTTP POST wrapper
    def post(self,url,headerz,postdata):
        if headerz == None:
            if self.proxies == None:
                if postdata == None:
                    r = requests.post(url)
                else:
                    r = requests.post(url,data=postdata)
            else:
                r = requests.post(url,data=postdata,proxies=self.proxies)
        else:
            if self.proxies == None:
                if postdata == None:
                    r = requests.post(url,headers=headerz)
                else:
                    r = requests.post(url,headers=headerz,data=postdata)
            else:
                if postdata == None:
                    r = requests.post(url,headers=headerz,proxies=self.proxies)
                else:
                    r = requests.post(url,headers=headerz,data=postdata,proxies=self.proxies)

        if r.status_code == requests.codes.ok:
            return r.text
        else:
            return False
    
    def sendMessage(self,to,body):
        payload = {
            "recipients": to,
            "body": body
        }
        headers = {
            "accept" : "application/json",
            "x-device-id" : self.deviceId,
            "x-client-version" : self.clientVersion,
            "accept-language" : "en",
            "x-user-authentication-token" : self.authToken,
            "user-agent" : self.useragent,
            "connection" : "Keep-Alive"
        }
        msg_response = self.post(self.base + "/messages",headers,payload)
        if msg_response != False:
            return True #json.loads(msg_response.decode('utf8'))
        else:
            return False
    
    #Function to login to Gifboom
    def login(self,email,password):
    
        payload = {
            "user[email]": email,
            "user[password]": password
        }
        
        headers = {
            "accept" : "application/json",
            "x-device-id" : self.deviceId,
            "x-client-version" : self.clientVersion,
            "accept-language" : "en",
            "user-agent" : self.useragent
        }
        
        login_response = self.post(self.base + "/login",headers,payload)
        if login_response != False:
            self.email = email
            self.password = password
            self.info = json.loads(login_response.decode('utf8'))
            if self.info['authentication_token']:
                self.authToken = self.info['authentication_token']
                return True
            else:
                return False
        else:
            return False

    #Create Account function.
    def createAccount(self,email,username,password):
        #Generate a new deviceId for this account
        did = self.genDeviceId()
        self.setDeviceId(did)
        
        payload = {
            "user[username]": username,
            "user[email]": email,
            "user[password]": password
        }
        headers = {
            "accept" : "application/json",
            "x-device-id" : self.deviceId,
            "x-client-version" : self.clientVersion,
            "accept-language" : "en",
            "user-agent" : self.useragent
        }
        register_response = self.post(self.base + "/users",headers,payload)
        if register_response != False:
            self.email = email
            self.password = password
            self.info = json.loads(register_response.decode('utf8'))
            if self.info['authentication_token']:
                self._id = self.info['_id']
                self.authToken = self.info['authentication_token']
                return True
            elif self.info['message']:
                print "Error message: " + self.info['message']
            else:
                print "ERROR1: " + str(register_response)
                return False
        else:
            return False
    
    #Get top 100 users on Gifboom
    def getTop(self):
        head = {
            "accept" : "application/json",
            "x-device-id" : self.deviceId,
            "x-client-version" : self.clientVersion,
            "accept-language" : "en",
            "user-agent" : self.useragent
        }
        r = self.get(self.base + "/users/top_users",head)
        if r != False:
            top_response = r.text
            return json.loads(top_response.decode('utf8'))
        else:
            return False
    
    #Get popular page
    def getPopular(self):
        #/feed/popular
        headers = {
            "accept" : "application/json",
            "x-device-id" : self.deviceId,
            "x-client-version" : self.clientVersion,
            "accept-language" : "en",
            "user-agent" : self.useragent,
            "connection" : "Keep-Alive"
        }
        popresp = self.get(self.base + "/feed/popular",headers)
        if popresp == False:
            return False
        else:
            resp = json.loads(popresp.encode('utf8'))
            return resp
    
    #Get a specific item (POST/GIF)
    def getItem(self,itemid):
        #/feed/popular
        headers = {
            "accept" : "application/json",
            "x-device-id" : self.deviceId,
            "x-client-version" : self.clientVersion,
            "accept-language" : "en",
            "user-agent" : self.useragent
        }
        
        popresp = self.get(self.base + "/items/" + itemid,headers)
        if popresp == False:
            return False
        else:
            resp = json.loads(popresp.encode('utf8'))
            return resp
    
    #Change profile picture (path relative to the location of script)
    def changeProfilePicture(self,photo):
        headers = {
            "accept" : "application/json",
            "accept-language" : "en",
            "connection" : "keep-alive",
            "x-user-authentication-token" : self.authToken,
            "x-client-version" : self.clientVersion,
            "x-device-id" : self.deviceId,
            "user-agent" : self.useragent
        }
        files = {
            'user[avatar]': (photo, open(photo, 'rb'))
        }
        if self.proxies == None:
            r = requests.put(self.base + "/users/" + self.info['_id'],headers=headers,files=files)
        else:
            r = requests.put(self.base + "/users/" + self.info['_id'],headers=headers,files=files,proxies=self.proxies)
        
        if r.status_code == requests.codes.ok:
            old_avatar = self.info['avatar']
            upload_response = r.text
            tmpinfo = json.loads(upload_response.decode('utf8'))
            if tmpinfo['avatar'] != old_avatar:
                self.info = tmpinfo
                return True
            else:
                self.info = json.loads(upload_response.decode('utf8'))
                return False
        else:
            return False

    #PUT to users/UID
    def editProfile(self,gender,bio,website,name,location,username,email,birthday):
        #gender syntax: 0 = male, 1 = female
        #birthday syntax: 1990-02-01 (Y-M-D)
        payload = {
            "user[gender]": gender,
            "user[bio]" : bio,
            "user[website]" : website,
            "user[name]" : name,
            "user[location]" : location,
            "user[username]" : username,
            "user[email]" : email,
            "user[birthday]" : birthday + "T05:00:00Z"
        }
        
        headers = {
            "accept" : "application/json",
            "accept-language" : "en",
            "connection" : "keep-alive",
            "x-user-authentication-token" : self.authToken,
            "x-client-version" : self.clientVersion,
            "x-device-id" : self.deviceId,
            "user-agent" : self.useragent
        }
        if self.proxies == None:
            r = requests.put(self.base + "/users/" + self.info['_id'],headers=headers,data=payload)
        else:
            r = requests.put(self.base + "/users/" + self.info['_id'],headers=headers,data=payload,proxies=self.proxies)
        
        if r.status_code == requests.codes.ok:
            edit_response = r.text
            tmpinfo = json.loads(edit_response.decode('utf8'))
            self.info = tmpinfo
            return True
        else:
            return False
            
    #Get the followers for the UserID - page = page number to fetch.
    def getFollowers(self,uid,page):
        headers = {
            "accept" : "application/json",
            "accept-language" : "en",
            "connection" : "keep-alive",
            "x-user-authentication-token" : self.authToken,
            "x-client-version" : self.clientVersion,
            "x-device-id" : self.deviceId,
            "user-agent" : self.useragent
        }
        
        fresp = self.get(self.base + "/users/" + uid + "/followers?page=" + str(page),headers)
        if fresp == False:
            return False
        else:
            resp = json.loads(fresp.encode('utf8'))
            return resp
    
    #Follow a user
    def follow(self,uid):
        headers = {
            "content-type" : "application/x-www-form-urlencoded",
            "accept" : "application/json",
            "accept-language" : "en",
            "connection" : "keep-alive",
            "x-user-authentication-token" : self.authToken,
            "x-client-version" : self.clientVersion,
            "x-device-id" : self.deviceId,
            "user-agent" : self.useragent
        }
        fresp = self.post(self.base + "/users/" + uid + "/follow",headers,None)
        if fresp == False:
            return False
        else:
            resp = json.loads(fresp.encode('utf8'))
            if resp['is_followed_by_me'] == True:
                return True
            else:
                return False
    
    #Reboom/retweet an item. 2nd parameter is the text to put.
    def reboom(self,itemid,body):
        payload = {
            "body": body
        }
        headers = {
            "content-type" : "application/x-www-form-urlencoded",
            "accept" : "application/json",
            "accept-language" : "en",
            "connection" : "keep-alive",
            "x-user-authentication-token" : self.authToken,
            "x-client-version" : self.clientVersion,
            "x-device-id" : self.deviceId,
            "user-agent" : self.useragent
        }
        rresp = self.post(self.base + "/items/" + itemid + "/retweet",headers,payload)
        if rresp == False:
            return False
        else:
            resp = json.loads(rresp.encode('utf8'))
            return True