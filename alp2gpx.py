#!/usr/bin/python

import sys
from struct import *
from datetime import datetime
import base64

class alp2gpx(object):
    inputfile = None
    fileVersion, headerSize = None, None
    
    def __init__(self, inputfile):
        self.inputfile = open(inputfile, "rb")
        (self.fileVersion, self.headerSize)= self.check_version()        
        
        self.parse_trk()
        
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
        result = []
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
            result.append({name: data})
        
        if fileVersion == 3:
            nmeta_ext = self._get_int()
            
        print('Metantries %s' % result)
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
        print('Total track time %s' % result)
        return result        
        
    def total_track_elevation_gain(self):
        self.inputfile.seek(52)
        result = self._get_double()
        print('Total elevation gain %s' % result)
        return result        
        
    def total_track_length_due_to_elevation(self):
        self.inputfile.seek(44)
        result = self._get_double()
        print('Total track length due to elevation %s' % result)
        return result
         
    def total_track_length(self):
        self.inputfile.seek(36)
        result = self._get_double()
        print('Total track length %s' % result)
        return result
    
    def time_of_first_location(self):
        self.inputfile.seek(28)
        result = datetime.fromtimestamp(self._get_timestamp())
        print('Time of first location %s' % result)
        return result
    
    def latitude_of_first_location(self):
        self.inputfile.seek(24)
        result = self._get_coordinate()
        print('Latitude of first location %s' % result)
        return result
    
    def longitude_of_first_location(self):
        self.inputfile.seek(20)
        result = self._get_coordinate()
        print('Longitude of first location %s' % result)
        return result
    
    def number_of_waypoints(self):
        self.inputfile.seek(16)
        result = self._get_int()     
        print('Number of waypoints %s' % result)
        return(result)
    
    def number_of_segments(self):
        self.inputfile.seek(12)
        result = self._get_int()     
        print('Number of segments %s' % result)
        return(result)
     
    def number_of_locations(self):
        self.inputfile.seek(8)
        result = self._get_int()     
        print('Number of locations %s' % result)
        return(result)
    
        
    def check_version(self):
        self.inputfile.seek(0)
        file_version = self._get_int()
        header_size  = self._get_int()          
        print('fileVersion=%s headerSize=%s' % (file_version, header_size))
        return (file_version, header_size);
    
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
        self.inputfile.seek(self.headerSize+8)
        metadata = self._get_metadata(self.fileVersion)
        waypoints = self._get_waypoints()
        segmentn = self._get_segments(self.fileVersion)
        #self.inputfile.seek(0)
   
    
if __name__ == "__main__":
    q = alp2gpx(sys.argv[1])