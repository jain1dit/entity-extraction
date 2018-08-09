'''
EXTRACT AN EMAIL ADDRESS FROM TEXT

Return a list of unique email addresses found in the text.
In the case where no email addresses are found an empty list is returned.


Parameters:
    1. entity_name -> name of the entity to be parsed
    1. exclusion_offset -> number of characters to be ignored after an appereance of an exclusion_list item.
    2. exclusion_list -> textual items that precedes characters that should be ignored while searching. 
    3. inclusion_offset -> number of characters to be included after an appereance of an inclusion_list item.
    4. inclusion_list -> textual items that precedes characters that should be searched for. 
    5. exclusion_url_list -> if the textual item contains a URL in this list it will be ignored.
    6. inclusion_url_list -> if the textual item contains a URL in this list it will be included, otherwise it will be ignored.
    7. predefined_extensions -> if True onlt emails with predfined extensions will be extracted. see extension_list.
    8. indicator -> True if only a True/False indication of an e-mal address existence in the doc should be returned, False if the actual entity is to be returned.
    
    (\+[0-9]+-)?([0-9]{3}-)([0-9]{3}-)([0-9]{4})
'''
import re

class EmailAddressExtractor:
    def __init__(self, 
                 entity_name = 'e-mail',
                 exclusion_offset=60,
                 exclusion_list=[],
                 inclusion_offset=40,
                 inclusion_list=[],
                 exclusion_url_list=[],
                 inclusion_url_list=[],
                 predfined_extensions = True,
                 indicator=False):
       # ([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)
       #cmil351.WM
       #Connected.DROP
       #(com|net|org|ro) removes errors from unknown formatting of descriptions but will miss other URLs 
       #Increased precision at the cost of missing other emails
       #using \w would collect all emails but will collect other strings that aren't emails
        self.entity_name = entity_name
        self.email_re = r"""([\w\.+-])+@(([\w-])+(\.))+\w+"""
        self.email_pattern = re.compile(self.email_re, re.VERBOSE | re.MULTILINE)
        self.exclusion_offset = exclusion_offset
        self.exclusion_list = exclusion_list
        self.inclusion_offset = inclusion_offset
        self.inclusion_list = inclusion_list
        self.indicator = indicator
        self.predefined_extensions = predfined_extensions
        self.extension_list = ['\.com','\.org','\.net','\.ro\Z']

        self.exclusion_pats = []
        for exc in self.exclusion_list:
            self.exclusion_pats.append(re.compile(exc, re.IGNORECASE))

        self.inclusion_pats = []
        for inc in self.inclusion_list:
            self.inclusion_pats.append(re.compile(inc, re.IGNORECASE))
        
        #add urls to exclude from our search
        self.exclusion_urls = []
        for url in exclusion_url_list:
            self.exclusion_urls.append(re.compile(url, re.IGNORECASE))
        
        #add urls to include from our search
        self.inclusion_urls = []
        for url in inclusion_url_list:
            self.inclusion_urls.append(re.compile(url, re.IGNORECASE))
            
    def get_matches(self, doc):
        '''
        Input: doc - string containing description text
        Returns: list of strings, each one is a valid email address
        '''
        doc = doc["text"]        
        res = []
        
        for p in self.email_pattern.finditer(doc):
            
            found_exc = False
            found_inc = False
            start_pos, end_pos = p.span()
            
            
            for exc_pat in self.exclusion_pats:
                if exc_pat.search(doc[max(start_pos-self.exclusion_offset,0):start_pos]):
                    found_exc = True
            
            if not self.inclusion_list:
                found_inc = True
            else:
                for inc_pat in self.inclusion_pats:
                    if inc_pat.search(doc[max(start_pos-self.inclusion_offset,0):start_pos]):
                        found_inc = True
            
            #ignore the email address if we find a URL from the exclusion list            
            for url in self.exclusion_urls:
                if url.search(doc[start_pos:end_pos]):
                    found_exc = True
            
            #if the inclusion list is non-empty only items with a URL in the inclusion list will be returned
            for url in self.inclusion_urls:
                if url.search(doc[start_pos:end_pos]):
                    found_inc = True
                else:
                    found_inc = False

            #(\+[0-9]+-)?([0-9]{3}-)([0-9]{3}-)([0-9]{4})
            if (not found_exc) and found_inc:
                s = p.group()
                
                if self.predefined_extensions:
                    for i in range(len(self.extension_list)):
                        item = re.search(self.extension_list[i]+'(\w)*', s)
                        if item:
                            #clip to ensure it ends after url extension
                            start, end = item.span()
                            s = s[0:start+len(self.extension_list[i])-1]
    
                            item = re.search('(\+[0-9]+-)?([0-9]{3}-)([0-9]{3}-)([0-9]{4})', s)
                            if item:
                                start, end = item.span()
                                s = s[end:len(s)]
    
                            res.append(s)
                else:
                    res.append(s)

        res_uniq = list(set(res))
        
        if self.indicator:
            dict = {self.entity_name:len(res_uniq) > 0}
            return dict
        
        dict = {self.entity_name:res_uniq}
        return dict

def main(argv):
    line = argv[0]
    
    extractor = EmailAddressExtractor(
                                    #indicator = True
                                    )
    
    res = extractor.get_matches(line)
    
    print(res)
    
if __name__ == "__main__":
    sample = "NiCk@amdocs.com AMDOCS is an email address nick@ amdocs.com is not, but 123@123.123 is"
    doc = {"text":sample}      
    
    main([doc])
        