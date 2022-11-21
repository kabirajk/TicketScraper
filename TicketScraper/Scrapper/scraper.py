from time import sleep
import pandas as pd
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import gzip,requests,json,brotli,datetime,os

def getepochtime(datestr):
    # datestr=datestr.replace("T"," ")
    datestr = datestr.split()
    date1=datestr[0].split('-')
    date1=list(map(int,date1))
    time1=datestr[1].split(':')
    time1=list(map(int,time1))
    return  int(datetime.datetime(date1[0],date1[1],date1[2],time1[0],time1[1],time1[2]).timestamp())

from .RedBus import RedBus
from .Ixigo import Ixigo
from .EaseMyTrip import EaseMyTrip

class scrapper:
    def __init__(self,fromcity,tocity,dateOfJourney) -> None:
        self.fromcity=fromcity
        self.tocity=tocity
        self.dateOfJourney=dateOfJourney
        self.busObject=[]
        self.mergedDataFrame=None
        Chromeoptions=webdriver.ChromeOptions()
        # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53'
        Chromeoptions.add_argument(f'user-agent={user_agent}')
        Chromeoptions.add_argument('--headless')
        driverPath=os.getcwd()+"\TicketScraper\Scrapper\chromedriver.exe"
        # print(os.getcwd())
        self.webdriver=webdriver.Chrome(executable_path=ChromeDriverManager().install(),options=Chromeoptions);
        self.busObject.append(RedBus(fromcity,tocity,dateOfJourney))
        self.busObject.append(Ixigo(fromcity,tocity,dateOfJourney))
        self.busObject.append(EaseMyTrip(fromcity,tocity,dateOfJourney))

        for i in self.busObject:
            self.response_body(i)
        self.webdriver.quit()
    def refetch(self,fromcity,tocity,dateOfJourney):
        self.fromcity=fromcity
        self.tocity=tocity
        self.dateOfJourney=dateOfJourney
        for busData in self.busObject:
            busData.changeValue(fromcity,tocity,dateOfJourney)
    def return_json(self):
        self.mergedDataFrame=self.busObject[0].dataFrame
        fareList=['rbFare','ixigoFare','emtFare']
        for i in range(1,len(self.busObject)):
            print(self.busObject[i].dataFrame)
            self.mergeDataframes(self.busObject[i].dataFrame,fareList[:i+1])
        return self.mergedDataFrame.to_json(orient='records')
    def getSearchQuery(self):
        urls={'rb':'','ix':"",'emt':""}
        urls['rb']=self.busObject[0].searchQuery;
        urls['ix']=self.busObject[1].searchQuery;
        urls['emt']=self.busObject[2].searchQuery;
        return urls
    def mergeDataframes(self,dataframe,fareList):
        # print(fareList)
        print(type(dataframe),dataframe)
        if(type(dataframe) == type(None)):
            return
        merged=pd.merge(self.mergedDataFrame,dataframe,how="outer",on=['name','startepoch','endepoch'])
        merged=merged.fillna(False)
        newmerged=pd.DataFrame()
        fareDict=dict()
        for i in fareList:
            fareDict[i]=[]
        name = []	
        startTime = []
        endtime = []
        boardpoint = []
        depaturepoint = []
        Bpcount = []
        btype = []
        # rbFare = []
        # ixigoFare= []
        emtFare=[]
        startepoch = []
        endepoch = []
        for i in range(0,merged.shape[0]):
            name.append(merged['name'][i])
            startTime.append(merged['startTime_x'][i] if merged['startTime_x'][i] else merged['startTime_y'][i])
            endtime.append(merged['endtime_x'][i] if merged['endtime_x'][i] else merged['endtime_y'][i])
            boardpoint.append(merged['boardpoint_x'][i] if merged['boardpoint_x'][i] else merged['boardpoint_y'][i])
            depaturepoint.append(merged['depaturepoint_x'][i] if merged['depaturepoint_x'][i] else merged['depaturepoint_y'][i])
            Bpcount.append(merged['Bpcount_x'][i] if merged['Bpcount_x'][i] else merged['Bpcount_y'][i])  
            btype.append(merged['type_x'][i] if merged['type_x'][i] else merged['type_y'][i])
            # rbFare.append(merged['rbminFare_x'][i] if merged['rbminFare_x'][i] else 'false')
            # ixigoFare.append(merged['rbminFare_y'][i] if merged['rbminFare_y'][i] else 'false')
            for site in fareList:
                if(site in merged):
                    fareDict[site].append(merged[site][i] if merged[site][i] else 'false')

            startepoch.append(merged['startepoch'][i])
            endepoch.append(merged['endepoch'][i])
        newmerged['name']	= name
        newmerged['startTime'] =startTime
        newmerged['endtime']=endtime
        newmerged['boardpoint']=boardpoint
        newmerged['depaturepoint']=depaturepoint
        newmerged['Bpcount']=Bpcount
        newmerged['type']=btype
        # newmerged['rbFare']=rbFare
        # newmerged['ixigoFare']=ixigoFare
        for site in fareList:
                newmerged[site]=fareDict[site]
        newmerged['startepoch']=startepoch
        newmerged['endepoch']=endepoch

        self.mergedDataFrame = newmerged

    def response_body(self,busData):
        fromcity=busData.fromCityData
        tocity=busData.toCityData
        # driver = webdriver.Chrome();
        url=busData.searchQuery
        self.webdriver.get(url)
        for req in self.webdriver.requests:
            # print(req,end="\n\n")
            if(req.response and req.url==busData.responseURL):
                data=busData.decompressdata(req.response.body)
                # print(type(data))
                data=busData.getessentialdetails(data)
                # with open('D:\ytdl\TicketScrapper\Scrapper\index.html','w',encoding="utf-8") as f:
                #     f.write(str(data))
                break
            
        # self.webdriver.quit()
        # self.webdriver.implicitly_wait(5)