"""
EXTRACT A PREDEFINED PATTERN FROM TEXT

Returnes a list of unique values that follows the passed regex pattern and found in the text.
In case where no etitites were extracted, an empty list is returned.

Parameters:
    1. entity_name -> name of the entity to be parsed.
    2. definite_extraction_regex -> regular expression pattern to be searched in the text, for full numbers to numbers
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
import string

class FromNumberToNumber:
    def __init__(self,
                 #entity_name_1 = 'From_Number',
                 #entity_name_2 = 'To_Number',
                 entity_name = 'From_Number_To_Number',
                 extraction_regex = "((?<=\D)|(?<=\b)|(?<=^))0\d{3}-\d{7}(?=\D)\s*\n*to\s*\n*0\d{3}-\d{7}(?=\D|$)|(((?<=\D)|(?<=\b)|(?<=^))0?\d{2,}\s*\n*\d*\s*\n*\d*(?=\D)\s*\n*to\s*\n*0?\d{2,}\s*\n*\d*\s*\n*\d*(?=(\D|$)))|(((?<=\D)|(?<=\b)|(?<=^))0?\d{2,}\s*\n*\d*\s*\n*\d*(?=\D)\s*\n*-\s*\n*0?\d{2,}\s*\n*\d*\s*\n*\d*(?=(\D|$)))|(((?<=\D)|(?<=\b)|(?<=^))0?\d{2}\s*\n*\d{4}\s*\n*\d{4}(?=(\D|$)))",
                 definite_to_extraction_regex = "((?<=\D)|(?<=\b)|(?<=^))0?\d{2}\s*\n*\d{4}\s*\n*\d{4}(?=\D)\s*\n*(to|-)\s*\n*0?\d{2}\s*\n*\d{4}\s*\n*\d{4}(?=(\D|$))|((?<=\D)|(?<=\b)|(?<=^))0\d{3}(?:-)\d{7}(?=\D)\s*\n*to\s*\n*0\d{3}(?:-)\d{7}(?=\D|$)",
                 partial_extraction_regex = "",
                 just_one_extraction_regex = "((?<=\D)|(?<=^))\d{10,11}(?=\D|$)|((?<=\D)|(?<=^))0\d{3}-\d{7}(?=\D|$)",
                 first_extraction_regex = "",
                 second_extraction_regex = "",
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
                 replace_char = ["",""]
                 ):
        
        
        
        #self.entity_name_1 = entity_name_1
        #self.entity_name_2 = entity_name_2
        self.entity_name = entity_name
        
        #print("extraction_regex = ",extraction_regex)
        
        self.extraction_regex = extraction_regex
        self.search_pattern = re.compile(self.extraction_regex,
                                        re.MULTILINE|re.IGNORECASE)
        #print("search_pattern = ",self.search_pattern)
        self.definite_to_extraction_regex = definite_to_extraction_regex
        self.definite_to_search_pattern = re.compile(self.definite_to_extraction_regex,
                                        re.MULTILINE|re.IGNORECASE)    
        
        self.partial_extraction_regex = partial_extraction_regex
        self.partial_search_pattern = re.compile(self.partial_extraction_regex,
                                        re.MULTILINE|re.IGNORECASE)  
        
        self.just_one_extraction_regex = just_one_extraction_regex
        self.just_one_search_pattern = re.compile(self.just_one_extraction_regex,
                                        re.MULTILINE|re.IGNORECASE)  
        
        
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
        
        '''        
        try:        
            if self.integer_indicator: 
                self.default_value = [int(eval(default_value))]
            else:
                self.default_value = [eval(default_value)] 
        except:
            self.default_value = []
        '''
        
    def create_dict_from_two_lists(self,From_Number_List,To_Number_List,length_list):
        '''
        Input: two lists: From_Number,To_Number,length of the lists
        Returns: one list of [From_Number_List1-To_Number_List1, From_Number_List2-To_Number_List2, From_Number_List3-To_Number_List3,...]
        '''
        List_to_Return = []
        #print("From_Number_List = ",From_Number_List)
        #print("To_Number_List = ",To_Number_List)
        #print("length_list = ",length_list)
        #print("len(From_Number_List) = ",len(From_Number_List))
        #print("len(To_Number_List) = ",len(To_Number_List))
        if not len(From_Number_List)==len(To_Number_List):
            dict = {self.entity_name:List_to_Return}            
            return dict
        
        for index,number in enumerate(From_Number_List):
            #print("From_Number_List[index]=",From_Number_List[index])
            #print("(To_Number_List[index]).strip()=",type((To_Number_List[index]).strip()))
            #print("int(To_Number_List[index]).strip()=",int((To_Number_List[index]).strip()))
            #List_to_Return[index] = str((From_Number_List[index]).strip()+" - "+(To_Number_List[index]).strip())
            from_num_add = str(int((From_Number_List[index]).strip())).zfill(length_list[index])
            to_num_add = str(int((To_Number_List[index]).strip())).zfill(length_list[index])
            List_to_Return.append(str(from_num_add+" - "+to_num_add))
            #print("List_to_Return = ",List_to_Return)
        
        return List_to_Return
    
    def is_in_list(self,number_to_check,From_numbers,To_numbers):
        '''
        Input: number_to_check - string containing a number, list of From_numbers and list of To_numbers
        Returns: True if the number is already in one of the lists, False if it isn't
        '''
        #print("number_to_check = ",number_to_check,type(number_to_check))
        #print("From_numbers = ",From_numbers)
        #print("To_numbers = ",To_numbers)
        if int(number_to_check) in [int(i) for i in From_numbers]:
            #print("num in from_list",number_to_check)
            return True
    
        if int(number_to_check) in [int(i) for i in To_numbers]:
            #print("num in to_list",number_to_check)
            return True
        #print("num not in lists")
        return False
        
        
    def get_matches(self, doc):
        '''
        Input: doc - string containing description text
        Returns: list of strings, each one is a valid phone number
        '''
        doc = doc["text"]        
        res = []
        From_Number = []
        To_Number = []
        default_value = []
        length_list = []
        found_in_res = False
        
        regex_first_extraction = "((?<=\D)|(?<=\b)|(?<=^))0?\d{9,10}(?=\D)\s*\n*(?=(to|-))|((?<=\D)|(?<=\b)|(?<=^))0\d{3}-\d{7}(?=\D)\s*\n*(?=to)"
        pattern_first_extraction = re.compile(regex_first_extraction,
                            re.MULTILINE|re.IGNORECASE)
        regex_second_extraction = "((?<=to)|(?<=-))\s*\n*0?\d{9,10}(?=(\D|$))|(?<=to)\s*\n*0\d{3}-\d{7}(?=(\D|$))"
        pattern_second_extraction = re.compile(regex_second_extraction,
                            re.MULTILINE|re.IGNORECASE)
        
        partial_to_search_regex = "(((?<=\D)|(?<=\b)|(?<=^))0?\d{2,8}\s*\n*to\s*\n*0?\d{9,10}(?=(\D|$|\n)))|(((?<=\D)|(?<=\b)|(?<=^))0?\d{2,8}\s*\n*-\s*\n*0?\d{9,10}(?=(\D|$|\n)))|(((?<=\D)|(?<=\b)|(?<=^))0?\d{9,10}\s*\n*to\s*\n*0?\d{2,8}(?=(\D|$|\n)))|(((?<=\D)|(?<=\b)|(?<=^))0?\d{9,10}\s*\n*-\s*\n*0?\d{2,8}(?=(\D|$|\n)))"
        pattern_partial_to_search = re.compile(partial_to_search_regex,
                            re.MULTILINE|re.IGNORECASE)
        
        partial_first_in_partial_regex = "((?<=\D)|(?<=\b)|(?<=^))0?\d{2,10}\s*\n*(?=to)|((?<=\D)|(?<=\b)|(?<=^))0?\d{2,10}\s*\n*(?=-)"
        pattern_first_in_partial_extraction = re.compile(partial_first_in_partial_regex,
                            re.MULTILINE|re.IGNORECASE)
        
        partial_second_in_partial_regex = "(?<=to)\s*\n*0?\d{2,10}(?=(\D|$|\n))|(?<=-)\s*\n*0?\d{2,10}(?=(\D|$|\n))"
        pattern_second_in_partial_extraction = re.compile(partial_second_in_partial_regex,
                            re.MULTILINE|re.IGNORECASE)
        '''
        try:        
            if self.integer_indicator: 
                default_value = [int(eval(self.default_value))]
            else:
                default_value = [eval(self.default_value)] 
        except:
           default_value = []
           '''
        for p in self.search_pattern.finditer(doc):
            #print("p = ",p)
            found_exc = False
            found_inc = False
            start_pos, end_pos = p.span()
            this_expr = False
            
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
            #print("found_inc = ",found_inc)
            
            #If not found in any of the exclusion list items and found in the inclusion list items than append to extraction list
            if (not found_exc) and found_inc:
                res.append(re.sub(self.replace_char[0],self.replace_char[1],re.sub(self.remove_char,"",p.group())))
                #print("res = ",res)
                
                for p0 in self.definite_to_search_pattern.finditer(p.group()):
                    #print("p0.group = ",p0.group())
                    first_num = re.search(pattern_first_extraction, p0.group()).group().replace("-","")
                    second_num = re.search(pattern_second_extraction, p0.group()).group().replace("-","")
                    #print("first_num,second_num = ",first_num,",",second_num)
                    first_as_str = str(int(first_num))
                    len_first = (len(first_num.strip()))
                    len_sec = (len(second_num.strip()))
                    #print("len_first,len_sec = ",len_first,",",len_sec)
                    #Equal lengths of from and to, this is a definite expression of 10 or 11 digits
                    if (len_first == len_sec) and (len_first==10) or (len_first==11):
                        #print("equal")
                        
                        if not self.is_in_list(str(first_num.strip().zfill(len_first)),From_Number,To_Number):
                            From_Number.append(str(first_num.strip().zfill(len_first)))
                            #print("From_Number after adding = ",From_Number) 
                            length_list.append(len_first)
                            found_in_res = True
                            this_expr = True
                        if not self.is_in_list(str(second_num.strip().zfill(len_sec)),From_Number,To_Number):
                            To_Number.append(str(second_num.strip().zfill(len_sec)))
                            #print("To_Number after adding = ",To_Number) 
                            
                #elif - this is a partial expression (pp - p partial)
                if not this_expr:
                    #print("partial expression")
                    for pp in pattern_partial_to_search.finditer(p.group()):
                        #print("Partial Pattern")
                        first_in_partial = re.search(pattern_first_in_partial_extraction, pp.group()).group().replace("-","")
                        second_in_partial = re.search(pattern_second_in_partial_extraction, pp.group()).group().replace("-","")
                        
    
                        len_first = (len(first_in_partial.strip()))
                        len_sec = (len(second_in_partial.strip()))
                        #print("len_first,len_sec = ",len_first,",",len_sec)
                        
                        first_as_str = str(int(first_in_partial)).zfill(len_first)
                        second_as_str = str(int(second_in_partial)).zfill(len_sec)
                        
                        #first num > 9 meaning that the first one is the full one
                        if (not found_in_res) and ((len_first==10) or (len_first==11)):
                            #print("the first one is the full one")
                            sec_partial_as_str = str(int(second_in_partial))
                            sec_full_as_str = ""
                            #print("sec_full_as_str = ",sec_full_as_str)
                            for i in range(0,len_first-1):
                                if (i<len_first-len_sec):
                                    sec_full_as_str = sec_full_as_str + first_as_str[i]
                                    #print("first_as_str[i],i, sec_full_as_str",first_as_str[i],",",i,",",sec_full_as_str)
                            sec_full_as_str = sec_full_as_str + sec_partial_as_str
                            found_in_res = True
                            #print("sec_full_as_str",sec_full_as_str)
                            second_as_str = sec_full_as_str
                          
                        #first num < 10 meaning that the second is the full one
                        else:
                            #print("the second one is the full one")
                            first_partial_as_str = str(int(first_in_partial))
                            first_full_as_str = ""
                            
                            for i in range(0,len_sec-1):
                                #print("i = ",i)
                                if (i<len_sec-len_first):
                                    first_full_as_str = first_full_as_str + second_as_str[i]
                            first_full_as_str = first_full_as_str + first_partial_as_str
                            found_in_res = True
                            #print("first_full_as_str",first_full_as_str)
                            first_as_str = first_full_as_str
                        
                        #for partial sets, after filled, add to the From-To lists
                        #print("first_as_str, sec_full_as_str",first_as_str.strip().zfill(len_first),",",second_as_str.strip().zfill(len_sec))
                        #print("From_Number = ",From_Number)
                        #print("To_Number = ",To_Number) 
                        if not self.is_in_list(first_as_str.strip().zfill(len_first),From_Number,To_Number):
                            From_Number.append(str(first_as_str.strip().zfill(len_first)))
                            #print("From_Number after adding 2= ",From_Number) 
                            length_list.append(max(len_first,len_sec))
                            found_in_res = True
                        if not self.is_in_list(second_as_str.strip().zfill(len_sec),From_Number,To_Number):
                            To_Number.append(str(second_as_str.strip().zfill(len_sec)))
                            #print("To_Number after adding 2= ",To_Number) 
                    #print("p1.group = ",p1.group())
                    #print("length_list = ",length_list)
                    
                    #to_num_add = (re.search(pattern_to_in_to, p1.group()).group()).replace('-','')
                    
                    #print("To_Number = ",To_Number) 
                    #start_pos_p1, end_pos_p1 = p1.span()
                    #text_after_definite = p1.group()
                    #text_after_definite = text_after_definite[0:start_pos_p1]+text_after_definite[end_pos_p1:]
                    #print("text_after_definite = ",text_after_definite[end_pos_p1:]) 
            #print("From_Number 3 = ",From_Number)
            #print("To_Number 3 = ",To_Number) 
            #print("found_in_res = ",found_in_res)
            
            
            if (not found_in_res) or (not From_Number):
                #print("here")
                for p1 in self.just_one_search_pattern.finditer(p.group()):
                    #print("p1 = ",p1) 
                    num = p1.group().strip().replace('-','')
                    #print("p2.group = ",type(p2.group()))
                    if self.is_in_list(str(int(num)),From_Number,To_Number):
                        #print("is in list already:",p2.group())
                        continue
                    length_list.append(len(num))
                    From_Number.append(str(num))
                    To_Number.append(str(num))
                    #print("To_Number = ",To_Number)
                
                '''
                if self.integer_indicator:
                    int_value = int(re.sub("[^0-9]", "",p.group()))
                    if len(str(int_value))<=self.length_limit: res.append(int_value)
                else:
                    #res.append(p.group().replace(self.remove_char,""))
                    if self.upper_case: 
                        res.append(re.sub(self.replace_char[0],self.replace_char[1],re.sub(self.remove_char,"",p.group().upper())))
                    else:
                        res.append(re.sub(self.replace_char[0],self.replace_char[1],re.sub(self.remove_char,"",p.group())))
                '''
                
        #Filter to only unique entities in the extraction list 
        #print("res = ",res) 
        #res_uniq = list(set(res))
        #print("res_uniq = ",res_uniq)
        #print("From_Number_final = ",From_Number)
        #print("To_Number_final = ",To_Number)
        
        #Return Default value (empty list) if no number or more than one range when we need only one
        if (len(From_Number)<1) or (self.unique_indicator and len(From_Number)>1):
                dict = {self.entity_name:default_value}    
                #print("dict0") 
                return dict
            
        #only one number in the ticket
        if (len(From_Number)==1):
            #print("From_Number1 = ",From_Number)
            #print("To_Number1 = ",To_Number)
            dict = {self.entity_name:self.create_dict_from_two_lists(From_Number,To_Number,length_list)}
            #print("dict1") 
            return dict
       
        #True if only a True/False indication of an entity existence in the doc should be returned, False if the actual entity is to be returned
        if self.indicator: 
            dict = {self.entity_name:len(From_Number)>0}  
            #print("dict2") 
            return dict
        
        dict = {self.entity_name:self.create_dict_from_two_lists(From_Number,To_Number,length_list)}
        
        #From_Number = {self.entity_name_1:from_num}
        #To_Number = {self.entity_name_2:to_num}
        #print("dict3") 
        return dict
    

#Script Tester
def main(argv):
    line = argv[0]
    extractor = FromNumberToNumber( #entity_name_1 = 'From_Number',
                                    #entity_name_2 = 'To_Number',
                                    entity_name = 'From_Number_To_Number',
                                    #inclusion_list=["soc_cd","SOC_CD"],
                                    #,indicator = True
                                    #integer_indicator = True,
                                    #length_limit = 2,
                                    #unique_indicator = True,
                                    #default_value = "datetime.datetime.now().strftime('%d')"
                                    #remove_char = " ",
                                    #upper_case = True,
                                    #replace_char = [":"," "]
                                    )                                     
    From_Number_To_Number = extractor.get_matches(line)
    print(From_Number_To_Number)

if __name__== "__main__":
    #sample = "02042961000 to 02042961099"
    #sample = "Need to be release of PRI serise 05224261800 to 05224261849"
    #sample = "Hi Team Please release below PRI series in NMS 02249093500 to \n\n02249093699 (200 nos) 02240083500 to 02240083699 (200 nos) 02240483500 to \n\n02240483699 (200 nos)"
    #sample = "NMS : Nubmer release form Aging to available did range : 04045453550 \n\nto 04045453599\n\n04045453599" #- uneven number of numbers
    #sample = "04045453550 to 04045453599 MSU Change : 4045453540 to 4045453589"
    #sample = "04045111111 to \n\n\n  04045222222" #-
    #sample = "PRI series release urgent - 07940211000 to 07940211099"
    #sample = "the range is 01149292100-01149292199"
    #sample = "release nms 0124-4601776 to 0124-4601778"
    
    #sample = "01149292100-99" #(INC000002072777) the range is 01149292100-01149292199 
    #sample = "01244785860 to 4785899" # (INC000002072778):the range is 01244785860 to 01244785899 (same first 4 digits to be completed automatically)
    #sample = "Pls PRI series release 07292426200 to 249"
    #sample = "123 to 04444444444"
    #sample = "123 to 1444444445"
    #sample = "01244785860 to 4785899, 123 to 04444444444"
    
    #sample = "release nms 0124-4601777" #{'From_Number_To_Number': ['0124-4601777']}
    #sample = "Hardware/ Software related support please relese number from NMS\n\n8822222220\n\n8822222220"
    #sample = "please relese number from NMS 7042607800" # (INC000002129883): Send same number in both parameters
    #sample = "Number Is To Be Release In NMS 7880979768" # (INC000002073503) what should be extracted? [Anirudha – 7880979768 is to be extracted in both parameters]
    
    #sample = "Number IS To be Release IN NMS 7390090621"
    #sample = "Hi Team\nPls release the number in NMS \n7081006123\n9081006116\n\n8081006125\n6081006118"
    sample = "01204130808\n01204165050\n01294144600\n01204135589\n01204130808\n01204165050\n01294144600\n01204135589"
    #sample = "01204130808\n01204130808"
    
    #sample = ""
    #sample = ""
    doc = {"text":sample}      
    
    main([doc])
    