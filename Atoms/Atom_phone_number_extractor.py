"""
EXTRACT A 10 DIGIT PHONE NUMBERS FROM TEXT

Returnes a list of unique telephone numbers (TNs) from the found in the text.
In case where no TNs were extracted, an empty list is returned.

Parameters:
    1. entity_name -> name of the entity to be parsed.
    2. exclusion_offset -> number of characters to be ignored after an appereance of an exclusion_list item.
    3. exclusion_list -> textual items that precedes characters that should be ignored while searching. 
    4. inclusion_offset -> number of characters to be included after an appereance of an inclusion_list item.
    5. inclusion_list -> textual items that precedes characters that should be searched for. 
    6. first_digit -> enforce a first digit of the TN.
    7. added_digits -> The default digits for MSISDN are 10, this parameter enables adding digits.
    8. indicator -> True if only a True/False indication of an TN existence in the doc should be returned, False if the actual entity is to be returned.
    
"""

import re

class PhoneNumberExtractor:
    def __init__(self,
                 entity_name = 'MSISDN',
                 exclusion_offset=60,
                 exclusion_list = [],
                 inclusion_offset = 40,
                 inclusion_list = [],
                 first_digit = None,
                 added_digits = 0,
                 indicator = False):
        self.entity_name = entity_name
        self.added_digits = added_digits
        self.phone_re = r"""(^|\D)(0?\d{3})-?(\d{3})-?(\d{1})-?(\d{3})-?(\d{,"""+str(self.added_digits)+"""})?(?=\D|$)""" 
        if first_digit: self.phone_re=r"""\D(0?"""+str(first_digit)+"""\d{2})-?(\d{3})-?(\d{1})-?(\d{3})-?(\d{,"""+str(self.added_digits)+"""})?(?=\D|$)""" 
        self.phone_pattern = re.compile(self.phone_re,
                                        re.VERBOSE|re.MULTILINE|re.IGNORECASE)
                                        
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
        doc = re.sub("~|\*|%","",doc)
        res = []
        for p in self.phone_pattern.finditer(doc):
            found_exc = False
            found_inc = False
            start_pos, end_pos = p.span()
            
            #Seacrh through all exclusion list items and tag True if found in at least one of them
            for exc_pat in self.exclusion_pats:
                #Look after the exclusion token 
                if self.exclusion_offset>=0:
                    #print(doc[max(start_pos-self.exclusion_offset,0):start_pos])
                    if exc_pat.search(doc[max(start_pos-self.exclusion_offset,0):start_pos]):      
                        found_exc = True
                #Look before the exclusion token
                else:
                    #print(doc[end_pos:min(end_pos-self.exclusion_offset,len(doc))])
                    if exc_pat.search(doc[end_pos:min(end_pos-self.exclusion_offset,len(doc))]):      
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
                phone_number = re.sub("[^0-9]", "",p.group())
                res.append(phone_number)
            
        #Filter to only unique entities in the extraction list 
        res_uniq = list(set(res))
        #"Cleans" the phone number formats
        res_uniq = [s.replace('-',"") for s in res_uniq]      
        
        if self.indicator:  
            dict = {self.entity_name: len(res_uniq)>0}
            return dict
            
        dict = {self.entity_name: res_uniq}
        return dict
    
#P2P_FLOW
'''def main(argv):
    line = argv[0]
    extractor = PhoneNumberExtractor(
                                    entity_name = 'Mobile_number'
                                    ,inclusion_list=["party account number", "post to pre"]
                                    ,inclusion_offset=80
                                    #,exclusion_list=[""]
                                    #,exclusion_offset=-40
                                    #exclusion_list = ["requestor phone", "contact phone", "requestor contact"]
                                    #added_digits = 3
                                    #,first_digit = 6
                                    #,inclusion_list=["Yaniv"]
                                    #,indicator = True
                                    )                                     
    res = extractor.get_matches(line)
    print(res)'''

#Dedupe failure
def main(argv):
    line = argv[0]
    extractor = PhoneNumberExtractor(
                                    entity_name = 'Mobile_number'
                                    ,inclusion_list=["Dedupe positive numbers "]
                                    ,inclusion_offset=80
                                    #,exclusion_list=[""]
                                    #,exclusion_offset=-40
                                    #exclusion_list = ["requestor phone", "contact phone", "requestor contact"]
                                    #added_digits = 3
                                    #,first_digit = 6
                                    #,inclusion_list=["Yaniv"]
                                    #,indicator = True
                                    )
    res = extractor.get_matches(line)
    print(res)

if __name__== "__main__":

        #P2P_FLOW
#    sample = r"""post to pre request unable to do in ward 9845948424"""    #INC000002397915
#    sample = r"""POST TO PRE ISSUE 9007102356"""                          #INC000002405494
#    sample =r"""9004251442   POST TO PRE pending"""                       #INC000002416232  // need to check this
#    sample =r"""Pls generate party account number 9937056072 D380035743 Error Code : FAILURE errorMessage : The invoked Method addAccount_NT has Thrown an Exception severity:"""   #INC000002185099
#    sample = r"""KK|post to pre|9964554048|post to pre migration issue"""   #INC000002678647

        # Dedupe failure
    sample = r"""Dedupe positive numbers 6900547151 but when i check the "View details" in the iDOC portal no details not found"""
    doc = {"text":sample}
    
    main([doc])
