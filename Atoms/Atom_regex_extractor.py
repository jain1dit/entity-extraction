"""
EXTRACT A PREDEFINED PATTERN FROM TEXT

Returnes a list of unique values that follows the passed regex pattern and found in the text.
In case where no etitites were extracted, an empty list is returned.

Parameters:
    1. entity_name -> name of the entity to be parsed.
    2. extraction_regex -> regular expression pattern to be searched in the text.
    3. exclusion_offset -> number of characters to be ignored after an appereance of an exclusion_list item.
    4. exclusion_list -> textual items that precedes characters that should be ignored while searching. 
    5. inclusion_offset -> number of characters to be included after an appereance of an inclusion_list item.
    6. exclusion_list -> textual items that precedes characters that should be searched for. 
    7. indicator -> True if only a True/False indication of an entity existence in the doc should be returned, False if the actual entity is to be returned.
    8. integer_indicator -> True if only integer number to be extracted.
    9. unique_indicator -> if True and more than 1 entity found returns an empty list.
    10. length_limit -> maximum number of characters in each entity
    11. default_value -> default value - PYTHON COMMAND - when no entities are found or more than 1 is found where unique_indicator is set to true
    12. remove_char -> ONE charcter to be removed from the extracted entity
    13. upper_case -> True if all charters should be in upper case
    14. replace_char -> list with 2 entries - char to be replaced and a replaceable char
    
"""

import re
import datetime

class RegexExtractor:
    def __init__(self,
                 entity_name = 'Regex',
                 extraction_regex = [],
                 exclusion_offset=40,
                 exclusion_list = [],
                 inclusion_offset = 40,
                 inclusion_list = [],
                 indicator = False,
                 integer_indicator = False,
                 unique_indicator = False,
                 length_limit = 1000,
                 default_value = [],
                 remove_char = "",
                 upper_case = False,
                 replace_char = ["",""],
                 multiline = True
                 ):
        
        self.entity_name = entity_name        
        self.extraction_regex = extraction_regex
        self.search_pattern = re.compile(self.extraction_regex,
                                        re.VERBOSE|re.MULTILINE|re.IGNORECASE)
                                        
        self.exclusion_offset=exclusion_offset
        self.exclusion_list=exclusion_list
        self.inclusion_offset=inclusion_offset
        self.inclusion_list=inclusion_list
        self.indicator=indicator
        
        self.integer_indicator=integer_indicator
        self.unique_indicator=unique_indicator
        self.length_limit=length_limit
        self.remove_char = remove_char
        self.upper_case = upper_case
        self.replace_char = replace_char
        
        self.exclusion_pats = []
        for exc in self.exclusion_list:
            self.exclusion_pats.append(re.compile(exc, re.IGNORECASE))
        self.inclusion_pats = []
        for exc in self.inclusion_list:
            self.inclusion_pats.append(re.compile(exc, re.IGNORECASE))
        
        self.default_value = default_value
        self.multiline = multiline
        
        '''        
        try:        
            if self.integer_indicator: 
                self.default_value = [int(eval(default_value))]
            else:
                self.default_value = [eval(default_value)] 
        except:
            self.default_value = []
        '''

    def get_matches(self, doc):
        '''
        Input: doc - string containing description text
        Returns: list of strings, each one is a valid phone number
        '''
        doc = doc["text"]        
        res = []
        
        try:        
            if self.integer_indicator: 
                default_value = [int(eval(self.default_value))]
            else:
                default_value = [eval(self.default_value)] 
        except:
            default_value = self.default_value        
        
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
                    search_space = doc[max(start_pos-self.inclusion_offset,0):start_pos]
                    try:
                        if not self.multiline:
                            search_space=search_space[search_space.rfind('\n')+1:] #search only in the line found and not lines before
                    except:
                        pass
                    if inc_pat.search(search_space):      
                        found_inc = True
                    
            #If not found in any of the exclusion list items and found in the inclusion list items than append to extraction list
            if (not found_exc) and found_inc:
                if self.integer_indicator:
                    int_value = int(re.sub("[^0-9]", "",p.group()))
                    if len(str(int_value))<=self.length_limit: res.append(int_value)
                else:
                    #res.append(p.group().replace(self.remove_char,""))
                    if self.upper_case: 
                        res.append(re.sub(self.replace_char[0],self.replace_char[1],re.sub(self.remove_char,"",p.group().upper())))
                    else:
                        res.append(re.sub(self.replace_char[0],self.replace_char[1],re.sub(self.remove_char,"",p.group())))
            
        #Filter to only unique entities in the extraction list 
        res_uniq = list(set(res))
        
        if (len(res_uniq)<1) or (self.unique_indicator and len(res_uniq)>1):
                res_uniq = default_value    
        
        #Return empty list if there's a demand for unique value and more than 1 value parsed        
        #if (self.unique_indicator) and len(res_uniq)>1:
        #    dict = {self.entity_name:[]}
        #    return dict
            
        if self.indicator: 
            dict = {self.entity_name:len(res_uniq)>0}            
            return dict
        
        dict = {self.entity_name:res_uniq}
        return dict
    
