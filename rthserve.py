import os
import logging
from typing import List, Optional
from itertools import groupby
from fastapi import FastAPI, Request, Depends, HTTPException, Form, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
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

with open('token', 'r') as tp:
    security_token = tp.read().strip()

logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'rthserve-{security_token}.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s')

cp = open('chain', 'r+', encoding='utf8')
chain = Chain(state, cp)
chain.load_previous()


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


def get_items(checked: bool):
    cat_orders = {key: n for n, (key, _) in enumerate(state.categories.items())}
    groups = groupby(sorted((cat_orders[cat], cat, thing) for thing, cat in state.things.items() if checked ^ (thing in state.unchecked)), lambda x: x[1])
    return {'cats': [{
        'name': state.categories[g[0]],
        'short': g[0],
        'items': list({
            'thing': thing,
            'comment': state.comments.get(thing, None)
            } for _, cat, thing in g[1])
        } for g in groups
    ]}


def get_item(thing):
    return {
        'thing': thing,
        'comment': state.comments.get(thing, None)
    }


@app.get('/{token}/list')
def read_list(token: str = Depends(check_token)):
    return get_items(False)


@app.put('/{token}/list/{thing}')
def check_item(thing: str, token: str = Depends(check_token)):
    chain.add_thing(thing)


@app.delete('/{token}/list/{thing}')
def uncheck_item(thing: str, token: str = Depends(check_token)):
    chain.remove_thing(thing)


@app.post('/{token}/list/{thing}')
def comment_item(thing: str, comment: str, token: str = Depends(check_token)):
    chain.comment(thing, comment)


@app.get('/{token}', response_class=HTMLResponse)
async def index_without_index_html(token: str = Depends(check_token)):
        return RedirectResponse(f'/{token}/index.html')


@app.get('/{token}/index.html', response_class=HTMLResponse)
async def index_html(request: Request,
                     check: Optional[List[str]] = Query(None),
                     uncheck: Optional[List[str]] = Query(None),
                     thing: Optional[str] = Query(None),
                     comment: Optional[str] = Query(None),
                     token: str = Depends(check_token)):

    changed = False

    if check is not None:
        list(map(chain.remove_thing, check))
        changed = True

    if uncheck is not None:
        list(map(chain.add_thing, uncheck))
        changed = True

    if comment is not None and thing is not None:
        chain.comment(thing, comment)
        changed = True

    if changed:
        return RedirectResponse('index.html')

    return templates.TemplateResponse('index.html', {
        'request': request,
        'token': token,
        'cats': get_items(False)['cats']})


@app.get('/{token}/select.html', response_class=HTMLResponse)
async def select_html(request: Request, token: str = Depends(check_token)):
    return templates.TemplateResponse('select.html', {
        'request': request,
        'token': token,
        'cats': get_items(True)['cats']})


@app.get('/{token}/{thing}/comment.html', response_class=HTMLResponse)
async def comment_html(request: Request, thing: str, token: str = Depends(check_token)):
    return templates.TemplateResponse('comment.html', {
        'request': request,
        'token': token,
        'item': get_item(thing)})


@app.on_event('shutdown')
def on_shutdown():
    cp.close()
