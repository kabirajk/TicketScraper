var Scrapper = {
    init : function () {
        this.tableBody=$("#tablebody");
        this.fetchButton = $("#fetchButton");
        this.fromcityInput=$("#fromcityInput");
        this.tocityInput=$("#tocityInput");
        this.dateInput=$("#dateInput");
        this.chartCanvas=$("#busDataCanvas");
        this.Foundbus=$("#dataTable_info");
        this.fromtotext=$("#fromtotext");
        this.seachBox=$("#searchbus");
        this.bindEvents();
    },
    bindEvents : function(){
       var base = this;
       base.fetchButton.on('click',function(event){
        event.preventDefault()
        let forminput={
            'fromcity' : base.fromcityInput.val(),
            'tocity' : base.tocityInput.val(),
            'dateOfJourney': base.dateInput.val()
        };
        fetch("/fecthbus", {
        "headers": {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-site": "same-origin",
            'Access-Control-Allow-Origin': null,

        },
        "referrerPolicy": "strict-origin-when-cross-origin",
        "body":  JSON.stringify(forminput),
        "method": "POST",
        "mode": "cors",
        "credentials": "omit"
        }).then((response)=>{
            if(response.ok){
                response.json().then((jsondata)=>{
                    if(jsondata['error'] != undefined){
                        base.fromtotext.text(jsondata['error'])
                    }
                    else{
                    base.scrapped = jsondata
                    base.busdata = JSON.parse(jsondata['scrapped'])
                    base.busUrls = jsondata['queryurls']
                    let details=Scrapper.scrapped.details
                    base.fromtotext.html(`${details.fromcity} To ${details.tocity} on ${details.dateOfJourney} 
                    <a class="btn btn-primary btn-sm d-none d-sm-inline-block" role="button" target="_blank" href="${base.busUrls['rb']}">RedBus</a>
                    <a class="btn btn-primary btn-sm d-none d-sm-inline-block" role="button" target="_blank" href="${base.busUrls['ix']}">Ixigo</a>
                    <a class="btn btn-primary btn-sm d-none d-sm-inline-block" role="button" target="_blank" href="${base.busUrls['emt']}">EaseMytrip</a>
                    `);
                    base.Foundbus.text(`Found ${base.busdata.length} busses`);
                    $(document).trigger('scrapperdetails',{'data':base.busdata});
                    }
                });
            }
            });
       });
       $(document).on('scrapperdetails',function(ev,data){
        console.log(data);
        base.tableBody.empty();
        $.each(data.data,function(index,busObject){
            base.tableBody.append(base.createTabrow(busObject));
        });
        if(typeof base.chartObject == "undefined"){
            base.renderCanvas();
        }
        else{
            base.removeData(base.chartObject)
            data=[]
            data.push(base.getDataFrom('rbFare'))
            data.push(base.getDataFrom('ixigoFare'))
            data.push(base.getDataFrom('emtFare'))
            base.addData(base.chartObject,base.getDataFrom('name'),data)
        }
       });
       base.seachBox.on('keyup',function(ev){
        base.searchBus()
       });
    },
    createTabrow : function( busObject){
        return $(`<tr>
        <td class="bus-name">${busObject.name}</td>
        <td>${busObject.type}</td>
        <td>${busObject.rbFare!='false'?busObject.rbFare:'None'}</td>
        <td>${busObject.ixigoFare!='false'?busObject.ixigoFare:'None'}</td>
        <td>${busObject.emtFare!='false'?busObject.emtFare:'None'}</td>
        <td>${busObject.startTime}</td>
        <td>${busObject.endtime}</td>
        </tr>`);
    },
    getDataFrom : function (typestr) {
        let jsondata = this.busdata; 
        let newArray = []
        jsondata.forEach(function (bus) {
            let value=""
            if(typestr=="name"){
                value=[bus[typestr],bus['type']]
                if(bus[typestr]==undefined){
                    value=""
                }
            }
            else{
                if(typestr.endsWith('Fare')){
                    if(bus[typestr]=='false'){
                        value=0
                    }
                    else{
                        value=bus[typestr]
                    }
                }
                else{
                    value=bus[typestr]
                }
            }
            newArray.push(value);
        });
        return newArray;
    },
    renderCanvas : function(){
        var base = this;
        var chart = base.chartCanvas;
        var chartObj = new Chart(chart, {
            type: 'bar',
            labels: base.getDataFrom('name'),
            data: {
                labels: base.getDataFrom('name'),
                datasets: [
                    {
                        label: 'redBUS',
                        data: base.getDataFrom('rbFare'),
                        borderColor: 'rgba(255, 77, 77, 1)',
                        backgroundColor: 'rgba(255, 77, 77, 0.5)',
                    },
                    {
                        label: 'Ixigio',
                        data: base.getDataFrom("ixigoFare"),
                        borderColor: 'rgba(0, 99, 132, 1)',
                        backgroundColor: 'rgba(0, 99, 132, 0.6)',
                    },
                    {
                        label: 'easeMytrip',
                        data: base.getDataFrom("emtFare"),
                        borderColor: 'rgba(100, 99, 132, 1)',
                        backgroundColor: 'rgba(100, 99, 132, 0.6)',
                    }
                ]
            },
            options: {
            indexAxis: 'x',
            // Elements options apply to all of the options unless overridden in a dataset
            // In this case, we are setting the border of each horizontal bar to be 2px wide
            elements: {
              bar: {
                borderWidth: 1,
                Category: 1.0,
                Bar:0.5,
                categoryPercentage: 1.0,
                barPercentage: 0.5
              }
            },
            responsive: true,
            plugins: {
              legend: {
                position: 'right',
              },
              title: {
                display: true,
                text: 'Chart.js'
              }
            }
          },
            DATA_COUNT : base.busdata.length,    
            });
        base.chartObject=chartObj
    },
    addData:function(chart, label, data) {
        chart.data.labels=label;
        chart.data.datasets.forEach((dataset,index) => {
            dataset.data=data[index];
        });
        chart.update();
    },

    removeData:function(chart) {
        chart.data.labels=[];
        chart.data.datasets.forEach((dataset) => {
            dataset.data=[]
        });
        chart.update();
    },
    searchBus : function(){
        let busnames=$(".bus-name");
        let seachquery = $("#searchbus").val();
        seachquery.toLowerCase()
        seachquery.trim()
        $.each(busnames,function(index,data){
            let busname = $(data).text()
            busname=busname.toLowerCase()
            if(busname.indexOf(seachquery)==-1){
                $(data).closest('tr').hide();
            }
            else{
                $(data).closest('tr').show();
            }
        });
    }
};