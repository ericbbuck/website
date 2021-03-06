from flask import Flask, render_template, url_for, render_template_string, Markup, redirect
from flask_flatpages import FlatPages, pygmented_markdown
# from flask_bootstrap import Bootstrap
from flask_frozen import Freezer

from datetime import datetime
import sys
import subprocess
import os
import time


# Config to ensure 
# Pages are loaded on request
# File name extension for pages is Markdown

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'

app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)
freezer = Freezer(app)

# Allows markdown to do flask functions before the site's HTML renders. INTEGRAL. SO IMPORTANT.
def prerender_jinja(text):
    prerendered_body = render_template_string(Markup(text))
    return pygmented_markdown(prerendered_body)
app.config['FLATPAGES_HTML_RENDERER'] = prerender_jinja

def dateconvert(str):
    return str.strftime("%B %d, %Y")
app.jinja_env.globals.update(dateconvert=dateconvert)

#About Page
@app.route('/')
def index(): 
    return render_template('index.html',pages=pages)

@app.route("/blog/")
def mainblog():
    print("main blog page")
    blogPages = [p for p in pages if "blog"==p.meta.get('label')]
    blogPages = [(x.meta.get('date'), x) for x in blogPages if 'wip' not in x.meta.get('tags')]

    blogPages.sort(reverse=True, key= lambda x: x[0])
    blogPages=[x[1] for x in blogPages]
    return render_template('blogmain.html', page=[], pages=blogPages)

@app.route("/blog/<string:title>/")
def blog(title):
    print("blog page " + title)
    page = [pages.get("blog/" + title)]
    blogPages = [p for p in pages if "blog"==p.meta.get('label')]


    if page[0] is None:
        return mainblog()
    return render_template('blog.html', page=page, pages = blogPages)


#Tag Route for tag.html
@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', pages=tagged, tag=tag)

@app.route('/tagged/')
def maintag():
    print("main tagged page")
    listPages = set()
    numPages = dict()

    allTag = []
    # For all blog posts,
    for p in pages:
        if ("blog"==p.meta.get('label')):
            for t in p.meta.get('tags', []):
                listPages.add(t)
                numPages[t] = numPages.get(t, 0) + 1
                allTag.append(t)

    listPages = sorted(list(listPages))
    numPages = [numPages[x] for x in listPages]
    return render_template('tagmain.html', pages=listPages, num_per_tag=numPages)

#URL Routing - Flat Pages; Retrieves page path
@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    return render_template('page.html', page=page)

#Main Function runs at http://0.0.0.0:8000
#if __name__ == "__main__":
 #   if len(sys.argv) > 1 and sys.argv[1] == "build":
        #Builds into static site and runs 'firebase dreloy' 
  #  else:
   #     app.run(port=8000)
 ##
 #Deploy to firebase
 ##

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        # Builds the website into a static site and runs "firebase deploy" to update the site
        #f len(sys.argv) > 2 and sys.argv[2] == "local":
            # turn off DEBUG
            DEBUG = False

            # Download all files in the static folder
            #for icloud_file in [x for x in os.listdir("static/") if ".icloud" in x]:
               # os.system("brctl download static/" + icloud_file)

            # wait for them to download
            #print("waiting for static resources to download from icloud", end="")
            #while (len([x for x in os.listdir("static/") if ".icloud" in x]) > 0):
                #time.sleep(1)
                #print(".", end="")


            # PLEASE DO NOT RUN "python sitebuilder.py build local" IF YOU ARE NOT ON ANDY'S MAC
            app.config["FREEZER_DESTINATION"] = "ericbuck.org/public"
            freezer.freeze()

            # Push everything to github
            #os.system("git stage -A")
           # os.system("git commit -m \"blog update " + time.ctime() + "\"")
            #os.system("git push origin master")

            # Deploy build file to firebase
            #os.system("(cd build && firebase deploy)")
        
    else:
        app.run(port=8000)