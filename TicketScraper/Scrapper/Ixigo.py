import pandas as pd
# from seleniumwire import webdriver
import requests,json,brotli
from .scraper import getepochtime
# def getepochtime(datestr):

class Ixigo:
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
        self.dateOfJourney = f"{tempDate[0]:02}{tempDate[1]:02}{tempDate[2]:02}"
    
    def getcitylist(self,city:list):
        city_Name=city['stationName']
        city_id=city['stationId']
        boradpoints=[]
        return{'name':city_Name,'id':city_id,'boradpoints':boradpoints}

    def getcityids(self,cityname:str):
        url=f"https://www.ixigo.com/api/v1/suggest/bus-station?input={cityname.title()}"
        response=requests.get(url);
        response=response.json();
        if len(response['data']):
            response=response['data'];
            newlist=[]
            for area in response:
                newlist.append(self.getcitylist(area))
        print(cityname,newlist[0])
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
            'ixigoFare':[],
            'startepoch':[],
            'endepoch':[],
            # 'rbfareList':[]
        }
        for i in data:#bc=>bus ac or non ac seeter
            buses['type'].append(i['busTypeName'])
            buses['name'].append(i['travelerAgentName'])
            buses['boardpoint'].append(i['sourceStationName'])
            buses['depaturepoint'].append(i['destinationStationName'])
            buses['ixigoFare'].append(i['seatFare'])
            buses['Bpcount'].append(len(i['boardingPoints']))
            # buses['bplist'].append(str(i['bpData']))
            # buses['rbfareList'].append(str(i['frLst']))
            buses['startTime'].append(i['journeyDate']+" "+i['startTime'])
            buses['endtime'].append(i['droppingPoints'][len(i['droppingPoints'])-1]['arrivalDateTime'].replace('T',' '))
            buses['startepoch'].append(getepochtime(i['journeyDate']+" "+i['startTime']))
            buses['endepoch'].append(getepochtime(i['droppingPoints'][len(i['droppingPoints'])-1]['arrivalDateTime'].replace('T',' ')))

        dataframe = pd.DataFrame(buses)
        self.dataFrame=dataframe
        # print("ixigo Data frame",dataframe)
        # dataframe.to_json('ixigo.json',orient='records')
   
    def reponse_url(self,from_city={"id":None,"name":None},to_city={"id":None,"name":None},dateOJ={"DD":None,"MMM":None,'YYYY':None}):#fromcity={id,name},tocity={id,name},date=f"{DD}-{MMM}-{YYYY}"
        redbus_base_url=f"https://www.ixigo.com/bus/v2/search"
        return redbus_base_url

    def form_queryurl(self,from_city={"id":None,"name":None},to_city={"id":None,"name":None},dateOJ={"DD":None,"MMM":None,'YYYY':None}):
        print(type(from_city),type(to_city),dateOJ)
        redbus_query_url=f"https://www.ixigo.com/search/result/bus/{from_city['id']}/{to_city['id']}/{dateOJ}"
        return redbus_query_url
    def decompressdata(self,dataOfRequest):
        data=json.loads(brotli.decompress(dataOfRequest).decode())
        if( not data.get('data') and not (data.get('data')).get('busServices') ):
            return None
        return data['data']['busServices']
