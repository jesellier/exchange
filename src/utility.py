# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 19:07:57 2021

@author: jesel
"""

import bisect 


def bisect_left(l, e, lo=None, hi=None, order="ASC"):
    """Find first index, starting from left, to insert e."""
    lo = lo or 0
    hi = hi or len(l)
    if order not in ("ASC", "DESC"):
        raise ValueError('order must either be asc or desc.')
    if order == "ASC":
        return bisect.bisect_left(l, e, lo, hi)
    return len(l) - bisect.bisect_right(l[::-1], e, lo, hi)


def bisect_right(l, e, lo=None, hi=None, order="ASC"):
    """Find first index, starting from right, to insert e."""
    lo = lo or 0
    hi = hi or len(l)
    if order not in ("ASC", "DESC"):
        raise ValueError('order must either be asc or desc.')
    if order == "ASC":
        return bisect.bisect_right(l, e, lo, hi)
    return len(l) - bisect.bisect_left(l[::-1], e, lo, hi)

