import csv
import re
import httplib
import urlparse
import time

#thanks to https://gist.github.com/jseidl/8192692

def unshorten_url(url):

    parsed = urlparse.urlparse(url)

    if parsed.scheme == 'https':
        h = httplib.HTTPSConnection(parsed.netloc)
    else:
        h = httplib.HTTPConnection(parsed.netloc)

    resource = parsed.path
    if parsed.query != "": 
        resource += "?" + parsed.query
    h.request('HEAD', resource )
    response = h.getresponse()
    if response.status/100 == 3 and response.getheader('Location'):
        return unshorten_url(response.getheader('Location')) # changed to process chains of short urls
    else:
        return url

def load_csv(filename):
    with open(filename, mode='rt') as f:
        lines = []
        reader = csv.reader(f,delimiter=",",quoting=csv.QUOTE_ALL)
        for row in reader:
            lines.append(row)
        return lines

def extract_links(downloaded_tweets):
    results = set([])
    time_idx = 1
    text_idx = 7
    t_co_shorten_len = 23
    start_idx = 2940 # failed: 1800, 2883, 2903, 2939
    for i in range(start_idx, len(downloaded_tweets)):
        tweet = downloaded_tweets[i]
        found = False
        time_fld = tweet[time_idx]
        text_fld = tweet[text_idx]
        matches = re.findall("(http|https|ftp|ftps)\:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(\/\S*)?", string=text_fld)
        if matches is not None:
            for match in matches:
                if not found:
                    shortened = match[0] + "://t.co" + match[1]
                    last_three = shortened.rstrip()[-3:]
                    if last_three == "...":
                        shortened = shortened[:-3]
                    if len(shortened) == t_co_shorten_len:
                        unwrapped = unshorten_url(shortened)
                        time.sleep(4)
                        if re.search("(\/news\/)", string=unwrapped) is not None:
                            time_link_tuple = (time_fld, unwrapped.rstrip())
                            results.add(time_link_tuple)
                            add_line_to_file(time_link_tuple)
                            found = True
        print("Finished line " + str(i + 1) + "of " + str(len(downloaded_tweets)))
    return results

def output_links(time_link_tuples):
    with open("linktime.txt", mode="wt") as f:
        for tuple in time_link_tuples:
            f.write(tuple[0] + ", " + tuple[1] + "\n")
    return

def add_line_to_file(time_link_tuple):
    with open("linktime_prog.txt", mode="a") as f:
        f.write(time_link_tuple[0] + ", " + time_link_tuple[1] + "\n")

def main():
    filename = "downloadedTweets.csv"
    pokemans = load_csv(filename)
    extracted_links = extract_links(pokemans)
    output_links(extracted_links)
    return

main()