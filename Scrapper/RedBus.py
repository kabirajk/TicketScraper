import pandas as pd
import gzip,requests,json,datetime
from .scraper import getepochtime

class RedBus:
    def __init__(self,fromcity,tocity,dateOfJourney) -> None:
        self.fromcity=fromcity
        self.fromCityData=self.getcityids(fromcity)
        self.tocity=tocity
        self.toCityData=self.getcityids(tocity)
        self.dateOfJourney=dateOfJourney
        self.dataFrame=None
        self.getFormatedDate()
        self.searchQuery=self.form_queryurl(self.fromCityData,self.toCityData,self.dateOfJourney)
        self.responseURL=self.reponse_url(self.fromCityData,self.toCityData,self.dateOfJourney)

    def changeValue(self,fromcity,tocity,dateOfJourney):
        self.fromcity=fromcity
        self.fromCityData=self.getcityids(fromcity)
        self.tocity=tocity
        self.toCityData=self.getcityids(tocity)
        self.dateOfJourney=dateOfJourney
        self.dataFrame=None
        self.getFormatedDate()
        self.searchQuery=self.form_queryurl(self.fromCityData,self.toCityData,self.dateOfJourney)
        self.responseURL=self.reponse_url(self.fromCityData,self.toCityData,self.dateOfJourney)

    def getFormatedDate(self):
        tempDate=list(map(int,self.dateOfJourney.split('-')))
        months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        tempDate[1] = months[(tempDate[1]-1)]
        self.dateOfJourney = f"{tempDate[0]:02}-{tempDate[1]}-{tempDate[2]}"
    
    def getcitylist(self,city):
        city_Name=city['Name']
        city_id=city['ID']
        boradpoints=[]
        # print(type(city['BpList']),type(None))
        if(type(city['BpList'])!=type(None)):
            for i in city['BpList']:
                boradpoints.append({'name':i['Name'],'id':i['ID']})
        return {'name':city_Name,'id':city_id,'boradpoints':boradpoints}

    def getcityids(self,cityname:str):
        url=f"https://www.redbus.in/Home/SolarSearch?search={cityname.lower()}&parentLocationId=14&parentId=602&parentLocationType=CITY"
        response=requests.get(url);
        response=response.json();
        newlist=[]
        if response['response']['numFound']>=1:
            response=response['response']['docs'];
            
            for area in response:
                # print(area)
                newlist.append(self.getcitylist(area))
        # print(type(newlist[0]))
        return newlist[0]

    def getessentialdetails(self,data:dict):
        if(type(data)==type(None)): return
        buses ={
            'name':[],
            'startTime':[],
            'endtime':[],
            'boardpoint':[],
            'depaturepoint':[],
            'Bpcount':[],
            # 'bplist':[],
            'type':[],
            'rbFare':[],
            'startepoch':[],
            'endepoch':[],
            # 'rbfareList':[],
        }
        for i in data:#bc=>bus ac or non ac seeter
            buses['type'].append(i['bt'])
            buses['name'].append(i['Tvs'])
            buses['boardpoint'].append(i['StdBp'])
            buses['depaturepoint'].append(i['StdDp'])
            buses['rbFare'].append(i['minfr'])
            buses['Bpcount'].append(len(i['bpData']))
            # buses['bplist'].append(str(i['bpData']))
            # buses['rbfareList'].append(str(i['frLst']))
            buses['startTime'].append(i['StdBpFullTime'])
            buses['endtime'].append(i['StdDpFullTime'])
            buses['startepoch'].append(getepochtime(i['StdBpFullTime']))
            buses['endepoch'].append(getepochtime(i['StdDpFullTime']))
        
        dataframe = pd.DataFrame(buses)
        self.dataFrame=dataframe
        # dataframe.to_json('redbus.json',orient='records')

   
    def reponse_url(self,from_city={"id":None,"name":None},to_city={"id":None,"name":None},dateOJ={"DD":None,"MMM":None,'YYYY':None}):#fromcity={id,name},tocity={id,name},date=f"{DD}-{MMM}-{YYYY}"
        redbus_base_url=f"https://www.redbus.in/search/SearchResults?fromCity={from_city['id']}&toCity={to_city['id']}&src={from_city['name'].title()}&dst={to_city['name'].title()}&DOJ={dateOJ}&sectionId=0&groupId=0&limit=0&offset=0&sort=0&sortOrder=0&meta=true&returnSearch=0"
        return redbus_base_url

    def form_queryurl(self,from_city={"id":None,"name":None},to_city={"id":None,"name":None},dateOJ={"DD":None,"MMM":None,'YYYY':None}):
        redbus_query_url=f"https://www.redbus.in/bus-tickets/{from_city['name'].lower()}-to-{to_city['name'].lower()}?fromCityName={from_city['name'].title()}&fromCityId={from_city['id']}&toCityName={to_city['name'].title()}&toCityId={to_city['id']}&onward={dateOJ}&srcCountry=IND&destCountry=IND&opId=0&busType=Any"
        return redbus_query_url
    def decompressdata(self,dataOfRequest):
        data= (json.loads(gzip.decompress(dataOfRequest).decode()))
        return data.get('inv')

def getepochtime(datestr):
    # datestr=datestr.replace("T"," ")
    datestr = datestr.split()
    date1=datestr[0].split('-')
    date1=list(map(int,date1))
    time1=datestr[1].split(':')
    time1=list(map(int,time1))
    return  int(datetime.datetime(date1[0],date1[1],date1[2],time1[0],time1[1],time1[2]).timestamp())
