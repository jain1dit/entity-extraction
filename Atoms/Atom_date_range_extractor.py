"""
EXTRACT DATE-RANGES ELEMENTS FROM A TEXT

Returnes two list of unique dates - dates from and date to - in the Date-time and EPOCH formats.
In case where no etitites were extracted, two empty lists are returned.
Time Zone definition is supported.

Basic Format expected in the text - American (MM/DD/YY)

Given the text, first a coarse filter finds lines suspected as containing
date ranges.
Next, they are parsed to get the ranges. 

Parameters:
    1. from_range_name -> name of the "from date" list
    2. to_range_name -> name of "to date" list
    3. from_range_epoch_name -> name of the "from date" in epoch format list
    4. to_range_epoch_name -> name of the "to date" in epoch format list
    3. time_zone -> Name of timezone. see full list at <pytz.all_timezones>. default - 'America/Chicago'
    
Known issues:
    1. In case where there are more than one dateranges within a line, only the first is being extracted.  
    2. A specific date (exa. Jul 17) is not returned as date from and date to.
"""

from datetime import datetime, timedelta
import re
import time
from dateutil.relativedelta import relativedelta
#from datetime import datetime, timedelta
import pytz

FINAL_TOKEN='$$$'


class ParserDate:
    def __init__(self,):
        self.UNINITIALIZED=-1
        self.day=self.UNINITIALIZED
        self.month=self.UNINITIALIZED
        self.year=self.UNINITIALIZED
        self.valid_prefix=False
    
    def set_day(self, day):
        self.day=day
    
    def set_month(self, month):
        self.month=month
    
    def set_year(self, year):
        self.year=year
        
    def set_valid_prefix(self, valid_prefix):
        self.valid_prefix=valid_prefix
    
    def is_day_defined(self):
        return self.day!=self.UNINITIALIZED
    
    def is_month_defined(self):
        return self.month!=self.UNINITIALIZED
    
    def is_year_defined(self):
        return self.year!=self.UNINITIALIZED
    
    def is_valid_prefix(self):
        return self.valid_prefix
    
    def is_date_full(self):
        return (self.is_day_defined() and self.is_month_defined() and self.is_year_defined())
    
    def is_date_undefined(self):
        return not (self.is_day_defined() or self.is_month_defined() or self.is_year_defined())
    
    def get_date(self):
        return datetime(self.year, self.month, self.day)
    
    def print_state(self):
        print("year: %d, month: %d, day: %d"%(self.year, self.month, self.day))
        
    def get_datetime(self):
        return datetime(self.year, self.month, self.day)
   
    def get_date_str(self):
        try:
            return datetime(self.year, self.month, self.day).strftime("%Y%m%d")
        except ValueError:
            print("getting max possible day in month:")
            return datetime(self.year, self.month, 30).strftime("%Y%m%d")
        
class Tokenizer:
    def __init__(self, line):
        self.tokenize(line)
        #print(self.tokens)
    
    def dash_split(self, token):
        res = []
        if token.find('-') > -1:
            fields = token.split('-')
            for f in fields:
                res.append(f)
                res.append('-')
            res = res[:-1]
        else:
            res = [token]
        return res
    
    def split_ignore(self, tok):
        fields = tok.replace(")"," ").replace("("," ").replace("/", " ").replace(","," ").replace("."," ").replace("and"," ").split()
        return fields
    
    def tokenize(self, line):
        #change all line to lowercase, to simplify later comparisons
        self.tokens = line.lower().split()
        filter_set = set([',',':'])
        ext_tokens = [self.dash_split(t) for t in self.tokens]
        orig_tokens = [t for sublist in ext_tokens for t in sublist]
        cur_tokens = [self.split_ignore(t) for t in orig_tokens]
        orig_tokens = [t for sublist in cur_tokens for t in sublist]
        #print("orig_tokens=%s"%(orig_tokens))
        self.tokens = [t for t in orig_tokens if t not in filter_set]
        self.tokens = [t for t in self.tokens if t!='']
        #add line final token
        self.tokens.append(FINAL_TOKEN)
        #print("self.tokens=%s"%(self.tokens))
        #print("num_tokens=%d"%(len(self.tokens)))
    
    def get_tokens(self):
        return self.tokens

