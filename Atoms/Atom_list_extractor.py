"""
EXTRACT A PREDEFINED LIST OF ENTITIES FROM TEXT

Returnes a list of unique values from the predefined list found in the text.
In case where no etitites were extracted, an empty list is returned.

Parameters:
    1. entity_name -> name of the entity to be parsed.
    2. extraction_list -> textual items that are to be searched in the text.
    3. exclusion_offset -> number of characters to be ignored after an appereance of an exclusion_list item.
    4. exclusion_list -> textual items that precedes characters that should be ignored while searching. 
    5. inclusion_offset -> number of characters to be included after an appereance of an inclusion_list item.
    6. exclusion_list -> textual items that precedes characters that should be searched for. 
    7. indicator -> True if only a True/False indication of an entity existence in the doc should be returned, False if the actual entity is to be returned.
    
"""
import re

class ListExtractor:
    def __init__(self,
                 entity_name = 'List',
                 extraction_list = [],
                 exclusion_offset=40,
                 exclusion_list = [],
                 inclusion_offset = 40,
                 inclusion_list = [],
                 indicator = False):
        
        # Devises a regular expression out of the list and compiles it
        search_regex = ""
        for entity in extraction_list: search_regex+=r"""\b"""+str(entity)+r"""\b|"""
        if(search_regex): search_regex=search_regex[:-1]
        self.search_pattern = re.compile(search_regex,
                                        re.VERBOSE|re.MULTILINE|re.IGNORECASE)
                                        
        self.entity_name = entity_name
        self.exclusion_offset=exclusion_offset
        self.exclusion_list=exclusion_list
        self.inclusion_offset=inclusion_offset
        self.inclusion_list=inclusion_list
        self.indicator=indicator
        
        self.exclusion_pats = []
        for exc in self.exclusion_list:
            self.exclusion_pats.append(re.compile(exc, re.IGNORECASE))
        self.inclusion_pats = []
        for exc in self.inclusion_list:
            self.inclusion_pats.append(re.compile(exc, re.IGNORECASE))

    def get_matches(self, doc):
        '''
        Input: doc - string containing description text
        Returns: list of strings, each one is a valid phone number
        '''
        doc = doc["text"]        
        res = []
    
        for p in self.search_pattern.finditer(doc):
            
            found_exc = False
            found_inc = False
            start_pos, end_pos = p.span()
            
            #Seacrh through all exclusion list items and tag True if found in at least one of them
            for exc_pat in self.exclusion_pats:
                if exc_pat.search(doc[max(start_pos-self.exclusion_offset,0):start_pos]):
                    found_exc = True
                    
            #Seacrh through all inclusion list items and tag True if found in at least one of them
            if not self.inclusion_list:
                found_inc = True    
            else:
                for inc_pat in self.inclusion_pats:
                    if inc_pat.search(doc[max(start_pos-self.inclusion_offset,0):start_pos]):      
                        found_inc = True
            
            #If not found in any of the exclusion list items and found in the inclusion list items than append to extraction list
            if (not found_exc) and found_inc:
                res.append(p.group())
            
        
        #Filter to only unique entities in the extraction list 
        res_uniq = list(set(res))
        
        if self.indicator: 
            dict = {self.entity_name:len(res_uniq)>0}
            return dict
        dict = {self.entity_name:res_uniq}
        return dict
    
#Script Tester
def main(argv):
    line = argv[0]
    extractor = ListExtractor(extraction_list = ["ABGB","DTH","Mobility","Telemedia"],
                              #exclusion_list = ["requestor phone", "contact phone", "requestor contact"],
                              inclusion_list=["LOB"]
                              #,indicator = True
                              )                                     
    res = extractor.get_matches(line)
    print(res)

if __name__== "__main__":
    sample="Hi, the numbers I want to extract: 912-3456-789, 812-3456785 and this is voice the contact phone 9876543210. LOB TELEMEDIA APPLICATION ICRM ISSUE unable to resolve SR 90532138 IN ICRM PL CLOSE FROM YOUR END TYPE ICRM FAULT REPAIR SR 90532138"
    doc = {"text":sample}      
    
    main([doc])