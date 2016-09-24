import xmltodict

def get_activity_json(gpx):
    ''' 

        open activity from gpx file


                     in . gpx . path of gpx file
                              . type . string
                     out . a . activity.json
                             . type . collections.OrederdDict


    In [2]: a = get_activity('run.gpx')
    
    In [3]: a.keys()
    Out[3]: [u'gpx']
    
    In [4]: a['gpx'].keys()
    Out[4]:
    [u'@version',
     u'@creator',
     u'@xsi:schemaLocation',
     u'@xmlns',
     u'@xmlns:gpxtpx',
     u'@xmlns:gpxx',
     u'@xmlns:xsi',
     u'metadata',
     u'trk']

     cf ./gpx.py for details

    '''
    with open(gpx, 'r') as f:
        parsed_gpx = xmltodict.parse(f.read())
        a = parsed_gpx['gpx']
    return a
