import pandas as pd
import requests,json,brotli
from .scraper import getepochtime


class EaseMyTrip:
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
        self.dateOfJourney = f"{tempDate[0]:02}-{tempDate[1]:02}-{tempDate[2]:02}"

    def getcityids(self,cityname:str):
        url=f"https://busservice.easemytrip.com/api/search/getsourcecity?id={cityname.title()}"
        response=requests.get(url);
        response=response.json();
        for i in response:
            if(i['name'] == cityname.title()):
                return i;
    def gettime(self,l):
        l=l.replace('T'," ")
        l=l.replace('+'," ")
        l=l.split()[:2]
        return f"{l[0]} {l[1]}"

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
            'emtFare':[],
            'startepoch':[],
            'endepoch':[],
            # 'rbfareList':[]
        }
        for i in data:#bc=>bus ac or non ac seeter
            buses['type'].append(i['busType'])
            buses['name'].append(i['Travels'])
            buses['boardpoint'].append(i['bdPoints'][0]['bdPoint'])
            buses['depaturepoint'].append(i['dpPoints'][len(i['dpPoints'])-1]['dpName'])
            buses['emtFare'].append(i['amount'])
            buses['Bpcount'].append(len(i['bdPoints']))
            arrivalTime=self.gettime(i['arrivalDate'])
            depature=self.gettime(i['departureDate'])
            buses['startTime'].append(arrivalTime)
            buses['endtime'].append(depature)
            buses['startepoch'].append(getepochtime(arrivalTime))
            buses['endepoch'].append(getepochtime(depature))

        dataframe = pd.DataFrame(buses)
        self.dataFrame=dataframe
        # dataframe.to_json('easemytrip.json',orient='records')
   
    def reponse_url(self,from_city={"id":None,"name":None},to_city={"id":None,"name":None},dateOJ={"DD":None,"MMM":None,'YYYY':None}):#fromcity={id,name},tocity={id,name},date=f"{DD}-{MMM}-{YYYY}"
        redbus_base_url=f"https://busservice.easemytrip.com/api/Home/GetSearchResult/"
        return redbus_base_url

    def form_queryurl(self,from_city={"id":None,"name":None},to_city={"id":None,"name":None},dateOJ={"DD":None,"MMM":None,'YYYY':None}):
        print(type(from_city),type(to_city),dateOJ)
        redbus_query_url=f"https://bus.easemytrip.com/home/list?org={from_city['name']}&des={to_city['name']}&date={dateOJ}&searchid={from_city['id']}_{to_city['id']}"
        return redbus_query_url

    def decompressdata(self,dataOfRequest):
        data=json.loads(brotli.decompress(dataOfRequest).decode())
        return data['Response']['AvailableTrips']
