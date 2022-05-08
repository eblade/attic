from typing import List, Optional
from itertools import groupby
from fastapi import FastAPI, Request, Depends, HTTPException, Form, status, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from rth.state import State
from rth.chain import Chain

app = FastAPI()
app.mount("/static", StaticFiles(directory="rth/static"), name="static")

templates = Jinja2Templates(directory='rth/templates')

state = State()
state.load_categories('rth/data/categories')
state.load_things('rth/data/things')

cp = open('chain', 'r+', encoding='utf8')
chain = Chain(state, cp)
chain.load_previous()

with open('token', 'r') as tp:
    security_token = tp.read().strip()


def check_token(token: str):
    if token != security_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return token


@app.get('/{token}/cat')
def read_cat(token: str = Depends(check_token)):
    return state.categories


@app.get('/{token}/things')
def read_things(token: str = Depends(check_token)):
    return state.things


@app.get('/{token}/count')
def read_count(token: str = Depends(check_token)):
    return state.counts


@app.get('/{token}/list')
def read_list(token: str = Depends(check_token)):
    things_with_count = [(thing, count) for thing, count in state.counts.items() if count > 0]
    result = []
    for thing, count in things_with_count:
        cat = state.things[thing]
        comments = state.comments.get(thing, [])
        result.append((cat, thing, count, comments))
    result.sort()
    return {
        'items': [{
            'cat': cat,
            'thing': thing,
            'count': count,
            'comments': comments,
        } for cat, thing, count, comments in result]
    }


@app.put('/{token}/list/{thing}')
def check_item(thing: str, token: str = Depends(check_token)):
    chain.add_thing(thing)


@app.delete('/{token}/list/{thing}')
def uncheck_item(thing: str, token: str = Depends(check_token)):
    chain.remove_thing(thing)


@app.post('/{token}/list/{thing}')
def comment_item(thing: str, comment: str, token: str = Depends(check_token)):
    chain.comment(thing, comment)


@app.get('/{token}/index.html', response_class=HTMLResponse)
async def index_html(request: Request,
                     check: Optional[List[str]] = Query(None),
                     uncheck: Optional[List[str]] = Query(None),
                     token: str = Depends(check_token)):
    if check is not None:
        print("Checking", check)
        for thing, count in map(lambda x: x.split('^', 1), check):
            chain.remove_thing(thing, current_count=int(count))

    if uncheck is not None:
        print("Unchecking", uncheck)
        list(map(chain.add_thing, uncheck))
    return templates.TemplateResponse('index.html', {
        'request': request,
        'token': token,
        'items': read_list(token)['items']})

@app.get('/{token}/select.html', response_class=HTMLResponse)
async def select_html(request: Request, token: str = Depends(check_token)):
    things_with_count = set(thing for thing, count in state.counts.items() if count > 0)
    groups = groupby(sorted((cat, thing) for thing, cat in state.things.items()), lambda x: x[0])

    return templates.TemplateResponse('add.html', {
        'request': request,
        'token': token,
        'cats': [{'name': state.categories[g[0]], 'items': list(item[1] for item in g[1])} for g in groups]})

@app.on_event('shutdown')
def on_shutdown():
    cp.close()
