'''
EXTRACT FILE NAMES FROM TEXT

Return a list of unique file names found in the text.
In the case where no file name names are found an empty list is returned.


Parameters:
    1. exclusion_offset -> number of characters to be ignored after an appereance of an exclusion_list item.
    2. exclusion_list -> textual items that precedes characters that should be ignored while searching. 
    3. inclusion_offset -> number of characters to be included after an appereance of an inclusion_list item.
    4. inclusion_list -> textual items that precedes characters that should be searched for. 
    5. indicator -> True if only a True/False indication of a file name existence in the doc should be returned, False if the actual entity is to be returned.

'''
import re

class FileNameExtractor:
	def __init__(self,
                  entity_name='file_name',
                  exclusion_offset=60,
                  exclusion_list=[],
                  inclusion_offset=40,
                  inclusion_list=[],
                  indicator=False):
		#(/[\w-]*[a-zA-Z][\w-]*)+/
         self.filename_re = r"""([\w-]+\.)+[a-z]{1,5}""" #Regex for a legal file name
         self.entity_name = entity_name
         self.filename_pattern = re.compile(self.filename_re, re.VERBOSE | re.MULTILINE)
         self.exclusion_offset = exclusion_offset
         self.exclusion_list = exclusion_list
         self.inclusion_offset = inclusion_offset
         self.inclusion_list	= inclusion_list
         self.indicator = indicator
		#list of extenstions to filter for, avoids grabbing urls
		#pulled from http://it.nmu.edu/docs/common-windows-file-extensions then added upon
		#maybe remove .htm(l) which would likely come from a url anyway
         self.extension_list = ['\.txt\Z','\.aif\Z','\.au\Z','\.avi\Z','\.bat\Z',
                                '\.bmp\Z','\.ja(r|va)\Z','\.csv\Z','\.cvs\Z','\.dbf\Z',
                                '\.dif\Z','\.doc(x)?\Z','\.eps\Z','\.exe\Z','\.fm3\Z',
                                '\.gif\Z','\.hqx\Z','\.htm(l)?\Z','\.jp(e)?g\Z','\.mac\Z',
                                '\.map\Z','\.mdb\Z','\.mid(i)?\Z','\.mov\Z|\.qt\Z',
                                '\.mt[bw]\Z','\.pdf\Z','\.[pt]65\Z','\.png\Z','\.ppt(x)?\Z',
                                '\.psd\Z','\.psp\Z','\.qxd\Z','\.ra\Z','\.rtf\Z','\.sit\Z',
                                '\.tar\Z','\.tif\Z','\.txt\Z','\.wav\Z','\.wk[123s]\Z',
                                '\.wp[d5]\Z','\.xls(x)?\Z','\.zip\Z','\.c(pp)?\Z',
                                '\.log\Z','\.sh\Z|\.bat\Z','\.js(p)?\Z','\.h\Z']
         self.exclusion_pats = []
         for exc in self.exclusion_list:
             self.exclusion_pats.append(re.compile(exc, re.IGNORECASE))
         self.inclusion_pats = []
         for inc in self.inclusion_list:
             self.inclusion_pats.append(re.compile(inc, re.IGNORECASE))    
             
	def get_matches(self, doc):
         doc = doc["text"]
         res = []
         for p in self.filename_pattern.finditer(doc):
             #print(p.span())
             found_exc = False
             found_inc = False
             start_pos, end_pos = p.span()
             
             for exc_pat in self.exclusion_pats:
                 if exc_pat.search(doc[max(start_pos-self.exclusion_offset,0):start_pos]):
                     found_exc = True
            
             if not self.inclusion_list:
                 found_inc = True
             else:
                 found_inc = False
             
             if not self.inclusion_list:
                 found_inc = True
             else:            
                 for inc_pat in self.inclusion_pats:
                     if inc_pat.search(doc[max(start_pos-self.inclusion_offset,0):start_pos]):
                         found_inc = True
			#TODO: filenames \w+\.\w{3,4}
             s = p.group()
	
             if (not found_exc) and found_inc:
                 for i in range(len(self.extension_list)):
                     if re.search(self.extension_list[i], s):
                         res.append(s)

         res_uniq = list(set(res))
         #print(res_uniq)

         if self.indicator:
             dict = {self.entity_name:len(res_uniq)>0}
             return dict

         dict = {self.entity_name:res_uniq}        
         return dict

def main(argv):
    line = argv[0]
    
    extractor = FileNameExtractor()
    
    res = extractor.get_matches(line)
    
    print(res)
    
if __name__ == "__main__":
    sample = "I wantto extract this file name_amdocs.txt , this in not a legal file name - try.yan"
    doc = {"text":sample}      
    
    main([doc])