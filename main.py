from chatbot import Chatbot, log

import datetime
import html
import re
import requests
import time

import stackapi

ROOMS = [120733]
DEBUG = False

CGCC = stackapi.StackAPI('codegolf.meta', key = '0lYaLshi5yEGuEcK3ZxYHA((')
HTML_search = re.compile(r'<a href="/questions/2140/sandbox-for-proposed-challenges/(\d+)\?r=SearchResults#\1"')
TITLE1_search = re.compile(r'<h1> *(.*?) *</h1>')
TITLE2_search = re.compile(r'<h2> *(.*?) *</h2>')
EMPTY_LINK = '[{}](https://codegolf.meta.stackexchange.com/a/{})'

SEARCH_URLS = ['https://codegolf.meta.stackexchange.com/search?q=inquestion%3A2140+lastactive%3A{}+score%3A0..+',
               'https://codegolf.meta.stackexchange.com/search?q=inquestion%3A2140+created%3A{}+score%3A0..+']

HTML_REPLACES = {

        'strong': '**',
        'em': '*',
        'code': '`'

}

POST_TIME = datetime.time(
        1, # hour
        0, # minute
        0, # second
)

if DEBUG:
        POST_TIME = (datetime.datetime.now() + datetime.timedelta(seconds = 5)).time()

def ignore_msgs(*arguments):
        return None

def search(url):
        a_week = datetime.timedelta(days = 7)
        today = datetime.datetime.utcnow()
        week_ago = (today - a_week).strftime('%Y-%m-%d')
        query = url.format(week_ago)

        req = requests.get(query)
        proposal_urls = HTML_search.findall(req.text)

        return proposal_urls

def get_posts(choose = 'both'):
        post_ids = [search(each_url) for each_url in SEARCH_URLS]

        if choose == 'create': return [post_ids[1]]
        if choose == 'active': return [post_ids[0] + ['22181', '22209']]
        
        return post_ids

def replace(string):
        for tag, markdown in HTML_REPLACES.items():
                string = re.sub(r'<{0}>(.*?)</{0}>'.format(tag), r'{0}\1{0}'.format(markdown), string)
        return string

def get_title(html_page):
        if '<h1>' in html_page: title = TITLE1_search.search(html_page).group(1)
        elif '<h2>' in html_page: title = TITLE2_search.search(html_page).group(1)
        else: title = '(untitled)'

        prev = title
        title = replace(title)
        while prev != title:
                prev = title
                title = replace(title)
        
        title = re.sub(r'<a href="https://codegolf.stackexchange.com/questions/tagged/.*? class="post-tag" title="show questions tagged .*?" rel="tag">(.*?)</a>', r'\[\1\]', title)
        title = re.sub(r'<a href.*?>(.*?)</a>', r'\1', title)
        title = re.sub(r'<span class="math-container">(.*?)</span>', r'\1', title)

        return html.unescape(title)

def not_posted(text):
        if len(text) <= 500:
                return False
        if re.search(r'<a href="https://codegolf.stackexchange.com/q(uestions)?/\d+.*?>posted</a>', text, re.I):
                return False
        if re.search(r'<h([12])><a href="https://codegolf.stackexchange.com/q(uestions)?/\d+.*?</a></h\1>', text):
                return False

        return True

def filter_posted():
        kept_posts = {'lastactive': [], 'c': [], 'created': []}
        gotten = get_posts(choose = 'active')
        keys = ('lastactive',)

        for search_type, array in zip(keys, gotten):
                
                if not array: continue
                
                posts = CGCC.fetch('posts/{ids}', ids = array, filter = 'withbody')
                
                for item in posts['items']:
                        if not_posted(item['body']):
                                kept_posts[search_type].append(
                                        [
                                                get_title(item['body']),
                                                item['post_id']
                                        ]
                                )

        for challenge in kept_posts['c']:
                if challenge not in kept_posts['lastactive']:
                        kept_posts['created'].append(challenge)

        del kept_posts['c']
        return kept_posts

def format_links(ids):
        return [EMPTY_LINK.format(title, post_id) for (title, post_id) in ids]

def get_msg():
        
        posts = filter_posted()
        indices = []
        index = 0
        
        messages = ['Sandbox posts last active a week ago: ',]

        if posts['lastactive']:
                links = format_links(posts['lastactive'])
                while links:
                        if len(messages[index] + links[0]) >= 499:
                                messages.append('Sandbox posts last active a week ago: ')
                                index += 1
                        messages[index] += links.pop(0) + ', '
        else:
                indices.append(index)
                        
        messages.append('Sandbox posts created a week ago: ')
        index += 1

        if posts['created']:
                links = format_links(posts['created'])
                while links:
                        if len(messages[index] + links[0]) >= 499:
                                messages.append('Sandbox posts created a week ago: ')
                                index += 1
                        messages[index] += links.pop(0) + ', '
        else:
                indices.append(index)

        sent = False

        for index, msg in enumerate(messages):
                if index not in indices:
                        sent = True
                        yield msg.rstrip(', ')

def time_until_post():
        post_at = datetime.datetime.combine(datetime.datetime.today(), POST_TIME)
        today = datetime.datetime.utcnow()
        return (post_at - today).seconds

def main(room_id):
        chatbot = Chatbot(decrypt = 'caird')
        chatbot.login()
        chatbot.joinRoom(room_id, ignore_msgs)
        
        for msg in get_msg():
                chatbot.rooms_joined[0].sendMessage(msg)

        chatbot.leaveAllRooms()
        return

if __name__ == '__main__':
        for room in ROOMS:
                main(room)
