#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module gvpy.time with time conversion functions. A few of these also still live in io.py for backwards compatibility.
"""

import datetime
import numpy as np
import pandas as pd
import xarray as xr


def mtlb2datetime(
    matlab_datenum, strip_microseconds=False, strip_seconds=False
):
    """
    Convert Matlab datenum format to python datetime.

    This version also works for vector input and strips
    milliseconds if desired.

    Parameters
    ----------
    matlab_datenum : float or np.array
        Matlab time vector.
    strip_microseconds : bool
        Get rid of microseconds (optional)
    strip_seconds : bool
        Get rid of seconds (optional)

    Returns
    -------
    t : np.datetime64
        Time in numpy's datetime64 format.
    """

    if np.size(matlab_datenum) == 1:
        day = datetime.datetime.fromordinal(int(matlab_datenum))
        dayfrac = datetime.timedelta(days=matlab_datenum % 1) - datetime.timedelta(days=366)
        t1 = day + dayfrac
        if strip_microseconds and strip_seconds:
            t1 = datetime.datetime.replace(t1, microsecond=0, second=0)
        elif strip_microseconds:
            t1 = datetime.datetime.replace(t1, microsecond=0)

    else:
        t1 = np.ones_like(matlab_datenum) * np.nan
        t1 = t1.tolist()
        nonan = np.isfinite(matlab_datenum)
        md = matlab_datenum[nonan]
        day = [datetime.datetime.fromordinal(int(tval)) for tval in md]
        dayfrac = [
            datetime.timedelta(days=tval % 1) - datetime.timedelta(days=366) for tval in md
        ]
        tt = [day1 + dayfrac1 for day1, dayfrac1 in zip(day, dayfrac)]
        if strip_microseconds and strip_seconds:
            tt = [
                datetime.datetime.replace(tval, microsecond=0, second=0)
                for tval in tt
            ]
        elif strip_microseconds:
            tt = [datetime.datetime.replace(tval, microsecond=0) for tval in tt]
        tt = [np.datetime64(ti) for ti in tt]
        xi = np.where(nonan)[0]
        for i, ii in enumerate(xi):
            t1[ii] = tt[i]
        xi = np.where(~nonan)[0]
        for i in xi:
            t1[i] = np.datetime64("nat")
        t1 = np.array(t1)

    return t1


def datetime2mtlb(dt):
    """Convert numpy datetime64 time format to Matlab datenum time format.

    Parameters
    ----------
    dt : array-like
        Time or time vector in numpy datetime64 time format.

    Returns
    -------
    dtnum : array-like
        Time in Matlab datenum format.
    """
    pt = pd.to_datetime(dt)
    dt = pt.to_pydatetime()
    mdn = dt + datetime.timedelta(days=366)
    frac_seconds = [
        (dti - datetime.datetime(dti.year, dti.month, dti.day, 0, 0, 0)).seconds
        / (24.0 * 60.0 * 60.0)
        for dti in dt
    ]
    frac_microseconds = [
        dti.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0) for dti in dt
    ]
    out = np.array([mdni.toordinal() for mdni in mdn])
    out = out.astype(float) + frac_seconds + frac_microseconds
    return out


def sbetime_to_mattime(sbetime):
    """Convert SBE time format to Matlab datenum time format.

    Parameters
    ----------
    sbetime : array-like
        Time or time vector in SBE time format.

    Returns
    -------
    dtnum : array-like
        Time in Matlab datenum format.
    """
    dtnum = sbetime / 24 / 3600 + 719529
    return dtnum


def mattime_to_sbetime(dtnum):
    """Convert Matlab datenum time format to SBE time format.

    Parameters
    ----------
    dtnum : array-like
        Time in Matlab datenum format.

    Returns
    -------
    sbetime : array-like
        Time or time vector in SBE time format.
    """
    sbetime = (dtnum - 719529) * 24 * 3600
    return sbetime


def mattime_to_datetime64(dnum):
    """Convert Matlab datenum time format to numpy's datetime64 format.

    Parameters
    ----------
    dtnum : array-like
        Time in Matlab datenum format.

    Returns
    -------
    time : np.datetime64
        Time in numpy datetime64 format

    Notes
    -----
    In Matlab, datevec(719529) = [1970 1 1 0 0 0]
    """
    time = pd.to_datetime(dnum-719529, unit='D')
    return time


def datevec_to_datetime64(dv):
    def vec2str(dv):
        return f'{dv[0]:02.0f}-{dv[1]:02.0f}-{dv[2]:02.0f} {dv[3]:02.0f}:{dv[4]:02.0f}:{dv[5]:02.0f}'
    if isinstance(dv, list):
        dtstr = [vec2str(dvi) for dvi in dv]
        time = np.array([str_to_datetime64(ti) for ti in dtstr])
    else:
        dtstr = vec2str(dv)
        time = str_to_datetime64(dtstr)
    return time


def str_to_datetime64(timestr):
    """
    Convert date/time in str format to numpy's datetime64 format.

    Makes intermediate use of pandas datetime format, their string
    conversion seems to be much more capable than numpy's.

    Parameters
    ----------
    timestr : str
        Date/time

    Returns
    -------
    time : np.datetime64
        Time in numpy datetime64 format
    """
    return pd.to_datetime(timestr).to_datetime64()


def yday1_to_datetime64(baseyear, yday):
    """
    Convert year day (starting at yday 1) to numpy's datetime64 format.

    Parameters
    ----------
    baseyear : int
        Base year
    yday : float
        Year day

    Returns
    -------
    time : np.datetime64
        Time in numpy datetime64 format
    """
    base = datetime.datetime(baseyear, 1, 1, 0, 0, 0)
    time = [base + datetime.timedelta(days=ti) for ti in yday - 1]
    # convert to numpy datetime64
    time64 = np.array([np.datetime64(ti, "ms") for ti in time])
    return time64


def yday0_to_datetime64(baseyear, yday):
    """
    Convert year day (starting at yday 0) to numpy's datetime64 format.

    Parameters
    ----------
    baseyear : int
        Base year
    yday : float
        Year day

    Returns
    -------
    time : np.datetime64
        Time in numpy datetime64 format
    """
    base = datetime.datetime(baseyear, 1, 1, 0, 0, 0)
    time = [base + datetime.timedelta(days=ti) for ti in yday]
    # convert to numpy datetime64
    time64 = np.array([np.datetime64(ti, "ms") for ti in time])
    return time64

    """
    Check if string can be converted to a float.

    Parameters
    ----------
    s : str
        string

    Returns
    -------
    out : bool
        True if string can be converted to float, else False.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

    return t1


