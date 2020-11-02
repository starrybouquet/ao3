import os
import sys
import random
import urllib.parse
import time

import markovify
import json
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath('..'))

import ao3
from ao3.utils import work_id_from_url
from ao3.works import Work

api = ao3.AO3()

def add_work_to_chain(work, models, state_size=3):
    '''adds new Markov chain model of work
    with given ID to the dict models and returns said dict'''
    text = work.get_work_text()
    model = markovify.Text(text, state_size=state_size)
    models[id] = model
    print('Added work {} to models.'.format(work.title))

    return models

def combine_models(models, weights=None):
    if not weights:
        model = markovify.combine(list(models.items()))
    else:
        model = markovify.combine(list(models.items()), weights)
    return model.compile()

def create_model():

    models = {} # each entry is id: model
    ids = []

    # addingIDs = True
    # while addingIDs == True:
    #     url = str(input('Enter url here, or q if you are finished adding urls: '))
    #     if url == 'q':
    #         addingIDs = False
    #     else:
    #         try:
    #             id = work_id_from_url(url)
    #             ids.append(id)
    #             models = add_work_to_chain(id, models)
    #         except Exception as e:
    #             print('ID {} was invalid with the following error: '.format(id))
    #             print(e)
    #             input('Hit Enter to continue')

    # api.login('starrybouquet')
    # data = api.user.bookmarks(load=False)
    # with open('data.txt', 'w') as f:
    #     for id, html in data.items():
    #         f.write("{0}\n{1}".format(id, html))
    with open('data.txt', 'r') as f:
        raw_data = f.readlines()

    bookmark_data = {}
    in_bookmark = False
    ending_bookmark = False
    current_id = '3413384'
    current_data = ''
    for line in raw_data:
        if ending_bookmark:
            print('Bookmark is ending')
            ending_bookmark = False
            parts = line.partition('>')
            current_data += parts[0]
            current_data += parts[1]
            print('Partitioned line: {}'.format(parts))
            bookmark_data[current_id] = current_data # add tag to dict
            print('Assigned current data to id {}'.format(current_id))
            current_id = parts[2].strip() # assign next id
            print('Assigned next id as {}'.format(current_id))
            current_data = ''
        else:
            current_data += line
            if '<div class="recent dynamic"' in line:
                ending_bookmark = True
                print('Turned on ending bookmark')
    print(bookmark_data['26777875'])
    input()
    all_works = []
    for id, html in bookmark_data.items():
        soup = BeautifulSoup(html, 'html.parser')
        all_works.append(Work(id, api.handler, load=False, soup=soup))

    possible_tags = set(['Samantha "Sam" Carter/Jack O\'Neill', 'Jack/Sam', 'Sam/Jack', 'Sam Carter/Jack O\'Neill'])
    matching_works = []
    for work in all_works:
        ship = set(work.relationship)
        print('Ship tags: {}'.format(work.relationship))
        intersection = possible_tags.intersection(ship)
        print('Intersection: {}'.format(intersection))
        if len(intersection) > 0:
            matching_works.append(work)
            print('Appended work')
    print('Works matching tags: ')
    print(len(matching_works))
    print(matching_works)
    input('Press Enter to continue: ')
    print()
    models_built = 0
    for work in matching_works:
        if models_built % 20 == 0:
            print('{} models built, sleeping 3 min'.format(models_built))
            time.sleep(180)
        models = add_work_to_chain(id, models)
        models_built += 1

    full_model = combine_models(models)
    num_sentences = int(input('Enter # of sentences to try: '))
    for i in range(num_sentences):
        print(full_model.make_sentence())

    save = str(input('Do you want to save this model? y or n: '))
    if save == 'y':
        filename = str(input('Enter filename to save: '))
        json_model = full_model.to_json()
        with open(filename, 'w') as f:
            json.dump(json_model, f)
        print('Saved file. IDs used were:')
        print(ids)

create_model()