class DateRangeParser:
    def __init__(self, line, verbose=0):
        self.verbose=verbose
        self.tokenizer = Tokenizer(line)
        self.tokens=self.tokenizer.get_tokens()
        self.end_offset=len(self.tokens)-1
        self.month_dict={}
        self.init_month_dict()
        self.month_length={}
        self.init_month_length()
        self.first_date=ParserDate()
        self.second_date=ParserDate()
        self.saw_to=False
        self.start_offset=self.get_start_offset()
        self.offset=self.start_offset
        self.lookahead=self.tokens[-1]
        if self.offset<self.end_offset-1:
            self.lookahead=self.tokens[self.offset+1]
        
            
    def echo(self, name):
        print("in: %s, current_token: %s"%(name, self.tokens[self.offset]))
        
    def is_valid_offset(self):
        return self.offset<self.end_offset
    
    def advance_one(self):
        self.offset+=1
        if self.offset<self.end_offset-1:
            self.lookahead=self.tokens[self.offset+1]
   
    def reached_barrier(self):
        '''
        True if we found token after text for a date
        '''
        cur_token = self.tokens[self.offset]
        return cur_token in[FINAL_TOKEN, "to","-"]
        
    def init_month_dict(self):
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 
                       'May', 'Jun', 'Jul', 'Aug',
                       'Sep', 'Oct', 'Nov', 'Dec']
        for i,m in enumerate(month_names):
            self.month_dict[m.lower()] = i+1
        if self.verbose>3: 
            print("month_dict:")                              
            print(self.month_dict)    
        
    def init_month_length(self):
        for month_num in range(1,13):
            self.month_length[month_num]=31
        self.month_length[2]=28
        for num in [4,6,9,11]:
            self.month_length[num]=30
        
    def is_date_start(self, t):
        if t.isdigit() and int(t)<32:
            return True
        else:
            stem = t[:3]
            if stem in self.month_dict:
                return True
        return False     
        
    def get_start_offset(self):
        if self.verbose>0:
            print("looking for start offset")
        for i,t in enumerate(self.tokens):
            if self.verbose>0:
                print(i, t)
            if self.is_date_start(t):
                break
        if self.verbose>0:
            print("start_offset is %d"%(i))
        return i
    
    def print_state(self):
        print("=========")
        print("offset:")
        print(self.offset)
        print("first date:")
        self.first_date.print_state()
        print("second date:")
        self.second_date.print_state()
    
    def parse_to(self):
        if self.verbose>0:
            self.echo("parse_to")
        if self.tokens[self.offset]=='to' or self.tokens[self.offset]=='-' or self.tokens[self.offset]=='until' or self.tokens[self.offset]=='till':
            self.offset += 1
            return True
        else:
            return False
        
    def parse_month(self):
        if self.verbose>0:
            self.echo("parse_month")
        res=-1
        cur_token = self.tokens[self.offset]
        if cur_token.isdigit():
            val = int(cur_token)
            if val>=1 and val<=12:
                res=val
        else:
            stem = self.tokens[self.offset][:3]
            if stem in self.month_dict:
                res = self.month_dict[stem]
        if res != -1:
            self.advance_one()
        if self.verbose>0:
            print("in parse_month, res=%d"%(res))
        return res
    
    def parse_year(self):
        if self.verbose>0:
            self.echo("parse_year")
        res = -1
        cur_tok = self.tokens[self.offset]
        if cur_tok.isdigit():
            val = int(cur_tok)
            if val>0 and val<100:
                res=val+2000
            elif val>2000 and val<2100:
                res=val
        if self.verbose>0:
            print("in parse_year, res=%d"%(res))
        if res != -1:
            self.advance_one()
        return res
        
    def parse_date_dmy(self, cur_parser_date):
        cur_parser_date.set_day(self.parse_day())
        if not cur_parser_date.is_day_defined():
            return
        if self.reached_barrier():
            return
        cur_parser_date.set_month(self.parse_month())
        cur_parser_date.set_year(self.parse_year())
        if self.verbose>0:
            print("after parse_date_dmy:")
            cur_parser_date.print_state()
        
    def parse_date_mdy(self, cur_parser_date):
        cur_parser_date.set_month(self.parse_month())
        if not cur_parser_date.is_month_defined() or not self.is_valid_offset():
            return
        cur_parser_date.set_valid_prefix(True)
        if self.reached_barrier():
            return
        cur_parser_date.set_day(self.parse_day())
        if not cur_parser_date.is_day_defined():
            cur_parser_date.set_valid_prefix(False)
        if not self.reached_barrier():
            cur_parser_date.set_year(self.parse_year())
        if self.verbose>0:
            print("after parse_date_mdy:")
            cur_parser_date.print_state()
        
        
        
    def parse_date(self, cur_parser_date, date_first_offset):
        self.parse_date_mdy(cur_parser_date)
        if not (cur_parser_date.is_valid_prefix()):
            self.offset=date_first_offset
            #cur_parser_date = ParserDate()
            self.parse_date_dmy(cur_parser_date)
            
    def parse_day(self):
        if self.verbose>0:
            self.echo("parse_day")
        res = -1
        if self.tokens[self.offset].isdigit():
            val = int(self.tokens[self.offset])
            if val >= 1 and val <= 31:
                res=val
                self.advance_one()
        return res
    
    def get_last_day(self, month_num):
        return self.month_length[month_num]
    
    def complement_days_from_default(self):
        self.first_date.set_day(1)
        self.second_date.set_day(self.get_last_day(self.second_date.month))
    
    def complement_years_from_default(self):
        '''
        If no year was mentioned, and the months are before current month,
        use current year. Alternatively use previous year.
        '''
        cur_year=int(time.strftime("%Y"))
        prev_year=cur_year-1
        cur_month=int(time.strftime("%m"))
        if cur_month>=self.second_date.month:
            self.second_date.set_year(cur_year)
            if cur_month>=self.first_date.month:
                self.first_date.set_year(cur_year)
            else:
                self.first_date.set_year(prev_year)
        else:
            self.second_date.set_year(prev_year)
            self.first_date.set_year(prev_year)
        
    def complement_dates(self):
        UNINITIALIZED=self.first_date.UNINITIALIZED
        if self.second_date.is_date_undefined():
            return #cannot complement - missing data
        if self.first_date.month==UNINITIALIZED:
            self.first_date.set_month(self.second_date.month)
        if self.first_date.year==UNINITIALIZED:
            self.first_date.set_year(self.second_date.year)
        if self.second_date.month==UNINITIALIZED:
            self.second_date.set_month(self.first_date.month)
        if not (self.first_date.is_day_defined() or self.second_date.is_day_defined()):
            self.complement_days_from_default()
        if not (self.second_date.is_year_defined()):
            if self.first_date.is_year_defined():
                self.second_date.set_year(self.first_date.year)
            else:
                self.complement_years_from_default()
            
    def parse_date_range(self):
        self.parse_date(self.first_date, self.offset)
        
        if not self.is_valid_offset():
            return
        if self.verbose>0:
            print("after parsing first date:")
            self.print_state()
        
        parse_to_res = self.parse_to()

        if self.verbose>0:        
            print("after parsing to:")
            self.print_state()
        if not self.is_valid_offset():
            return
        if not parse_to_res:
            return
        
        self.parse_date(self.second_date, self.offset)
        if self.verbose>0:
            print("after parsing second date:")
            self.print_state()
            
       
        #if not self.is_valid_offset():
        #   return
        if not self.has_full_range():
            #missing parts - try to complement them
            self.complement_dates()
        if self.verbose>0:
            print("after complementing dates:")
            self.print_state()
        
    def parse(self):
        first_date_str="error"
        second_date_str="error"
        if self.is_valid_offset():
            self.parse_date_range()
            if self.has_full_range():
                first_date_str = self.first_date.get_date_str()
                second_date_str = self.second_date.get_date_str()
                #print("after parsing, offset=%d"%(self.offset))
        return first_date_str, second_date_str
    
    def parse_several(self):
        res_lst = []
        prev_offset = -1
        while prev_offset < self.offset:
            prev_offset=self.offset
            res_lst.append(self.parse())
        #print(res_lst)
        return res_lst
    
    def has_full_range(self):
        return (self.first_date.is_date_full() and self.second_date.is_date_full())
    