def convert_units(t, unit='s'):
    if type(t) == xr.DataArray:
        torig = t.copy()
        xa = True
        t = t.data
    else:
        xa = False

    data_type = type(t)
    if data_type == list:
        t0 = t[0]
        t_type = type(t0)
        if t_type == np.datetime64:
            tfun = np.datetime64
        elif t_type == np.timedelta64:
            tfun = np.timedelta64
    elif data_type == np.ndarray:
        if t.dtype == '<M8[ns]':
            tfun = np.datetime64
        elif t.dtype == '<m8[ns]':
            tfun = np.timedelta64
    else:
        t0 = t
        t_type = type(t0)
        if t_type == np.datetime64:
            tfun = np.datetime64
        elif t_type == np.timedelta64:
            tfun = np.timedelta64


    if data_type == np.ndarray and t.size > 1:
        out = np.array([tfun(ti, unit) for ti in t])
    elif data_type == np.ndarray and t.size == 1:
        out = tfun(t, unit)
    elif data_type == list:
        out = [tfun(ti, unit) for ti in t]
    elif data_type == np.datetime64 or data_type == np.timedelta64:
        out = tfun(t, unit)

    if xa:
        out = xr.DataArray(out, coords=torig.coords)

    return out


def datetime64_to_str(dt, strformat='%Y-%m-%d'):
    t = dt.astype(datetime.datetime)
    tstr = t.strftime(strformat)
    return tstr


def now_datestr():
    datestr = datetime64_to_str(np.datetime64(datetime.datetime.now()), strformat="%Y-%m-%d")
    return datestr
