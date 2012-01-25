#!/usr/bin/env python
from glob import glob
from mako.template import Template
from mako.lookup import TemplateLookup
from sys import argv
from os import unlink, mkdir, listdir, getcwd, pardir
from os.path import join, isdir, split
from shutil import copytree, rmtree
from subprocess import Popen, PIPE
from yaml import load
from operator import itemgetter

def clean():
    if isdir("build/js"):
        rmtree("build/js")

    for f in glob("build/*.html"): unlink(f)

def build():
    if not isdir("build"):
        mkdir("build")
    # copy the javascript library
    copytree("js", "build/js")

    def required(page, required_vars):
        for var in required_vars: page[var] = page.get(var, "")

    for book_path in glob("books/*"):
        print book_path
        book_name = book_path.split('/')[1]

        output_path = join("build", book_name)
        if not isdir(output_path):
            mkdir(output_path)

        chapters = [load(file(c)) for c in glob(join(book_path, "*.yaml"))]

        pages = []
        toc = []
        for chapter in sorted(chapters, key=itemgetter('order')):

            chapter["output_file_name"] = "%s.html" % chapter["name"]
            pages.append(chapter)
            toc.append((chapter["title"], chapter["output_file_name"]))

            required(chapter, ["code", "explain_before", "explain_after", 
                               "title", "hidden_code", "library"])

        for i, page in enumerate(pages):
            page["prev"] = pages[i-1]["name"] if i > 0 else ""
            page["next"] = pages[i+1]["name"] if i+1 < len(pages) else ""
            page["toc"]  = toc
            page["book_name"] = book_name

            output_file = file(join(output_path, page["output_file_name"]), 'w')
            output_file.write(
                 Template(filename="templates/template.mak",
                          lookup=TemplateLookup(directories=['.'])).render(**page))

def deploy():
    print "deploying"
    for f in ['build/*.html', 'js']:
        cmd = "rsync -avuz -e ssh %s llimllib@billmill.org:~/static/canvastutorial" % f
        p = Popen(cmd, shell=True, stderr=PIPE)

if __name__ == "__main__":
    clean()
    build()
    if argv[-1].lower() == "deploy":
        deploy()