class PotentialDateFilter:
    def __init__(self):
        self.date_regex = self.get_month_regex()
        
    def get_month_regex(self):
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 
                       'May', 'Jun', 'Jul', 'Aug',
                       'Sep', 'Oct', 'Nov', 'Dec']
        with_brackets = ["(?:\W" + name + ")" for name in month_names]
        year_pat = "(?:\D(20)?\d{2}\D)"
        with_brackets.append(year_pat)
        date_pat = '|'.join(with_brackets)
        #inline_pat = ''.join([r"^.*", date_pat,".*$"])
        #print(inline_pat)
        #print(re.compile(date_pat, re.MULTILINE|re.IGNORECASE))
        return re.compile(date_pat, re.MULTILINE|re.IGNORECASE)
    
    def is_potential_date(self, line):
        #Checks for a potential date range line and returnes the line where this date range is started
        parsed_line_re = self.date_regex.search(line)
        date_range_line = None
        if parsed_line_re is not None:
            #date_range_line = line[parsed_line_re.span()[0]:]
            date_range_line = line[max(parsed_line_re.span()[0]-3,0):]
        return (parsed_line_re is not None), date_range_line 
    

# Added by Yaniv - Parses verbose date ranges
class VerboseDateRangeParser:
    def __init__(self, line):
        self.parsed_line = line
        
    def parse_verbose(self):
        numeric_value_regex = "\d(\d?)"
        numeric_verbose_regex = "\s(one|two|three|four|five|six|seven|eight|nine|ten)\s"
        search_for_numeric_value = re.compile(numeric_value_regex, re.MULTILINE|re.IGNORECASE).search(self.parsed_line)
        search_for_numeric_verbose_value = re.compile(numeric_verbose_regex, re.MULTILINE|re.IGNORECASE).search(self.parsed_line)
        if search_for_numeric_value is None:
            if search_for_numeric_verbose_value is not None:
                verbose_dict = {"one":1, "two":2, "three":3, "four":4,
                                "five":5, "six":6, "seven":7, "eight":8,
                                "nine":9, "ten":10}
                #convert verbose value to integer - relative delta function receives only integer values 
                numeric_value = int(verbose_dict[re.sub("\s","",search_for_numeric_verbose_value.group(0))])
            else:
                return [("error","error")]
        else:
            #convert numeric value to integer - relative delta function receives only integer values        
            numeric_value = int(search_for_numeric_value.group(0))
        
        #indicates if the range is defined by user as months or days        
        day_indicator = False        
        if self.parsed_line.find("day") > 0:
            day_indicator = True
            
        # To date - the date of today        
        to_year=(time.strftime("%Y"))
        to_month=(time.strftime("%m"))
        to_day=(time.strftime("%d"))
        to_date = "".join([to_year,to_month,to_day])
        
        # From date - "months" or "days" from today
        cur_day = datetime(int(to_year), int(to_month), int(to_day))
        
        if day_indicator:
            from_date = cur_day+relativedelta(days=-numeric_value)
        else:
            from_date = cur_day+relativedelta(months=-numeric_value)+relativedelta(days = 1)
        
        from_year=(from_date.strftime("%Y"))
        from_month=(from_date.strftime("%m"))
        from_day=(from_date.strftime("%d"))
        from_date = "".join([from_year,from_month,from_day])
        
        date_range = [(from_date, to_date)]

        return date_range
        

