"""
EXTRACT THE TICKET CREATE DATE IN THE AGREED FORMAT

"""

import re
from datetime import datetime, timedelta

class CreateDateExtractor:
    def __init__(self,
                 entity_name = 'Create_Date',
                 extraction_regex = "\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}",
                 inclusion_offset = 30,
                 inclusion_list = [],
                 timezone_offset = 0
                 ):
        
        self.entity_name = entity_name        
        self.extraction_regex = extraction_regex
        self.search_pattern = re.compile(self.extraction_regex, re.MULTILINE|re.IGNORECASE)
        self.timezone_offset = timezone_offset        
        
        self.inclusion_list=inclusion_list
        self.inclusion_offset=inclusion_offset  
        self.inclusion_pats = []
        for exc in self.inclusion_list:
            self.inclusion_pats.append(re.compile(exc, re.IGNORECASE))       

    def string_to_date_tokens(self, date_string):
        try:        
            year = int(date_string[:4])
            month = int(date_string[5:7])
            day = int(date_string[8:10])
            hour = int(date_string[11:13])
            minute = int(date_string[14:16])
            second = int(date_string[17:19]) 
        except:
            year = int(time.strftime("%Y"))
            month = int(time.strftime("%m"))
            day = int(time.strftime("%d"))
            hour = int(time.strftime("%H"))
            minute = int(time.strftime("%M"))
            second = int(time.strftime("%S")) 
        return year, month, day, hour, minute, second
        
    def get_matches(self, doc):
        '''
        Input: doc - string containing the ticket create date
        Returns: create date in agreed format
        '''
        doc = doc["create_date"]   
        res = []
        
        for p in self.search_pattern.finditer(doc):
            start_pos, end_pos = p.span()
            found_inc = False
            #Seacrh through all inclusion list items and tag True if found in at least one of them
            if not self.inclusion_list:
                found_inc = True    
            else:
                for inc_pat in self.inclusion_pats:
                    if inc_pat.search(doc[max(start_pos-self.inclusion_offset,0):start_pos]):      
                        found_inc = True
            if found_inc:
                res.append(p.group())
                      
        #Filter to only unique entities in the extraction list 
        res_uniq = list(set(res))    
        
        if res_uniq:
            year, month, day, hour, minute, second = self.string_to_date_tokens(res_uniq[0])
        else:
            #Assign current time
            year, month, day, hour, minute, second = self.string_to_date_tokens("now")
            
        date = datetime(year=year, month=month, day=day, hour = hour, minute = minute, second = second)
        date += timedelta(days=self.timezone_offset/24)
        parsed_date = str(date.strftime("%d-%b-%Y %H:%M:%S"))
        
        parsed_dict = {self.entity_name:[parsed_date]}
        return parsed_dict
    
#Script Tester
def main(argv):
    line = argv[0]
    extractor = CreateDateExtractor(timezone_offset = 0)
    res = extractor.get_matches(line)
    print(res)

if __name__== "__main__":   
   
    #sample = r"""please extract DM14O2186144;        1;1 hi please"""
    sample = "Ticket_Create_Date:2017-09-05-04-57-22"
    
    doc = {"create_date":sample}      
    
    main([doc])
    