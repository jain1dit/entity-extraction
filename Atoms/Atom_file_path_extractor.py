'''
EXTRACT FILE PATHS FROM TEXT

Return a list of unique file path names found in the text.
In the case where no file path names are found an empty list is returned.

Parameters:
    1. exclusion_offset -> number of characters to be ignored after an appereance of an exclusion_list item.
    2. exclusion_list -> textual items that precedes characters that should be ignored while searching. 
    3. inclusion_offset -> number of characters to be included after an appereance of an inclusion_list item.
    4. inclusion_list -> textual items that precedes characters that should be searched for. 
    5. indicator -> True if only a True/False indication of a file path existence in the doc should be returned, False if the actual entity is to be returned.

'''
import re

class FilePathExtractor:
	def __init__(self, 
				 entity_name='file_path',
				 exclusion_offset=60,
				 exclusion_list=[],
				 inclusion_offset=40,
				 inclusion_list=[],
				 indicator=False):
		#(/[\w-]*[a-zA-Z][\w-]*)+/
		self.entity_name = entity_name
		self.filepath_re = r"""(/[\w-]+)+/"""
		self.filepath_pattern = re.compile(self.filepath_re, re.VERBOSE | re.MULTILINE)
		self.exclusion_offset = exclusion_offset
		self.exclusion_list = exclusion_list
		self.inclusion_offset = inclusion_offset
		self.inclusion_list	= inclusion_list
		self.indicator = indicator

		self.exclusion_pats = []
		for exc in self.exclusion_list:
			self.exclusion_pats.append(re.compile(exc, re.IGNORECASE))

		self.inclusion_pats = []
		for inc in self.inclusion_list:
			self.inclusion_pats.append(re.compile(inc, re.IGNORECASE))

	def get_matches(self, doc):
		doc = doc["text"]     
		res = []

		for p in self.filepath_pattern.finditer(doc):
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
			#TODO: filenames \w+\.\w{3,4}
			s = p.group()
			number = re.search('/([\d-]+/)+', s)
			abbrev = re.search('/[A-Z]{3}/', s)
			number_flag = True
			abbrev_flag = True
			if number:
				number_flag = len(s) != len(number.group())
			if abbrev:
				abbrev_flag = len(s) != len(abbrev.group())
			if (not found_exc) and found_inc and number_flag and abbrev_flag:
				res.append(p.group())

		res_uniq = list(set(res))

		if self.indicator:
			dict = {self.entity_name:len(res_uniq)>0}      
			return dict

		dict = {self.entity_name:res_uniq}		
		return dict
def main(argv):
    line = argv[0]
    
    extractor = FilePathExtractor()
    
    res = extractor.get_matches(line)
    
    print(res)
    
if __name__ == "__main__":
    sample = "I want to extract the file path of this file - C:/Users/Yaniv.zip"
    doc = {"text":sample}      
    
    main([doc])