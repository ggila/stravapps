import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

strava_id = ['StravaGPX', 'strava.com Android']

class gpx(object):
    '''
        gpx file interface

        gpx is an XML schema designed as a common GPS data format for software applications.
        This class has read() and write() methods for reading and writing gpx file.


        from gps 1.1 doc:
            <gpx
            version="1.1 [1]"
            creator="xsd:string [1]"> 
                <metadata> metadataType </metadata> [0..1] 
                <wpt> wptType </wpt> [0..*] 
                <rte> rteType </rte> [0..*] 
                <trk> trkType </trk> [0..*] 
                <extensions> extensionsType </extensions> [0..1] 
            </gpx>
        from gps 1.1 doc:
            <metadata> 
                <name> xsd:string </name> [0..1] 
                <desc> xsd:string </desc> [0..1] 
                <author> personType </author> [0..1] 
                <copyright> copyrightType </copyright> [0..1] 
                <link> linkType </link> [0..*] 
                <time> xsd:dateTime </time> [0..1]
                <keywords> xsd:string </keywords> [0..1] 
                <bounds> boundsType </bounds> [0..1] 
                <extensions> extensionsType </extensions> [0..1] 
            </metadata>

        from gps 1.1 doc:
            <trk> 
                <name> xsd:string </name> [0..1] 
                <cmt> xsd:string </cmt> [0..1] 
                <desc> xsd:string </desc> [0..1] 
                <src> xsd:string </src> [0..1] 
                <link> linkType </link> [0..*] 
                <number> xsd:nonNegativeInteger </number> [0..1] 
                <type> xsd:string </type> [0..1] 
                <extensions> extensionsType </extensions> [0..1] 
                <trkseg> trksegType </trkseg> [0..*] 
            </trk>

        from gps 1.1 doc:
            <trkseg> 
                <trkpt> wptType </trkpt> [0..*] 
                <extensions> extensionsType </extensions> [0..1] 
            </trkseg>
    '''

    _xml_namespace = '{http://www.topografix.com/GPX/1/1}'

    class garmin(object):
        time_format = '%Y-%m-%dT%H:%M:%S.000Z'

    class strava(object):
        time_format = '%Y-%m-%dT%H:%M:%SZ'

    def __repr__(self):
        pass

    @staticmethod
    def read(gpx_file):
        '''return a dict describing activities'''
        # parse xml file
        it = ET.iterparse(gpx_file)
        for _, el in it:
            if '}' in el.tag: el.tag = el.tag.split('}', 1)[1]    # drop xml namespace
        root = it.root
        origin = gpx.strava() if root.attrib['creator'] in strava_id else gpx.garmin() # garmin and strava don't have the same format. gpx tag has an attrib creator which tell us file origin.

        #unpack xml (for now, we consider only gpx with one track)
        metadata, (trkName, trkPt) = list(root)
        
        #get info
        time = gpx._readTime(metadata, origin.time_format)
        trk_lst = []
        for pt in trkPt:
            trk_lst.append(gpx._readTrkPt(pt, time, origin.time_format))
        
        return {'origin': origin.__class__.__name__,
                'name': trkName.text,
                'time': time,
                'track': trk_lst}

    @staticmethod
    def _readTime(meta, time_format):
        '''return datetime from metadata xml element'''
        time = meta.find('time'.format(gpx._xml_namespace)).text
        return datetime.strptime(time, time_format)

    @staticmethod
    def _readDeltaTime(time, t0, time_format):
        return datetime.strptime(time, time_format) - t0

    @staticmethod
    def _addAttr(ptDict, pTag, attr, func):
            tag = pTag.find(attr)
            if tag is not None:
                ptDict[attr] = func(tag.text)

    @staticmethod
    def _readTrkPt(pt, t0, tf):
        '''setup track points list from trkseg xml element'''
        ptDict = {k: float(v) for k, v in pt.attrib.items()}  # get lon and lat
        for attr, func in (('ele', float),
                           ('time', lambda t: gpx._readDeltaTime(t, t0, tf)),):
            gpx._addAttr(ptDict, pt, attr, func)
        extensions = pt.find('extensions')
        if extensions is not None:
            for attr, func in (('hr', int),
                               ('cad', int),
                               ('atemp', int),):
                gpx._addAttr(ptDict, extensions[0], attr, func)
        return ptDict