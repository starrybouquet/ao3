import os
import sys
import random
import urllib.parse

import markovify
import json

sys.path.insert(0, os.path.abspath('..'))

import ao3
# from ao3.works import Work, iterate_pages

api = ao3.AO3()

def add_work_to_chain(id, models, state_size=3):
    '''adds new Markov chain model of work
    with given ID to the dict models and returns said dict'''
    work = ao3.work(id)
    text = work.get_work_text()

    model = markovify.Text(text, state_size=state_size)
    models[id] = model

    return models

def combine_models(models, weights=None):
    if not weights:
        model = markovify.combine(models.items())
    else:
        model = markovify.combine(models.items(), weights)
    return model.compile()

def create_model():

    models = {} # each entry is id: model
    ids = []

    addingIDs = True
    while addingIDs == True:
        id = str(input('Enter ID here, or q if you are finished adding IDs: '))
        if id == 'q':
            addingIDs = False
        else:
            try:
                ids.append(id)
                models = add_work_to_chain(id, models)
            except Exception as e:
                print('ID {} was invalid with the following error: '.format(id))
                print(e)
                input('Hit Enter to continue')

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
