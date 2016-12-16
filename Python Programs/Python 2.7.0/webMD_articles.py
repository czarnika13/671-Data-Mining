#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import urllib2
import time
import csv
from bs4 import BeautifulSoup

#Purpose: Extract all WebMD article text, title and tags from a given list of URLS

#Read in file
#Return: List with each row containing a timestamp and url
def read_input(file):
    input = []
    with open(file, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            input.append(row)
    return input

#Request website connection with Urllib, convert into a Beautiful Soup object
#Return: Beautiful Soup Object
def get_soup(site):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(site, headers=hdr)
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page)
    return soup

#Extract article text from WebMD web article/blog
#Return: Article text, "slideshow" if not an article
def extract_text(soup):
    article = ''
    #Find all instances of text block in the code
    new_articles = soup.find("div", {"class": "article-page active-page"})
    old_articles = soup.find("div", {"id": "textArea"})
    blogs = soup.find("section", {"class": "content"})
    #Case by case for each difference in text blocks
    #Get text and split, remove Author and heading information (i.e. anything with HealthDay)
    if new_articles:
        # Loop through all p
        p = new_articles.find_all("p")
        for text in p:
            split = str(text.get_text().encode("utf-8")).split()
            if split:
                if split[0] != "By" and split[0] != "HealthDay":
                    article += text.get_text() + " "
        return article
    elif old_articles:
        # Loop through all p
        p = old_articles.find_all("p")
        for text in p:
            split = str(text.get_text().encode("utf-8")).split()
            if split[0] != "By" and split[0] != "HealthDay":
                article += text.get_text() + " "
        return article
    elif blogs:
        # Loop through all p
        p = blogs.find_all("p")
        for text in p:
            if not text.attrs:
                split = str(text.get_text().encode("utf-8")).split()
                if split:
                    if split[0] != "By" and split[0] != "HealthDay":
                        article += text.get_text() + " "
        return article
    else:
        return "slideshow"

#Extract next page in a WebMD web article/blog
#Return href for the next page of an article, nothing if there's only one page
def extract_next(soup):
    #Find the "Next" button on the page
    next = soup.findAll("div", {"class": "outline_fmt right"})
    #Extra the href from that html object
    if next:
        for test in next:
            a = test.contents[1]
            next = a.attrs['href']
        url = soup.find_all("link", {"rel": "amphtml"})
        if url:
            url = url[0].attrs["href"]
            next = url + next
            return next
        else:
            return None
    else:
        next = soup.findAll("li", {"class": "next"})
        for test in next:
            a = test.contents[1]
            next = a.attrs['href']
        return next

#Extract article title in a WebMD web article/blog
#Return Article Title, "error" if not found
def extract_title(soup):
    # Find all instances of header in the code
    header = soup.find("h1", {"itemprop": "headline"})
    slide_header = soup.find("span", {"id": "titleBarTitle_fmt"})
    page_header = soup.find("header", {"class": "page-header"})
    #Case by case for each difference in text header
    if header:
        title = header.get_text().encode("utf-8")
        return title
    elif slide_header:
        title = slide_header.get_text().encode("utf-8")
        return title
    elif page_header:
        h1 = page_header.find_all("h1")
        titles = h1[0]
        title = titles.get_text().encode("utf-8")
        return title
    else:
        return "error"

#Extract article tags in a WebMD web article/blog
#Return Article Tags, "error" if not found
def extract_tags(soup):
    #Find all instances of tags in the code
    meta = soup.find("meta", {"name": "keywords"})
    if meta:
        keywords = meta.attrs['content']
        tags = keywords.split(',')
        tags = [x.strip() for x in tags]
        return tags
    else:
        return "error"

#Call the extract methods and write the results to an output file
def write_article(timestamp, url):
    original_site = url
    new_site = str(original_site)
    run = True
    result = ""
    next = []
    f = open("final_file.csv", "a")
    while run:
        #Get Beautiful Soup Object
        soup = get_soup(new_site)
        #Extract Article Text
        result = extract_text(soup)
        #If article is not a slideshow, find if the article has multiple pages, extract href if so
        if result != "slideshow":
            next = extract_next(soup)
        #Extract title and tags
        title = extract_title(soup)
        tags = extract_tags(soup)
        #If there's no next page, or there's no title/tag, exit the loop
        if not next or title == "error" or tags == "error":
            run = False
        #If there's a "Next" page in the article, append the ref to the original url and loop again
        else:
            new_site = next
    #If the page was an article/blog, write the timestamp, url, title, tags, and article text
    if result != "slideshow":
        f.write(str(timestamp) + ", " + url + ", " +
                title.encode("utf-8") + ", " + str([x.encode('utf-8') for x in tags]) + ", " + result.encode("utf-8") + "\n")
    #If the page was a slideshow, write the timestamp, url, title, tags, no article text
    elif title != "error":
        f.write(str(timestamp) + ", " + url + ", " +
                title.encode("utf-8") + ", " + str([x.encode('utf-8') for x in tags]) + "\n")
    f.close()


def main():
    #Delete any files that were previously created
    if os.path.isfile('article_text.txt'):
        os.remove("article_text.txt")
    if os.path.isfile('article_tags.txt'):
        os.remove("article_tags.txt")
    if os.path.isfile('final_file.csv'):
        os.remove("final_file.csv")
    #Get urls and timestamps
    filename = "./Project/link.txt"
    input = read_input(filename)
    for i in input:
        write_article(i[0], i[1])
        time.sleep(5)

# Standard boilerplate to call the main() function.
if __name__ == '__main__':
    main()