#!/usr/bin/python

import sys
from struct import *
from datetime import datetime
import base64
import xml.etree.ElementTree as ET
from io import BytesIO
import os

class alp2gpx(object):
    inputfile, outputfile = None, None
    fileVersion, headerSize = None, None
    metadata, waypoints, segments = None, None, None 
    
    def __init__(self, inputfile):
        self.inputfile = open(inputfile, "rb")
        self.outputfile = '%s.gpx' % os.path.splitext(inputfile)[0] 

        (self.fileVersion, self.headerSize)= self.check_version()        
        
        
        
    def _get_int(self):
        result = self.inputfile.read(4)
        return  unpack('>l', result)[0]
    
    def _get_double(self):
        result = self.inputfile.read(8)
        return  unpack('>d', result)[0]
    
    def _get_coordinate(self):
        result = self._get_int() * 1e-7;
        return result
    
    def _get_double(self):
        result = self.inputfile.read(8)
        return  unpack('>d', result)[0]
    
    def _get_long(self):
        result = self.inputfile.read(8)
        return  unpack('>q', result)[0]
     
    def _get_timestamp(self):
        result = self._get_long() * 1e-3;
        return result
    
    def _get_string(self, size):
        result = self.inputfile.read(size)
        return result.decode('UTF-8')
        
    def _get_int_raw(self):
        print('jell')
        size = self._get_int()
        value = self.inputfile.read(size)
        result = base64.b64encode(value)
        return result
    
    def _get_bool(self):
        result = self.inputfile.read(1)
        return unpack('c', result)[0]
    
    def _get_height(self):
        result = self._get_int()
        if result ==  -999999999:
            return None
        else:
            result *= 1e-3
        return result
    
    def _get_accuracy(self):
        return self._get_int()
    
    def _get_pressure(self):
        result = self._get_int()
        if result ==  999999999:
            return None
        else:
            result *= 1e-3
        return result        
    
    def _get_metadata(self, fileVersion):
        result = {}
        num_of_metaentries = self._get_int()
        for entry in range(num_of_metaentries):
            name_len = self._get_int()
            name = self._get_string(name_len)
            data_len = self._get_int()
            if data_len == -1:  data = self._get_bool()
            if data_len == -2:  data = self._get_long()
            if data_len == -3:  data = self._get_double()
            if data_len == -4:  data = self._get_int_raw()
            if data_len >= 0:  data = self._get_string(data_len)
            result[name] = data
        
        if fileVersion == 3:
            nmeta_ext = self._get_int()

        return result
    
    def _get_location(self):
        size = self._get_int()
        lon = self._get_coordinate()
        lat = self._get_coordinate()
        alt = self._get_height()
        ts = self._get_timestamp()
        
        acc,bar = None, None
        
        if size > 20:
            acc = self._get_accuracy()
        if size > 24:
            bar = self._get_pressure()
        
        result = { 'lat': lat, 'lon': lon, 'alt': alt, 'ts': ts, 'acc': acc, 'bar': bar}
        return result
    
    
    def _get_segment(self, segmentVersion):
        if segmentVersion < 3:
            self._get_int()
        else:
            meta = self._get_metadata(segmentVersion)
        
        nlocations = self._get_int()
        result = []
        for n in range(nlocations):
            location = self._get_location()
            result.append(location)
        return result
            
    def _get_segments(self, segmentVersion):
        num_segments = self._get_int()
        results = []
        for s in range(num_segments):
            segment = self._get_segment(segmentVersion)
            results.append(segment)
        return results
            
            
    def _get_waypoints(self):
        num_waypoints = self._get_int()
        result = []
        for wp in range(num_waypoints):
            meta = self._get_metadata(self.fileVersion)
            location = self._get_location()
            result.append({'meta': meta, 'location': location})
        return result
        
        
    def total_track_time(self):
        self.inputfile.seek(60)
        result = self._get_long()
        return result        
        
    def total_track_elevation_gain(self):
        self.inputfile.seek(52)
        result = self._get_double()
        return result        
        
    def total_track_length_due_to_elevation(self):
        self.inputfile.seek(44)
        result = self._get_double()
        return result
         
    def total_track_length(self):
        self.inputfile.seek(36)
        result = self._get_double()
        return result
    
    def time_of_first_location(self):
        self.inputfile.seek(28)
        result = datetime.fromtimestamp(self._get_timestamp())
        return result
    
    def latitude_of_first_location(self):
        self.inputfile.seek(24)
        result = self._get_coordinate()
        return result
    
    def longitude_of_first_location(self):
        self.inputfile.seek(20)
        result = self._get_coordinate()
        return result
    
    def number_of_waypoints(self):
        self.inputfile.seek(16)
        result = self._get_int()     
        return(result)
    
    def number_of_segments(self):
        self.inputfile.seek(12)
        result = self._get_int()     
        return(result)
     
    def number_of_locations(self):
        self.inputfile.seek(8)
        result = self._get_int()     
        return(result)
    
        
    def check_version(self):
        self.inputfile.seek(0)
        file_version = self._get_int()
        header_size  = self._get_int()          
        return (file_version, header_size);
    
    def write_xml(self):
        '''
        <?xml version="1.0" encoding="UTF-8"?>
        <gpx version="1.0">
            <metadata>
            <desc>description</desc>
            <link href="" />
            <time>2020-04-18T13:26:36Z</time>
            </metadata>
            <wpt lat="46.57638889" lon="8.89263889">
                <ele>2372</ele>
                <name>LAGORETICO</name>
            </wpt>
            <trk><name>Example gpx</name><number>1</number><trkseg>
                <trkpt lat="46.57608333" lon="8.89241667"><ele>2376</ele><time>2007-10-14T10:09:57Z</time></trkpt>
                <trkpt lat="46.57619444" lon="8.89252778"><ele>2375</ele><time>2007-10-14T10:10:52Z</time></trkpt>
                <trkpt lat="46.57641667" lon="8.89266667"><ele>2372</ele><time>2007-10-14T10:12:39Z</time></trkpt>
                <trkpt lat="46.57650000" lon="8.89280556"><ele>2373</ele><time>2007-10-14T10:13:12Z</time></trkpt>
                <trkpt lat="46.57638889" lon="8.89302778"><ele>2374</ele><time>2007-10-14T10:13:20Z</time></trkpt>
                <trkpt lat="46.57652778" lon="8.89322222"><ele>2375</ele><time>2007-10-14T10:13:48Z</time></trkpt>
                <trkpt lat="46.57661111" lon="8.89344444"><ele>2376</ele><time>2007-10-14T10:14:08Z</time></trkpt>
            </trkseg></trk>
        </gpx>
        '''
        name = self.metadata.get('name', datetime.now().strftime("%Y%m%d-%H%M%S"))
        
        root = ET.Element('gpx', version = '1.1', xmlns="http://www.topografix.com/GPX/1/1" )
        tree = ET.ElementTree(root)
        metadata = ET.SubElement(root, 'metadata')
        desc = ET.SubElement(metadata, 'desc')
        desc.text = name
        link = ET.SubElement(metadata, 'link', href='https://github.com/jachetto/alp2gpx')
        
        for wp in self.waypoints:
            wpt = ET.SubElement(root, 'wpt', lat = '%s' % wp['location']['lat'], lon = '%s' % wp['location']['lon'] )
            node = ET.SubElement(wpt, 'ele')
            node.text = '%s' % wp['location']['alt']
            node = ET.SubElement(wpt, 'name')
            node.text = wp['meta']['name']
        for s in self.segments:
            trk = ET.SubElement(root, 'trk')
            trkseg = ET.SubElement(trk, 'trkseg')
            for p in s:
                trkpt = ET.SubElement(trkseg, 'trkpt', lat = '%s' % p['lat'], lon = '%s' % p['lon'] )
                node = ET.SubElement(trkpt, 'ele')
                node.text = '%s' % p['alt']                
                d = datetime.fromtimestamp(int(p['ts']))
                tz = d.strftime("%Y-%m-%dT%H:%M:%SZ")
                node = ET.SubElement(trkpt, 'time')
                node.text = tz
                
        tree.write(open(self.outputfile, 'w'), encoding='utf-8', xml_declaration=True)
        
        
    def parse_trk(self):
        # version 3 (version 2 is the same but uses a different {Metadata} and {Segments} struct
        # - int         file version
        # - int         header size (size of data to before {Metadata}
        # - int         number of locations
        # - int         number of segments
        # - int         number of waypoints
        # - coordinate  longitude of first location
        # - coordinate  latitude of first location
        # - timestamp   time of first location
        # - double      total track length (in m)
        # - double      total track length due to elevation changes (in m)
        # - double      total track elevation gain (in m)
        # - long        total track time (in s)
        # - {Metadata}  (version 2)
        # - {Waypoints}
        # - {Segments}  (version 2)        
        
        '''
        JUST FOR API REFERENCE
        number_of_locations = self.number_of_locations()
        number_of_segments = self.number_of_segments()
        number_of_waypoints = self.number_of_waypoints()
        longitude_of_first_location = self.longitude_of_first_location()
        latitude_of_first_location = self.latitude_of_first_location()
        time_of_first_location = self.time_of_first_location()
        total_track_length = self.total_track_length()
        total_track_length_due_to_elevation = self.total_track_length_due_to_elevation()
        total_track_elevation_gain = self.total_track_elevation_gain()
        total_track_time = self.total_track_time()
        '''
        
        self.inputfile.seek(self.headerSize+8)
        self.metadata = self._get_metadata(self.fileVersion)
        self.waypoints = self._get_waypoints()
        self.segments = self._get_segments(self.fileVersion)
        self.write_xml()
        #self.inputfile.seek(0)
   
    
if __name__ == "__main__":
    q = alp2gpx(sys.argv[1])
    q.parse_trk()