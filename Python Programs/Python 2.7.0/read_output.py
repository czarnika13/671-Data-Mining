#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

#Purpose: Clean the results of webMD_articles.py

#Read input from csv file
#Return input in a list, format: timestamp + ", " + url + ", " + title + ", " + tags + ", " + text
def read_input(file):
    input = []
    with open(file, 'rb') as f:
        reader = f.readlines()
        count = 0
        for row in reader:
            #Split the row by commas
            row = row.strip().split(",")
            count += 1
            #Extract the timestamp, url, and title
            timestamp = row[0]
            url = row[1]
            title = row[2]
            title = "|" + title + "|"
            tt = ""
            #Get all text and tags, because the tags were in a list [a, b, c] format, multiple rows were individual tags
            for i in range(3, len(row)):
                tt += "".join(row[i])
            p = re.compile('.+(\[\'.+\'\] )(.+)')
            tag_text = p.match(tt)
            #If there was both text and tags in the row, append both
            if tag_text:
                tags = tag_text.group(1)
                text = tag_text.group(2)
                tags = "|" + tags + "|"
                text = "|" + text + "|"
            #If there was only tags, append the tags and an empty text field of ||
            else:
                tag_text = re.search('(\[.+\])', tt)
                tags = tag_text.group()
                tags = "|" + tags + "|"
                text = "||"
            input.append(timestamp + ", " + url + ", " + title + ", " + tags + ", " + text)
    return input


#For tag analysis, do the same process as before, but only extract the tags
#Return input in a list, format: timestamp + ", " + tags
def read_topicsum(file):
    input = []
    with open(file, 'rb') as f:
        reader = f.readlines()
        count = 0
        for row in reader:
            # Split the row by commas
            row = row.strip().split(",")
            count += 1
            # Extract the timestamp
            timestamp = row[0]
            tt = ""
            #Get all text and tags, because the tags were in a list [a, b, c] format, multiple rows were individual tags
            for i in range(3, len(row)):
                tt += "".join(row[i])
            p = re.compile('.+(\[\'.+\'\] )(.+)')
            tag_text = p.match(tt)
            #Regardless of if there was both text and tags in the row, append only the tags
            if tag_text:
                tags = tag_text.group(1)
            else:
                tag_text = re.search('(\[.+\])', tt)
                tags = tag_text.group()
            tags = tags.strip().split()
            #Remove extra punctuation such as brackets
            for tag in tags:
                out = "".join(c for c in tag if c not in ('[', ']', '\''))
                input.append(timestamp + ", " + out)
    return input

def main():
    #Open webMD_articles output file
    filename = "./final_file.csv"
    #Extract input, clean and write to final_output
    input = read_input(filename)
    f = open("final_output.csv", "w")
    for line in input:
        f.write(str(line) + "\n")
    f.close()
    #Extract input (only timestamps and tags), clean and write to final_output
    input = read_topicsum(filename)
    f = open("final_tags.csv", "w")
    for line in input:
        f.write(str(line) + "\n")
    f.close()

# Standard boilerplate to call the main() function.
if __name__ == '__main__':
    main()