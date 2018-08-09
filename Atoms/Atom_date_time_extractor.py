"""
EXTRACT DATE-TIME ELEMENTS FROM A TEXT

Returnes a list of unique dates in the format of EPOCH.
In case where no etitites were extracted, an empty list is returned.
Time Zone definition is supported

Utilizes parsedatetime package (not icluded in Anaconda)
Basic Format - American (MM/DD/YY)

The parser searches for date/time entities line by line (seperated by a dot or a line break) in a document.
In a case of multiple date-time objects in a line, the last one would be extrcated.

Parameters:
    1. entity_name -> name of the entity to be parsed
    2. time_zone -> Name of timezone. see full list at <pytz.all_timezones>. default - 'America/Chicago'
    4. exclusion_offset -> number of characters to be ignored after an appereance of an exclusion_list item.
    5. exclusion_list -> textual items that precedes characters that should be ignored while searching. 
    6. inclusion_offset -> number of characters to be included after an appereance of an inclusion_list item.
    7. exclusion_list -> textual items that precedes characters that should be searched for. 
    8. ignore_linebreak -> True if a line break should not be considered as a new line, False otherwise.
    9. indicator -> True if only a True/False indication of an entity existence in the doc should be returned, False if the actual entity is to be returned.
    10. format_to_extract -> a dictionary for the format of the date extracted
    11. unique_indicator -> if True and more than 1 entity found returns an empty list.
    12. default_value -> default value - PYTHON COMMAND - when no entities are found or more than 1 is found where unique_indicator is set to true
    13. input_format -> expected format of the date to be parsed - "ddyymm" or "mmddyy"
    
Known issues:
    1. 4 digit numbers are ambigious and could be interpeted as time. for example 2100 is interpeted as 21:00 PM. 
       Can't exclude aprioiri, as numbers such as 2015 are correctly interpeted as years after a month. 
    2. In case where words such as "today" or "tomorrow" should not stand for time it should be explicitly mentioned in the exclusion list
    * a date with some character next to the date numbers or word - this is not handled
"""

import re
import parsedatetime
from datetime import datetime, timedelta, timezone, date
import pytz
from pytz import timezone
import time
    
