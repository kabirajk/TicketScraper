from TicketScraper import app
import json,os
import pandas as pd
from flask import request,jsonify,render_template
from .Scrapper.scraper import scrapper

@app.route('/fecthbus',methods=['POST'])
def get_busdetails():
    input_json=request.get_json(force=True)
    formatedDate=input_json['dateOfJourney']
    formatedDate=formatedDate.split("-")
    formatedDate=f"{formatedDate[2]}-{formatedDate[1]}-{formatedDate[0]}"
    if(os.path.isfile((input_json['fromcity']+input_json['tocity']+formatedDate+'.json'))):
        file=open(input_json['fromcity']+input_json['tocity']+formatedDate+'.json')
        jsondata=json.load(file)
        return jsonify(jsondata)
    scrapped = None
    try:
        scrapped = scrapper(input_json['fromcity'],input_json['tocity'],formatedDate)
        # print(type(scrapped.mergedDataFrame))
        alreadyhave ={'details':input_json,'scrapped':scrapped.return_json(),'queryurls':scrapped.getSearchQuery()}
        return jsonify(alreadyhave)
    except ValueError as vs:
        print(vs)
        return jsonify({'error':f"{str(vs)}"})
    except  Exception as error:
        print("exception",error)
        if(str(error)=="BrotliDecompress failed"):
            alreadyhave ={'details':input_json,'scrapped':scrapped.return_json(),'queryurls':scrapped.getSearchQuery()}
            return jsonify(alreadyhave)
        if(str(error)=="'NoneType' object has no attribute 'get'"):
            return jsonify({'error':"No trips found"})
        return jsonify({'error':"we faced some error please try after some time"})
    # scrapped.mergedDataFrame.to_json(input_json['fromcity']+input_json['tocity']+formatedDate+'.json',orient='records')

    # return alreadyhave
    
@app.route('/')
def hello_world():
    return render_template('index.html')