#Script Tester
def main(argv):
    line = argv[0]
    extractor = RegexExtractor(
                                    extraction_regex = "((?<=\\D)|(?<=\\b)|(?<=''))[7-9](\\d{9})((?=\\b)|(?=\\s)|(?=\\D))",
                                    #extraction_regex = r"""[A-Z]+(\t|[; ]+)[0-9]+(\t|[; ]+)[\w: ,.()]+(\t|[; ]+)[0-9]+""",
                                    exclusion_list = ["sfo","Ac No"	,"Account no","a c no","ac(?!tivation)"],
                                    #inclusion_list=["Customer id"],
                                    #inclusion_offset=1000,
                                    exclusion_offset=20,
                                    #,indicator = True
                                    integer_indicator = True,
                                    multiline=False
                                    #length_limit = 2,
                                    #unique_indicator = True
                                    #default_value = "datetime.datetime.now().strftime('%d')"
                                    #remove_char = "(\n|\s)",
                                    #upper_case = True,
                                    #replace_char = [",",";"]
                                    )                                     
    res = extractor.get_matches(line)
    print(res)

if __name__== "__main__":
    #sample="Hi, this is the numbers I want to extract: 912-3456-789, 812-3456785 and this is the contact phone 9876543210"
    #sample = "Issue Details: OrderID/ServiceID: customer requested for change of loading schedule from 8th to 17th seeding 18/08/09 19"
    #sample = "App support BE , Advance MRC   is showing Threshold break in TZ 05 .   Kindly check if  failure is valid or not.  Non Linkage :     Advance MRC Time zone File Name 05 Date Success Failure \"Failed % (Threshold Break 1%)\" 4-Apr-17 26,842 0 0.00% 5-Apr-17 29,380 1 0.00% 6-Apr-17 30,498 2 0.01% 7-Apr-17 26,991 1 0.00% Variance Day on Day (Threshold Break 1%) -11% -50%  Thanks & Regards, Uday Pawar"
    #sample = "LTP <9055131553>NON RCPT OF LOAD ; 97535155\r\n\r\nIncoming call\r\nContact Phone: 9175601433\r\n\r\nSeeding date: 17th Notes: Ms. Mary Ann Dela Cruz Felix ci to follow up her LTP500 .\r\n\r\nThe account is was never incollection status with 0 past due amount"
    #sample = "pport ClickIT TicketBAN/Account:PTN:Order Number: DM14-O-32762211 Operation: Complete Order Front End Order #: Dm14-O-32762211"

    sample =r"""Actual DMT#: S8A00433330290, SMC 011015791012"""
    doc = {"text":sample}
    
    main([doc])
    