# Added by Yaniv - Filters out lines with verbose date range (months only)
class PotentialVerboseDateFilter:
    def __init__(self):
        self.date_regex = self.get_verbose_regex()
        
    def get_verbose_regex(self):
        verbose_date_pat = "((latest)|(last)|(prev)|(past)).{0,10}(month|day)"
        return re.compile(verbose_date_pat, re.MULTILINE|re.IGNORECASE)
    
    def is_potential_date(self, line):
        #parsed_line = self.date_regex.search(line).group(0)
        parsed_line = self.date_regex.search(line)
        if parsed_line is not None:
            return parsed_line.group(0), True
        else:
            return "", False
            
# Added by Yaniv - Parses full month when only month name appears
class FullMonthParser:
    def __init__(self,):
        self.year_pat = "(?:(20)\d{2}(\D|$))"
        self.month_names = ['Jan', 'Feb', 'Mar', 'Apr', 
                       'May', 'Jun', 'Jul', 'Aug',
                       'Sep', 'Oct', 'Nov', 'Dec',
                       'January', 'February', 'March', 'April', 
                       'May', 'June', 'July', 'August',
                       'September', 'October', 'November', 'December']
        self.date_regex = self.get_full_month_regex()   
        
    def month_regex (self):
        with_brackets = ["(?:" + name + ")" for name in self.month_names]
        month_pat = '|'.join(with_brackets)
        return month_pat

    def get_full_month_regex(self):
        month_pat = self.month_regex()         
        date_pat = "\s("+month_pat+")\s(\s{0,10}?)"+self.year_pat
        return re.compile(date_pat, re.MULTILINE|re.IGNORECASE)
    
    def is_potential_date(self, line):
        #parsed_line = self.date_regex.search(line).group(0)
        parsed_line = self.date_regex.search(line)
        if parsed_line is not None:
            year = (re.compile(self.year_pat, re.MULTILINE|re.IGNORECASE)).search(line).group(0)
            month_pat = self.month_regex() 
            month = (re.compile(month_pat, re.MULTILINE|re.IGNORECASE)).search(line).group(0)[:3].title()
            month = self.month_names.index(month)+1
            
            date_from = datetime(int(year), int(month), 1)
            date_to = date_from+relativedelta(months=1)+relativedelta(days = -1)
            
            from_year=(date_from.strftime("%Y"))
            from_month=(date_from.strftime("%m"))
            from_day=(date_from.strftime("%d"))
            from_date = "".join([from_year,from_month,from_day])
            
            to_year=(date_to.strftime("%Y"))
            to_month=(date_to.strftime("%m"))
            to_day=(date_to.strftime("%d"))
            to_date = "".join([to_year,to_month,to_day])
            
            date_range = [(from_date, to_date)] 
            
            return True, date_range
        else:
            return False, []

