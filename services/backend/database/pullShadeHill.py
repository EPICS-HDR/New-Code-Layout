import requests

def pullShadeHill(start_day, start_month, start_year, end_day, end_month, end_year):

    datasets = ["AF", "FB", "IN", "MM", "MN", "MX", "PP", "PU", "QD", "QRD", "QSD", "RAD"]

    for dataset in datasets:
        shadehillrequest(start_year, start_month, start_day, end_year, end_month, end_day, dataset)

def shadehillrequest(startyear, startmonth, startday, endyear, endmonth, endday, dataset):
    
    # URL of the form action
    url = "https://www.usbr.gov/gp-bin/arcread.pl"

    # Form data to be submitted
    form_data = {
        'st': 'SHR',
        'by': startyear,
        'bm': startmonth,
        'bd': startday,
        'ey': endyear,
        'em': endmonth,
        'ed': endday,
        'pa': dataset,
        # Data options: AF, FB, IN, MM, MN, PP, PU, QD, QRD, QSD, RAD
    }

    datasets = {
        'AF': "Reservoir Storage Content",
        'FB': "Reservoir Forebay Elevation",
        'IN': "Daily Mean Computed Inflow",
        'MM': "Daily Mean Air Temperature",
        'MN': "Daily Minimum Air Temperature",
        'MX': "Daily Maximum Air Temperature",
        'PP': "Total Precipitation (inches per day)",
        'PU': "Total Water Year Precipitation",
        'QD': "Daily Mean Total Discharge",
        'QRD': "Daily Mean River Discharge",
        'QSD': "Daily Mean Spillway Discharge",
        'RAD': "Daily Mean Gate One Opening",
    }

    dataname = datasets[dataset]

    # Sending the POST request
    response = requests.post(url, data=form_data)

    # Split the text into lines
    lines = response.text.strip().split('\r')

    count = 0
    times = []
    datas = []

    for line in lines: 
        if count >= 3:
            
            date = line.split(" ")[0]
            year = (date.split("/")[0]).strip("\n")
            month = date.split("/")[1]
            day = date.split("/")[2]

            # Accumulates data
            datas.append(line.split(" ")[-1])

            # Assumes midnight for every day, since time isn't provided
            times.append(year + "-" + month + "-" + day + " " + "00:00")

        count += 1
    
    del times[-1]
    del datas[-1]