class DateTimeExtractor:
    def __init__(self,
                 entity_name = 'datetime',
                 #entity_name_epoch = 'datetime_epoch',
                 time_zone = 'America/Chicago',
                 exclusion_offset=40, #POSSIBLE ISSUE- en event where the location is less than exclusion_offset char. from the begining of the text
                 exclusion_list = ["remar"],
                 inclusion_offset = 50,
                 inclusion_list = [],
                 ignore_linebreak = False,
                 #indicator = False,
                 format_to_extract = 2,
                 unique_indicator = False,
                 default_value = [],
                 #input_format="mmddyy",
                 multiple_values=True
                ):
        
        self.entity_name = entity_name
        #self.entity_name_epoch = entity_name_epoch
        self.exclusion_offset=exclusion_offset
        self.exclusion_list=exclusion_list
        self.inclusion_offset=inclusion_offset
        self.inclusion_list=inclusion_list
        self.ignore_linebreak=ignore_linebreak
        #self.indicator=indicator
        self.time_zone = time_zone
        self.time_zone = pytz.timezone(self.time_zone)
        self.format_to_extract = format_to_extract
        self.unique_indicator = unique_indicator
        self.default_value = default_value
        #self.input_format = input_format
        self.multiple_values = multiple_values

    def replace_for_ddmmyy(self,document):
        ddmmyy_re = "(?!\D)\d{1,2}\/\d{1,2}\/\d{2,4}(?:(\D|$))"
        ddmmyy_pattern = re.compile(ddmmyy_re)
        for p in ddmmyy_pattern.finditer(document):
            full_date = p.group()
            cou = 0
            for slash in re.compile("\/").finditer(full_date):
                if cou == 0:
                     dd_start, dd_finish = slash.span()
                     dd = full_date[0:dd_finish-1]
                else:
                    mm_start, mm_finish = slash.span()
                    mm = full_date[dd_finish:mm_start]
                    yy=full_date[mm_finish:]
                cou+=1
            if (int(mm)<=12):
                switched_str="".join([mm,"/",dd,"/",yy])
                start, finish = p.span()
                document = document[:start]+switched_str+document[finish:]
            
        return document
    
    def Indonesian_Dict(self,doc):
        #a dictionary from Indonesian months to English months     
        #Make sure the long phrase comes before the short one: djuli before juli
        Months_Dict = {'djan':'jan','januari':'jan','peb':'feb','mrt':'mar','maret':'mar','mei':'may','mai':'may','juni':'jun','juli':'jul','ag':'aug','okt':'oct','nop':'nov','des':'dec'}
        for k,v in Months_Dict.items():
            doc = doc.lower().replace(k, v)
            
        Months_Dict = {'djun':'jun','djul':'jul'}
        for k,v in Months_Dict.items():
            doc = doc.lower().replace(k, v)
        #print(doc)
        
        #Ignore dot as a sentence break when preceded by a month abbreviation
        
        #English Short Upper, English Short Lower
        month_list = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec",
                      "jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
                             
        #Indonesian	Jan./Djan. 	Peb.	Mrt.	Apr.	Mei/Mai	Juni/Djuni	Juli/Djuli	Ag.	Sept.	Okt.	Nop.	Des.    
        for month in month_list:
            doc = re.sub(month+". ",month+" ", doc.rstrip())
        return doc
    
    def get_month_word_from_number(self,month_number):
        #month_number is a string
        #Dict_month_from_num_to_word = {'1':'jan','2':'feb','3':'mar','4':'apr','5':'may','6':'jun','7':'jul','8':'aug','9':'sep','10':'oct','11':'nov','12':'dec'}
        
        #month_number is an int
        Dict_month_from_num_to_word = {1:'jan',2:'feb',3:'mar',4:'apr',5:'may',6:'jun',7:'jul',8:'aug',9:'sep',10:'oct',11:'nov',12:'dec'}
        
        month_word = Dict_month_from_num_to_word[month_number]
        #print("month_word = ",month_word)
        return month_word
    
    def string_to_date_tokens(self, date_string):
        try:        
            year = int(date_string[:4])
            month = int(date_string[5:7])
            day = int(date_string[8:10])
            #hour = int(date_string[11:13])
            #minute = int(date_string[14:16])
            #second = int(date_string[17:19]) 
        except:
            year = int(time.strftime("%Y"))
            month = int(time.strftime("%m"))
            day = int(time.strftime("%d"))
            #hour = int(time.strftime("%H"))
            #minute = int(time.strftime("%M"))
            #second = int(time.strftime("%S")) 
        return year, month, day#, hour, minute, second
    
    def get_date_from_create_date(self,docu):
        #input to run within the Atom: "Ticket_Create_Date:2017-09-05-04-57-22"
        #input to run in evaluate ticket: "create_date":1515428070
        
        docu = docu["create_date"] 
        res=[]
        #print("docu = ",docu)
        
        create_date_regex = "\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}"
        create_date_pattern = re.compile(create_date_regex, re.MULTILINE|re.IGNORECASE)
        
        for p in create_date_pattern.finditer(docu):
            start_pos, end_pos = p.span()
            '''
            found_inc = False
            #Seacrh through all inclusion list items and tag True if found in at least one of them
            if not self.inclusion_list:
                found_inc = True    
            else:
                for inc_pat in self.inclusion_pats:
                    if inc_pat.search(doc[max(start_pos-self.inclusion_offset,0):start_pos]):      
                        found_inc = True
            if found_inc:
            '''
            res.append(p.group())
          
        
        if res:
            year_as_number, month_as_number, day = self.string_to_date_tokens(res[0])
        else:
            return ""
        
        #print("type month = ",type(month))
        month_as_word = self.get_month_word_from_number(month_as_number)
        #print("type(year) = ",type(year))
        return month_as_word,month_as_number,year_as_number
    
    def year_as_4_digits(self, int3):
        #int3 is a string, returns str
        #year handling - making sure that it's 4 digits
        
        digits_in_year = sum(c.isdigit() for c in int3)
        #print("digits_in_year = ",digits_in_year)
        
        if digits_in_year == 4:
            return int3
        elif digits_in_year == 2:
            sum_is = sum([int(int3), int(2000)])
            #print(sum_is)
            return str(sum_is)
        else:
            return ""
    
    def get_matches(self, docu):
        '''
        Input: doc - string containing description text
        Returns: list of strings, each one is a date-time
        '''
        doc = docu["text"]
        #print("docu[create_date] = ",docu["create_date"])
        res = []
        #res_epoch = []
        
        #Format_Dict: 1 = "MMM-DD-YYYY HH:MM"; 2 = "YYYYMMDD"
        Format_Dict = {1:'%b-%d-%Y %H:%M',2:'%b-%d-%Y'}

        #get month and year from create date
        month_from_create_date_as_word,month_from_create_date_as_number,year_as_number_from_create_date = self.get_date_from_create_date(docu)
        
        #Delete charchters that can be interpeted as hours or dates        
        doc = re.sub(#r'(\b\d?\d?\d?[0-9]{3}\b)'
                    r'\b\d{3}\b' #Eliminate 3 digit numbers
                    + r'|\b\d{5,6}\b' #Eliminate 5 or 6 digit numbers
                    + r'|@'
                    #+ r'|-'
                    , r' NUMBER ', doc.rstrip())
        #print("doc1 = ",doc)
        doc = self.Indonesian_Dict(doc)
        #print("doc2 = ",doc)
        doc = doc.replace("-","/")
        #print("doc3 = ",doc)
        #if self.input_format == "ddmmyy":
            #doc = self.replace_for_ddmmyy(doc)
        
        
        #for date in parsed_list:
            #date = date.replace("-","/")
        #print("parsed_list = ",parsed_list)
        
        #Delete text elements after exclusion list items        
        if self.exclusion_list:
            for exclusion_item in self.exclusion_list:
                exclusion_regex = str(r'' + exclusion_item + '.{0,' + str(self.exclusion_offset) + '}')
                doc = re.sub(exclusion_regex, r' EXCLUDED ', doc.rstrip())
        #print("doc6 = ",doc)
        #Parse text elements after inclusion list items    
        #print("self.inclusion_list = ",self.inclusion_list)
        if self.inclusion_list:
            parsed_list = []
            for inclusion_item in self.inclusion_list: 
                search_pattern = re.compile(inclusion_item, re.IGNORECASE)
                for p in search_pattern.finditer(doc):
                    #print("p = ",p)
                    start_pos, end_pos = p.span()
                    #print("adding to parsed_list = ",doc[end_pos:min(end_pos+self.inclusion_offset,len(doc))])
                    parsed_list.append(doc[end_pos:min(end_pos+self.inclusion_offset,len(doc))])       
        else:
            if not self.ignore_linebreak:            
                #doc = doc.replace(".","\n")
                parsed_list = doc.split('\n')
                
            else:
                parsed_list = doc.split('.')
                
        
        #Months_num_Dict = {'/jan/':' jan ','/feb/':' feb ','/mar/':' mar ','/apr/':' apr ','/may/':' may ','/jun/':' jun ','/jul/':' jul ','/aug/':' aug ','/sep/':' sep ','/oct/':' oct ','/nov/':' nov ','/dec/':' dec '}
        #{'jan/':'1/','feb/':'2/','mar/':'3/','apr/':'4/','may/':'5/','jun/':'6/','jul/':'7/','aug/':'8/','sep/':'9/','oct/':'10/','nov/':'11/','dec/':'12/'}
        
        #print("\nparsed_list0 = ",parsed_list)
        #Check if the month in the date is in a word format
        month_as_word = [False] * (len(parsed_list))
        #print("len(parsed_list) = ",len(parsed_list))
        #print("month_as_word1 = ",month_as_word)
        months_list = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
        #for month in months_list:
        for index,date in enumerate(parsed_list, start=0):
            #print("\ndate = ",date)
            
            #month_as_word[index] = date.find(month)
            parsed_list[index] = parsed_list[index].replace("/", " ")
            parsed_list[index] = parsed_list[index].replace("\n", " ")
            parsed_list[index] = parsed_list[index].replace(".", " ")
            parsed_list[index] = parsed_list[index].replace(",", " ")
            
            #print("parsed_list1 = ",parsed_list)
            list_strings_in_date=parsed_list[index].split(' ') 
            #print("list_strings_in_date = ",list_strings_in_date)

            list_ints_in_date = [x for x in list_strings_in_date if x.isnumeric()==True]
            #print("list_ints_in_date = ",list_ints_in_date)
            
            #checks in the first 3 relevant items - is the month a word or not
            count_ints = 0
            for string in list_strings_in_date:
                #print(string)
                if ("jan" in string)or("feb" in string)or("mar" in string)or("apr" in string)or("may" in string)or("jun" in string)or("jul" in string)or("aug" in string)or("sep" in string)or("oct" in string)or("nov" in string)or("dec" in string):
                    month_as_word[index]=True
                    break
                if string.isnumeric()==True:
                    count_ints+=1
                    #print("count_ints = ",count_ints)
                if count_ints == 3:
                    break
   
            #in case the month is in a word format
            #if month in date:
            if (month_as_word[index]==True):
                month=""
                #print("month = ",month)
                for i in range(len(months_list)):
                    #Bug found: the month can be further in the string, such as 'nov' in the word 'lenovo'. 
                    #The fix: only the first found month string should be taken
                    if months_list[i] in date and not(month):
                        month = months_list[i]
                        #print("month = ",month)
                month_as_word[index] = True
                #print("\nMonth is a word")
                
                if len(list_ints_in_date) < 2:
                    parsed_list[index] = " "
                else:
                    #checking the position of the year in the date
                    if sum(c.isdigit() for c in list_ints_in_date[1])==4:
                        year_int = list_ints_in_date[1]
                        day = list_ints_in_date[0]
                    elif sum(c.isdigit() for c in list_ints_in_date[0])==4:
                        year_int = list_ints_in_date[0]
                        day = list_ints_in_date[1]
                    else:
                        year_int = year_as_number_from_create_date
                        
                    #print("year_int = ",year_int)
                    year_as_4_digits = str(self.year_as_4_digits(str((year_int))))
                    #print("year_as_4_digits = ",year_as_4_digits)
                    if ((not year_as_4_digits)|(int(year_as_4_digits) < 4)):
                        parsed_list[index] = ""
                        continue
                    parsed_list[index]=str(day)+' '+month+' '+year_as_4_digits

            #in case the month is in a numerical format
            else:   
                if len(list_ints_in_date)<3:
                    parsed_list[index] = ""
                    continue
                
                int1 = list_ints_in_date[0]
                int2 = list_ints_in_date[1]
                int3 = list_ints_in_date[2]
                #print(type(int1),type(int2),type(int3))
                int11 = int(list_ints_in_date[0])
                int22 = int(list_ints_in_date[1])
                int33 = int(list_ints_in_date[2])
                #print(type(int11),type(int22),type(int33))
                #print(int11,int2,int33)
                
                month_int = ""
                
                #checking the position of the year in the date
                #year is in the third position --> month will be in the second or first position, format year-month-day
                if sum(c.isdigit() for c in int3)==4:
                    year_int = int33
                #year is in the first position --> month will be in the second position
                elif sum(c.isdigit() for c in int1)==4:
                    year_int = int11
                    month_int = int22
                    #print("year is in the first position")
                    day = int33
                    
                    year_as_4_digits = str(self.year_as_4_digits(str(year_int)))
                    #print("year_as_4_digits = ",year_as_4_digits)
                    if not year_as_4_digits:
                        parsed_list[index] = ""
                        continue
                    parsed_list[index]=str(month_int)+'/'+str(day)+'/'+year_as_4_digits
                    #print("full date = ",parsed_list[index])
                    continue
                #error for the year, take year from the create date
                else:
                    year_int = int3
                    #year_int = year_as_number_from_create_date
                    #print("year_int = ",year_int)
                
                #year handling - making sure that it's 4 digits
                year_as_4_digits = str(self.year_as_4_digits(str(year_int)))
                #print("year_as_4_digits = ",year_as_4_digits)
                if not year_as_4_digits:
                    parsed_list[index] = ""
                    continue
                
                #fuzzy date, we can't know which is the month and which is the day
                if (int11<13) and (int22<13):
                    day = int33
                    #print("month_as_word,month_as_number = ",month_from_create_date_as_word,month_from_create_date_as_number)
                    if int11 == month_from_create_date_as_number:
                        day = int22
                        #print("day is int22 = ",day)
                    elif int22 == month_from_create_date_as_number:
                        day = int11
                        #print("day is int11 = ",day)
                    else:
                        parsed_list[index] = ""
                        continue
                    parsed_list[index]=month_from_create_date_as_word+' '+str(day)+' '+year_as_4_digits
                    #print("full date = ",parsed_list[index])
                    #input from UTS: "Ticket_Create_Date:2017-09-05-04-57-22"
                    #print("fuzzy date")
                #format mm/dd/yyy
                elif (int11<13):
                    #month = self.get_month_word_from_number(int11)
                    parsed_list[index]=int1+'/'+int2+'/'+int3
                    #print("full date = ",parsed_list[index])
                #format dd/mm/yyy
                elif (int22<13):
                    #month = self.get_month_word_from_number(int22)
                    parsed_list[index]=int2+'/'+int1+'/'+int3
                    #print("full date = ",parsed_list[index])
                #else:
                    #print("error in date")
                #print(parsed_list[index])
                    
                #string = 'string%d' % (i,)
        
        #Parse date-time from candidates string elements        
        cal = parsedatetime.Calendar()
        
        #cal = cal.replace(tzinfo=timezone.utc)
        #print("parsed_list2 = ",parsed_list)
        for line in parsed_list:
            #print("line = ",line)
            #extracted_date_time, extraction_status = cal.parse(line,settings={'TIMEZONE': 'EST', 'TO_TIMEZONE': 'EDT'})
            extracted_date_time, extraction_status = cal.parse(line)
            #print("extracted_date_time = ",extracted_date_time)
            if extraction_status!=0:
                try:
                    res.append(time.strftime(Format_Dict[self.format_to_extract],  extracted_date_time))                
                    extracted_date_time = self.time_zone.localize(datetime(*extracted_date_time[:5]) ,is_dst=None)
                    extracted_date_time = (extracted_date_time - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
                    
                    #res_epoch.append(int(extracted_date_time))
                except:
                    pass

        #print("res = ",res)       
        #returns the first Issue date found in the text, (needed because the list is in reversed order)
        if (not res) or (self.multiple_values == True):
            #Filter to only unique entities in the extraction list, pay attention that 'set' returns an unordered list, with a new random order
            res_uniq = list(set(res))
            #print("here")
            dict = {self.entity_name:res_uniq}
        elif self.multiple_values == False:
            dict = {self.entity_name:res[0]}
         
        #print("dict = ",dict) 
        return dict
    
        #if (len(res_uniq)<1) or (self.unique_indicator and len(res_uniq)>1):
               #res_uniq = self.default_value    
    
        #res_uniq_epoch = list(set(res_epoch))
        #dict_epoch = {self.entity_name_epoch:res_uniq_epoch}
        #return dict, dict_epoch
        
         #if self.indicator: 
            #dict = {self.entity_name:len(res_uniq)>0}
            #return dict    
            
        #Return empty list if there's a demand for unique value and more than 1 value parsed        
        #if (self.unique_indicator) and len(res_uniq)>1:
        #    dict = {self.entity_name:[]}
        #    return dict
''' ------------------------------------------ Script Tester ------------------------------------------'''
def main(argv):
    line = argv[0]
    extractor = DateTimeExtractor(
                                    #time_zone = 'Africa/Lusaka'                                    
                                    #exclusion_list = ["list at"],
                                    #exclusion_offset=15
                                    #inclusion_list=["ISSUE_DATE","ask","cust sudah rec","aktivasi","activation date","waktu","tf","time frame","Time Frame","Time frame","tanggal","t.frime","kejadian","WKT","Sejak kapan terjadi kendala","pada tgl","kapan"],
                                    #indicator = True
                                    format_to_extract = 2,
                                    unique_indicator = False,
                                    entity_name = "Issue Date",
                                    #input_format = "ddmmyy",
                                    multiple_values = False
                                    )                                     
    res = extractor.get_matches(line)
        
    print(res)
    '''
    print('\n Converted for Israel Time:')
    for date in res[1]['datetime_epoch']:
        #print(date)        
        print (datetime(1970, 1, 1, tzinfo=pytz.utc) + timedelta(seconds=date) + timedelta(hours=3))
    '''
    

if __name__== "__main__":
    #sample = "waktu : 9.1.18w 07.00 AM" #not handled - wrong date ! explained in issues at the top
    
    
    #MON-DD-YYYY  - Krrish needs this format. If the date is with the first or second number that is higher than 12, then Amily will decide with a rule.
    
    
    #sample="Please perform 230 DRFs to SPS, OMA and EAIB with NMS Flag set to Y for the attached list at 2030 PM CT. This is last Apr 15th at 9PM" #gets the first date which is unknown..
    #sample="This is last Apr 15th at 9PM"  #-
    #sample="This is last Des. 15th at 9PM" #-
    
    #sample = "2 mar. 2015" #+
    #sample = "tfs 4 Djuli 2017" #+
    #sample = "waktu bla bla 4 may 2017" #+
    
    sample = "bla blka" #++ 0, empty list
    
    #sample = "4 Feb 2017, 5 mrt 2013" #-- 1, returns a mix of the dates, a problem !
    #sample = "4 djuli 2017"  #+
    #sample = "4-djuli-2017"  #+
    #sample = "4/djuli/2017"  #+
    #sample = "Notes: non receipt of load/ seeding date is every 25th of the month" #--,0,empty list
    
    #sample = "Time frame  : May 19 2017" #+
    #sample = "Time frame  : 19 May 2017" #+
    #sample = "Time frame  : Dec-19-2017" #+
    #sample = "Time frame  : Dec 19/2017" #+

    #sample = "Time frame = 2-Jan-2016" #+
    #sample = "Time frame = 2/Jan/2016" #+
    
    #sample = "Time frame  : 12/19/2017"
    #sample = "Time frame  : 19/12/2017"
    #sample = "Time Frame : 01/05/2017"
    #sample = "Time frame = 2-Jan-2018"
    #sample = "Time frame = 06/01/2017"
    #sample = "Time frame = 06/01/17"
    #sample = "Time frame = jun / 1 / 2017"
    #sample = "Time frame = jun/1/2017"
    #sample = "Time frame = jun/1/17"
    #sample = "waktu : 8 jan 2018 23.59"
    #sample = "waktu : 6 feb 2015 23.59"
    #sample = "Sejak kapan terjadi kendala : 9.1.18, 07.00 AM"
    #sample = " 9.1.18, 07.00 AM"
    #sample = '''\t\t\t===========PROBING============ \n kapan 15/1/2018 pukul 13.00 \nlokasi\t\nhp	Samsung Galaxy Tab 4 7.0 T235'''
    
    #sample = "KAPAN  : 16 JANUARI 2018"
    #sample = "Tanggal                : 2017-12-21 13:50:22"
    #sample = "Tanggal                : 2017-12-21 13:50:22"
    #sample = "004\\nTanggal : 2017-12-21 13:50:22\\nRemark :"
    #sample = "TIME FRAME : feb-27-2018 lenovo"
    

    
    doc = {"text":sample,"create_date":"Ticket_Create_Date:2017-01-05-04-57-22"}    #create date as yyy-mm-dd  
    
    main([doc])
    