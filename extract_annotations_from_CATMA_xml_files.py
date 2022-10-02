# python 3
# goal: extract annotation data from CATMA TEI (xml) files and save it to a csv file
# How to get the necessary files?
    # From the CATMA project click on the document you want to download.
    # Click on the three dots and select "Export Documents & Collections".
    # A file with .gz as an extension will be downloaded.
    # This file will have .tar before the .gz extension.
    # Extract this file (I used 7Zip).
    # Change ".tar" to ".xml".
    # If a dialogue about changing the file extension opens up, click OK.
    # Now the file can be opened in any text editor.
    # Open the Annotation section in CATMA and look for start and end point of the actual annotation.
    # Copy from the original text (located at the beginning of the xml file) the annotated span (gaps in the annotation are ok; make sure to copy from the FIRST to the LAST annotated character!)
    # Save this copied text to a txt file. Name this file [Original name of the xml file] + "_reference_text" 
    # Put all xml files into one directory.
    # Put all txt files into another directory.
    # Create a separate directory for the csv files.

# imports
import os
import sys
import re
import csv
from unicodedata import category

# custom functions
def extract_seg(annotation_file):
    file = annotation_files_dir + r"\\" + annotation_file
    f = open(file, "r", encoding = "utf-8")
    full_xml = f.read()
    pattern = "<seg.*\s*.*" # matches the <seg> tag
    list_of_matches = re.findall(pattern, full_xml)
    return (list_of_matches)

def extract_ana_and_chars(segment):
    pattern_ana = "\"#CATMA.*\""
    pattern_chars = "[0-9]*,[0-9]*"
    ana = re.findall(pattern_ana,segment)
    chars1 = re.findall(pattern_chars,segment)
    chars2 = re.split(",", chars1[0])
    return [ana[0],chars2[0],chars2[1]]

def extract_fs(annotation_file):
    file = annotation_files_dir + r"\\" + annotation_file
    f = open(file, "r", encoding = "utf-8")
    full_xml = f.read()
    pattern = "<fs xml:id.*type.*>" # this regex matches all the first lines inside the <fs> tag
    list_of_matches = re.findall(pattern, full_xml)
    return (list_of_matches)

def match_ana_with_xmlid(ana_and_chars, list_fss):
    pattern_ana = ana_and_chars[0][2:44]
    
    for fs in list_fss:
        ana_match = re.findall(pattern_ana,fs)
        if len(ana_match) == 1:
            pattern_type = "type=\".*\""
            annotation_type = re.findall(pattern_type,fs)
            type = annotation_type[0][6:-1]
    
    return [type, ana_and_chars[1], ana_and_chars[2]]

def decode_types(entry):
    encoded_type = entry[0]
    if encoded_type == "CATMA_276CCF39-696A-4B2C-8F8D-387CDE7F53AA":
        decoded_type = "thesis"
    elif encoded_type == "CATMA_52CECC33-7B72-4343-8462-FDF540F83F57":
        decoded_type = "argument"
    elif encoded_type == "CATMA_938768F0-1658-4A05-88C3-79FCAF265258":
        decoded_type = "notion"
    entry[0] = decoded_type

def return_reference_text(ref_text):
    file = reference_texts_dir + r"\\" + ref_text
    f = open(file, "r", encoding = "utf-8")
    readable_text = f.read()
    return readable_text

def index_string(string,running_index):
    dictionary_indexed_string = {}
    for character in string:
        dictionary_indexed_string[running_index] = character
        running_index += 1
    return dictionary_indexed_string

def create_list_for_csv(list_annotation_types_and_chars, dictionary_ref_text_indexed):
    list_for_csv = []
    category = ""
    list_annotation_types_and_chars_merged =[]
    for i in list_annotation_types_and_chars:
        if i[0] != category:
            if list_annotation_types_and_chars.index(i) != 0:
                list_annotation_types_and_chars_merged.append([category,start,end])
            category = i[0]
            start = int(i[1])
            end = int(i[2])
        else:
            end = int(i[2])
        

    for i in list_annotation_types_and_chars_merged:
        category = i[0]
        start = int(i[1])
        end = int(i[2]) + 1
        string = ""
        for j in range(start,end):
            if j not in dictionary_ref_text_indexed:
                break
            if dictionary_ref_text_indexed[j] == "\n":
                string += " "
            else:
                string += dictionary_ref_text_indexed[j]
        #print("|||",string,"|||") # this should print almost only full sentences
        list_for_csv.append([string,category])
    return list_for_csv

def create_csv(list_for_csv, name):
    os.chdir(results_dir)
    with open ("results_"+name+".csv", "w", encoding="utf-16") as f: # Warning! Changing the encoding may require a different delimiter in the next line.
        write = csv.writer(f, lineterminator = '\n', delimiter='\t') 
        toprow = ["Annotation Category", "Human-Annotated Text"]
        write.writerow(toprow)
        for i in list_for_csv:
            rows = [i[1],i[0]]
            write.writerow(rows)
    print("csv file successfully created for " + name)

############################################################################################
# Put your paths here
base_dir = r"C:\Users\fjbol\Desktop\HiWi DH Stuttgart\CATMA\Weiterverarbeitung für ML"
os.chdir(base_dir)
annotation_files_dir = os.getcwd() + r"\Annotation Files"
annotation_files = os.listdir(annotation_files_dir)
reference_texts_dir = os.getcwd() + r"\Reference Texts"
reference_texts = os.listdir(reference_texts_dir)
results_dir = r"C:\Users\fjbol\Desktop\HiWi DH Stuttgart\CATMA\Weiterverarbeitung für ML\Results"
#############################################################################################

# main loop
for annotation_file in annotation_files:
    segments = extract_seg(annotation_file)
    list_fss = extract_fs(annotation_file)
    list_ana_and_chars = []
    for segment in segments:
        list_ana_and_chars.append(extract_ana_and_chars(segment))
    list_annotation_types_and_chars = [] # this list will contain all spans with their respective annotation category
    for entry in list_ana_and_chars:
        list_annotation_types_and_chars.append(match_ana_with_xmlid(entry, list_fss))
    for entry in list_annotation_types_and_chars:
        decode_types(entry)
    #print(list_annotation_types_and_chars) # check if list items look like this: ["thesis", "128", "156"]
    for ref_text in reference_texts:
        #print(annotation_file) # example: CATMA-Corpus_Export Annotation Artstein GT.xml
        #print(ref_text) # example: CATMA-Corpus_Export Annotation Artstein GT_reference_text.txt
        annotation_file_comparable = annotation_file[:-4]
        #print(annotation_file) # check file name
        ref_text_comparable = ref_text[:-19]
        #print(ref_text) # check file name
        if annotation_file_comparable == ref_text_comparable:
            print("Reference text found for " + annotation_file)
            ref_text_as_str = return_reference_text(ref_text)
            starting_index = int(list_annotation_types_and_chars[0][1])
            dictionary_ref_text_indexed = index_string(ref_text_as_str,starting_index)
            #print(dictionary_ref_text_indexed)
            list_for_csv = create_list_for_csv(list_annotation_types_and_chars, dictionary_ref_text_indexed)
            #print(list_for_csv) # each item should consist of a text span and the annotation category, its length should be 2
            create_csv(list_for_csv,annotation_file_comparable)
            os.chdir(base_dir) # change the directory back to the original one to continue with the next file
        else:
            print("...Searching for reference text for " + annotation_file + "...")
print("All possible csv files created!")