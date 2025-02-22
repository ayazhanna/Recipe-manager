import os
import requests
import sqlite3
import numpy as np

from flask import redirect, session, request
from functools import wraps
from typing import Any, List

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# Functions
def database(db="weba0.db"):
    con = sqlite3.connect(db)
    cur = con.cursor()
    return con, cur

def split_dict(dct, sections):
    lst = sorted(list(dct.items()))
    split_lst = np.array_split(lst, sections)
    splitted = []
    for i in range(sections):
        sec_i = split_lst[i]
        splitted.append(dict(sec_i))
    return splitted


def stringify(list_name, string):
    list = request.args.getlist(list_name)
    arr = []
    for l in list:
        arr.append(string + l)
    stringified = "".join(arr)
    return list, stringified



def readable_list(seq: List[Any]) -> str:
    seq = [str(s) for s in seq]
    if len(seq) < 3:
        return ' and '.join(seq)
    return ', '.join(seq[:-1]) + ', and ' + seq[-1]