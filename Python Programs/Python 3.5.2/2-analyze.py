import requests
import json
import csv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import copy

# Enter your Mashape API key for the Text Summarization (https://market.mashape.com/textanalysis/text-summarization) API here:
API_KEY = ""

EXAMPLE_CORPUS_ENTRY = [["Fri Jul 22 14:55:41 EDT 2016",
           "https://t.co/Tr3ng6dQcO",
           "Marijuana Chemical May be in Colorado Town's Water",
           "['marijuana', 'pot', 'cannabis', 'THC', 'Hugo', 'Colorado', 'water', 'water supply', 'well']",
           "July 22, 2016 -- Residents of the Colorado town of Hugo have been told not to drink or shower in tap water because the community\'s wells may be contaminated with the chemical in marijuana that makes people high. THC was detected in some tests conducted with field kits, and more definitive laboratory tests are underway, according to sheriff\'s Capt. Michael Yowell, the Associated Press reported. No illnesses have been linked to the town\'s water, Lincoln County Public Health Director Susan Kelly said. There are indications that one of the town\'s five wells was tampered with, but it\'s not known if the water was deliberately tainted, according to Yowell. The FBI and the Colorado Bureau of Investigation are assisting in the case, he added. Hugo has a population of about 730 and is located about 100 miles southeast of Denver, the AP reported. Drinking THC-contaminated water is unlikely to cause lasting health effects, according to Mark Salley, a spokesman for the state Department of Public Health and Environment. The effects would depend on the concentration of THC in the water and how much and how quickly water was consumed, he told the AP."]]


def get_summary_from_api(article_body, api_key):
    endpoint = "https://textanalysis-text-summarization.p.mashape.com/text-summarizer-text"
    api_key = "qXbihCWt3Dmsh1XKz8TvWa9QrR02p1yt7rzjsnPHNf97qszGrg"
    headers = {"X-Mashape-Key": api_key,
               "Content-Type": "application/x-www-form-urlencoded",
               "Accept": "application/json"}
    params = {
        "sentnum": "1",
        "text": article_body
    }
    result = requests.post(endpoint,data=params,headers=headers)
    return json.loads(result.text)['sentences'][0]

def load_csv(filename):
    with open(filename, mode='rt', encoding='utf-8') as f:
        lines = []
        reader = csv.reader(f,delimiter=",",quotechar='|', quoting=csv.QUOTE_ALL)
        for row in reader:
            clean_row = []
            for field in row:
                field = field.replace("|", "")
                field = field.rstrip()
                field = field.lstrip()
                clean_row.append(field)
            lines.append(clean_row)
        return lines

def clean_corpus_for_analysis(corpus):
    title_idx = 2
    text_idx = 4

    to_remove = []

    for i in range(0,len(corpus)):
        line = corpus[i]
        # check for missing title, which occasionally happens given variation in
        if line[title_idx] == "error" or line[title_idx] == "":
            to_remove.append(i)
            continue
        # check for missing text
        if line[text_idx] == "error" or line[text_idx] == "":
            to_remove.append(i)
    i = len(to_remove) - 1
    while i >= 0:
        del corpus[to_remove[i]]
        i -= 1
    return corpus

def get_corpus_sentiment(corpus):
    title_idx = 2
    text_idx = 4
    summary_idx = 5
    analyzer = SentimentIntensityAnalyzer()

    for line in corpus:
        title_scores = analyzer.polarity_scores(line[title_idx])
        text_scores = analyzer.polarity_scores(line[text_idx])
        summary_scores = analyzer.polarity_scores(line[summary_idx])
        line.append(title_scores["compound"])
        line.append(text_scores["compound"])
        line.append(summary_scores["compound"])
    return corpus

# This function takes a cleaned corpus (that is, one with blank values for title or text removed)
# and makes a call to the TextSummarizer API to summarize the text
def get_summaries(api_key, cleaned_corpus):
    text_idx = 4
    i = 0
    for line in cleaned_corpus:
        text = line[text_idx]
        summary = get_summary_from_api(text)
        summary_tuple = (i, summary)
        backup_summary_tuple(summary_tuple)
        line.append(summary)
        i += 1
    return

def load_summaries_from_backup(filename):
    summary_list = []
    with open(filename, "rt") as f:
        for line in f.readlines():
            comma_re = re.search("([0-9]*,)", line)
            split_idx = comma_re.regs[0][1]
            line_index = line[:split_idx - 1]
            summary = line[split_idx + 1:]
            summary_list.append((summary.replace("\n",""),int(line_index)))
    return [string for string, index in sorted(summary_list, key=lambda x: x[1], reverse=False)]

def backup_summary_tuple(summary_tuple):
    with open("summary_backup_prog.txt", mode="a") as f:
        f.write(str(summary_tuple[0]) + ", " + str(summary_tuple[1]) + "\n")

def write_results_to_csv(filename, complete_corpus):
    with open(filename, mode="wt", encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_ALL)
        writer.writerow(["Date", "Link", "Title", "Tags", "ArticleText", "Summary", "TitleSentimentVader", "TextSentimentVader", "SummarySentimentVader"])
        for line in complete_corpus:
            writer.writerow(line)
    return

def dummy_out_cancer(corpus):
    title_idx = 2
    text_idx = 4
    summary_idx = 5
    for line in corpus:
        line[title_idx] = line[title_idx].replace("cancer", "")
        line[title_idx] = line[title_idx].replace("Cancer", "")
        line[summary_idx] = line[summary_idx].replace("cancer", "")
        line[summary_idx] = line[summary_idx].replace("Cancer", "")
        line[text_idx] = line[text_idx].replace("cancer", "")
        line[text_idx] = line[text_idx].replace("Cancer", "")
    return corpus
        

def main():
    backup_summaries = load_summaries_from_backup("summary_backup_prog.txt")
    loaded_corpus = load_csv("corpus.csv")
    cleaned_corpus = clean_corpus_for_analysis(loaded_corpus)
    if len(cleaned_corpus) == len(backup_summaries):
        for i in range(0, len(cleaned_corpus)):
            cleaned_corpus[i].append(backup_summaries[i])
    else:
        get_summaries(cleaned_corpus)
    # create a copy of the cleaned corpus with summaries, for later use in producing a
    # sentiment set with "cancer" removed from its body (no pun intended)
    dummy_out_cancer_copy = copy.deepcopy(cleaned_corpus)
    cleaned_corpus = get_corpus_sentiment(copy.copy(cleaned_corpus))
    write_results_to_csv("corpus_plus_sentiment.csv", cleaned_corpus)
    # try removing "cancer" from corpus and re-create csv for analysis
    dummy_out_cancer_copy = dummy_out_cancer(dummy_out_cancer_copy)
    dummy_out_cancer_copy = get_corpus_sentiment(dummy_out_cancer_copy)
    write_results_to_csv("no_cancer_corpus_plus_sentiment.csv", dummy_out_cancer_copy)
    return

if __name__ == '__main__':
  main()