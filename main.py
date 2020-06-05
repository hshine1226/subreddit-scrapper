import requests, os
from flask import Flask, render_template, request
from bs4 import BeautifulSoup

os.system("clear")
"""
When you try to scrape reddit make sure to send the 'headers' on your request.
Reddit blocks scrappers so we have to include these headers to make reddit think
that we are a normal computer and not a python script.
How to use: requests.get(url, headers=headers)
"""

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}


"""
All subreddits have the same url:
i.e : https://reddit.com/r/javascript
You can add more subreddits to the list, just make sure they exist.
To make a request, use this url:
https://www.reddit.com/r/{subreddit}/top/?t=month
This will give you the top posts in per month.
"""

subreddits = [
    "javascript",
    "reactjs",
    "reactnative",
    "programming",
    "css",
    "golang",
    "flutter",
    "rust",
    "django"
]

db = {}

def get_subreddit(readingList):
    results = []
    for subreddit in readingList:        
        if db.get(subreddit):
            results.append(db[subreddit])
        else:
            url = f"https://www.reddit.com/r/{subreddit}/top/?t=month"
            r = requests.get(url, headers=headers)
            html_doc = r.content
            soup = BeautifulSoup(html_doc, 'html.parser')
            blocks = soup.find_all("div", class_="_1oQyIsiPHYt6nx7VOmd1sz")
            reddits = []
            for block in blocks:
                if not 'promotedlink' in block['class']:
                    vote = block.find("div", class_="_23h0-EcaBUorIHC-JZyh6J").find("div", class_="_1rZYMD_4xY3gRcSS3p8ODO").string
                    title = block.find("h3", class_="_eYtD2XCVieq6emjKBH3m").string
                    link = block.find("a", class_="SQnoC3ObvgnGjWt90zD9Z")['href']
                    reddit = {"subreddit": subreddit, "title": title, "vote": vote, "link": f"https://www.reddit.com{link}"}
                    reddits.append(reddit)
            results.append(reddits)
            db[subreddit] = reddits
    return results
        

app = Flask("DayEleven")


@app.route("/")
def home():
    return render_template("home.html", subreddits=subreddits)


@app.route("/read")
def read():
    readingList = []
    for subreddit in subreddits:
        if request.args.get(subreddit) == "on":
            readingList.append(subreddit)
    
    results = get_subreddit(readingList)

    return render_template("read.html", readingList=readingList, results=results)


@app.route("/add", methods=["POST"])
def add():
    added = request.form['subreddit']
    if "/r/" in added :
        return render_template("add.html", result="has_r")
    else:
        if added in subreddits:
            return render_template("add.html", result="already")
        else:
            aa = get_subreddit([added])
            if aa == [[]]:
                return render_template("add.html", result="no_exist")
            else:
                subreddits.append(added)
                return render_template("home.html", subreddits=subreddits) 

app.run(host="0.0.0.0")