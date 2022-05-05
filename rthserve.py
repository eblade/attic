from fastapi import FastAPI, Depends, HTTPException, status

from rth.state import State
from rth.chain import Chain

app = FastAPI()

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
    return 'ok'


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
    things_with_count = [thing for thing, count in state.counts.items() if count > 0]
    result = []
    for thing in things_with_count:
        cat = state.things[thing]
        comments = state.comments.get(thing, [])
        result.append((cat, thing, comments))
    result.sort()
    return {
        'list': [{
            'cat': cat,
            'thing': thing,
            'comments': comments,
        } for cat, thing, comments in result]
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


@app.on_event('shutdown')
def on_shutdown():
    cp.close()