class DateRangeExtractor:
    def __init__(self,
                 from_range_name = 'date_from',
                 to_range_name = 'date_to',
                 from_range_epoch_name = 'date_from_epoch',
                 to_range_epoch_name = 'date_to_epoch',
                 time_zone = 'America/Chicago'
                 ):
        self.potential_date_finder = PotentialDateFilter()
        self.potential_verbose_date_finder = PotentialVerboseDateFilter()
        self.full_month_parser = FullMonthParser()
        self.from_range_name = from_range_name
        self.to_range_name = to_range_name
        self.from_range_epoch_name = from_range_epoch_name
        self.to_range_epoch_name = to_range_epoch_name
        self.time_zone = time_zone
        self.time_zone = pytz.timezone(self.time_zone)
        
    def get_matches(self, doc):
        doc = doc["text"]
        good_list = []
        error_list = []
        for line in doc.replace(":"," ").split('\n'):
            #is_potential_date, line
            if self.potential_date_finder.is_potential_date(line)[0]:
                parser = DateRangeParser(self.potential_date_finder.is_potential_date(line)[1], verbose=0)
                res_lst=parser.parse_several()
                for res in res_lst:
                    first, second=res
                    if first=="error":
                        error_list.append(res)
                    else:
                        good_list.append(res)

            #Added by Yaniv - Search for date ranges written verbose (i.e. "past 2 months")
            parsed_line, parsed_filter = self.potential_verbose_date_finder.is_potential_date(line)
            if parsed_filter:
                parser = VerboseDateRangeParser(parsed_line)
                res_lst=parser.parse_verbose()
                for res in res_lst:
                    first, second=res
                    if first=="error":
                        error_list.append(res)
                    else:
                        good_list.append(res)
            
            #Added by Yaniv - last check - check for one full month            
            if not good_list:    
                full_month_parsed_indicator, full_month_parsed_date_range = self.full_month_parser.is_potential_date(line)
                if full_month_parsed_indicator:
                    for res in full_month_parsed_date_range:
                        good_list.append(res)
                    
        #Transform to a unique list of daterange lists     
        good_list = [list(x) for x in set(tuple(x) for x in good_list)]
       

      #Transform date range list to two lists - dates from and dates to - Date-time format        
        from_list = []
        to_list = []
        for date in good_list:
            from_value = datetime(int(date[0][:4]), int(date[0][4:6]), int(date[0][6:8]), 0,0,0)
            to_value = datetime(int(date[1][:4]), int(date[1][4:6]), int(date[1][6:8]), 23,59,59)
            
            #In case of error where the from date is higher than the to date 1 month is being substracted from the from date
            if from_value > to_value:
                day = int(date[0][6:8])
                from_value = (from_value.replace(day=1)-timedelta(days=1)).replace(day = day)
            
            from_list.append(from_value.strftime('%b-%d-%Y %H:%M'))
            to_list.append(to_value.strftime('%b-%d-%Y %H:%M'))
        from_dict = {self.from_range_name:from_list}
        to_dict = {self.to_range_name:to_list}


        #Sorting mechanism - added on 3/21/18
        try:
            result_dict=dict(zip(from_list, to_list))
            sorted_from_list = sorted(result_dict)
            sorted_to_list=[]
            for i in sorted_from_list:
                sorted_to_list.append(result_dict[i])
            from_dict={self.from_range_name:sorted_from_list}
            to_dict = {self.to_range_name:sorted_to_list}
        except:
            pass
        
        #Transform dates to Epoch        
        for date in good_list:
            #First convert string to datetime
            from_values = [date[0][:4], date[0][4:6], date[0][6:8] ,0,0,0]
            from_values = map(int, from_values)
            to_values = [date[1][:4], date[1][4:6], date[1][6:8], 23,59,59]
            to_values = map(int, to_values)
            date[0] = datetime(*from_values).timetuple()
            date[1] = datetime(*to_values).timetuple()
            
            #In case of error where the from date is higher than the to date 1 month is being substracted from the from date            
            if date[0]>date[1]:            
                from_date = list(date[0])
                if from_date[1] > 1:
                    from_date[1] -= 1
                else:
                    from_date [1] = 12
                date[0] = time.struct_time(tuple(from_date))
            
            #Convert datetime to epoch - from date
            date[0] = self.time_zone.localize(datetime(*date[0][:5]) ,is_dst=None)
            date[0] = int((date[0] - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds())
            #Convert datetime to epoch - to date
            date[1] = self.time_zone.localize(datetime(*date[1][:5]) ,is_dst=None)
            date[1] = int((date[1] - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds())
        
        #Transform date range list to two lists - dates from and dates to - Epoch format
        from_list = []
        to_list = []        
        for item in good_list:
            from_list.append(item[0])
            to_list.append(item[1])
        
        from_dict_epoch = {self.from_range_epoch_name:from_list}
        to_dict_epoch = {self.to_range_epoch_name:to_list}
        #return from_dict, to_dict, from_dict_epoch, to_dict_epoch
        return from_dict, to_dict


def main(argv):
    line = argv[0]
    dre = DateRangeExtractor()
    df = dre.get_matches(line)
    
    if type(df) is dict: print(df)
    if type(df) is tuple:
        for list_instance in df:
            print(list_instance)
    
    #print(type(df))

if __name__== "__main__":

        
    #sample='''
    #from 8/28/-9/29
    #'''
    
    #sample = 'coverage date of extraction:06/13/17 to 07/12/17'
    #sample = 'the date I want to extract is April 16 to May 15, 2017'
    #sample = 'Bill no.6, from June 10, 2017 until July 9, 2017'
    #sample = 'please extract for june 2016'
    sample = r"""71430237
9171430234
9171454577
9171430235
9171430236

Coverage Date of Extraction:	 2/16/18-3/15/18 and 3/16/18 - 4/15/18
Fields Needed:	 EXTRACTION OF DATA USAGES and CALL AND TEXT USAGES
Customer Type(only if applicable):	 n/a
Target/Completion date:	 Urgent
	 
Attachment Needed:	 """
    #sample = 'extract the last 3 months'
    #sample = 'e jl 7/1/2017-7/31/2017'
    #sample = 'I want to extract 7/3/2017-8/12/2017 and 6/13/2017-7/12/2017 please'

    '''Do not work properly'''
    #sample ='June 16 to July 17' #does not parse correctly (change to Jun)    
    #sample = 'erage date of extraction:bill 18 cycle 07/10/17 to 08/09/17' #does not parsed correctly 
    #sample = 'please extract for June until August 2016' #does not parse correctly
    #sample='''Kindly facilitate data extraction request from bill period 7/27/-9/26/, 7/27/-8/26/ last 2 months and confirm if the charges were valid or not''' #multi parse issue?

    
    doc = {"text":sample}      
    
    main([doc])

