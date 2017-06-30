# -*- coding: utf-8 -*-
#
#    This file belongs to the Interactive Syllabus project
#
#    Copyright (C) 2017  Alexandre Dubray, François Michel
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.



import os
from flask import Flask, render_template, request
import syllabus.utils.pages, syllabus.utils.directives
from syllabus.utils.pages import get_syllabus_toc, get_chapter_content
from docutils.core import publish_string
from syllabus.config import *
from docutils.parsers.rst import directives

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
directives.register_directive('inginious', syllabus.utils.directives.InginiousDirective)
directives.register_directive('table-of-contents', syllabus.utils.directives.ToCDirective)
directives.register_directive('author', syllabus.utils.directives.AuthorDirective)


@app.route('/')
@app.route('/index')
def index():
    toc = syllabus.get_toc()
    return render_template('rst_page.html',
                           inginious_url="http://%s:%d" % (inginious_instance_hostname, inginious_instance_port),
                           chapter="", page="index", render_rst=syllabus.utils.pages.render_page,
                           structure=get_syllabus_toc("pages"), list=list,
                           toc=toc,
                           chapter_content=None, next=None, previous=None)


@app.route('/<chapter>')
def chapter_index(chapter):
    return render_web_page(chapter, None)


@app.route('/<chapter>/<page>')
@syllabus.utils.pages.sanitize_filenames
def get_page(chapter, page):
    return render_web_page(chapter, page)


def render_web_page(chapter, page):
    toc = syllabus.get_toc()
    # find previous/next page/chapter
    if page is None:
        # find previous/next chapter
        chapters = list(toc.keys())
        chapter_index = chapters.index(chapter)
        previous = None if chapter_index == 0 else chapters[chapter_index - 1]
        next = None if chapter_index == len(chapters) - 1 else chapters[chapter_index + 1]
    else:
        # find previous/next page
        pages = list(toc[chapter]["content"].keys())
        page_index = pages.index(page)
        previous = None if page_index == 0 else pages[page_index - 1]
        next = None if page_index == len(pages) - 1 else pages[page_index + 1]
    return render_template('rst_page.html',
                           inginious_url="http://%s:%d" % (inginious_instance_hostname, inginious_instance_port),
                           chapter=chapter, page=page, render_rst=syllabus.utils.pages.render_page,
                           toc=toc,
                           chapter_content=get_chapter_content(chapter, toc), next=next, previous=previous)


@app.route('/parserst', methods=['POST'])
def parse_rst():
    inpt = request.form["rst"]
    out = publish_string(inpt, writer_name='html')
    return out


def main():
    app.run()
