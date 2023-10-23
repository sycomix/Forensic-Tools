#!/usr/bin/env python
import sqlite3, os, sys, platform
from datetime import datetime as dt


def time_to_epoch(time_string):
    '''Convert a YY_MM_DD_HH_MM_SS formatted date time string to unix timestamp'''
    tm = [int(item) for item in time_string.split("_")]
    return dt(tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]).timestamp()

def get_firefox_db(db_file):
    '''Return the full path of firefox sqlite databases, platform independent'''
    success = False
    plat_dict = {
        "Windows 7": r"C:\Users\%s\AppData\Roaming\Mozilla\Firefox\Profiles"
        % os.getlogin(),
        "Windows XP": r"C:\Documents and Settings\%s\Application Data\Mozilla\Firefox\Profiles"
        % os.getlogin(),
        "Linux": f"/home/{os.getlogin()}/.mozilla/firefox/",
        "Darwin": f"/Users/{os.getlogin()}/Library/Application Support/Firefox/Profiles",
    }
    if platform.system() == "Windows":
        string = plat_dict[f"{platform.system()} {platform.release()}"]
    else:
        string = plat_dict[platform.system()]
    for item in os.listdir(string):
        if os.path.isdir(os.path.join(string, item)) and "default" in item:
            if os.path.isfile(os.path.join(string, item, db_file)):
                success = True
                return os.path.join(string, item, db_file)
    if not success:
        sys.exit("Couldn't find the database file in the default location! Try providing a different location using the -b option...")

def getFileName(full_path):
    '''Get the file name from a string that might or might not contain the full path'''
    x = 0
    for i in range(len(full_path)):
        if full_path[i] in ("\\", "/"):
            x = i

    if any(char in full_path for char in ("\\", "/")):
        x += 1
    return full_path[x:]

def parse_value(value, integer=False, div=1):
    try:
        ret_val = "Not Applicable" if value == "" or not value else str(value)
        return "%.2f" % (int(value) / div) if integer else ret_val
    except:
        return "Not Applicable"

def saveResult(file_name, data):
    '''Save whatever data the scripts produce to a file...'''
    if os.path.isfile(file_name):
        sys.exit(
            f"{file_name} already exists! Rename or move that file to avoid losing your data!"
        )

    print("saving results to %s\n" % file_name)
    try:
        with open(file_name, "w", encoding='utf-8') as rf:
            rf.write(data)
    except IOError as ie:
        print(f"Could not save the result... An IOError occured: {ie}")
    print("done! Results saved to %s...\n" % file_name)

def pull_from_db(db, command, facebook_name=False):
    '''Send queries to a database and return the results'''
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute(command)
        return c.fetchall()
    except Exception as e:
        if facebook_name:
            return [(f"Name Unavailable {e}", )]
        else:
            sys.exit(f"Error reading the database: {e}")

def init_data(title, size):
    '''Generate static html with a time code and an appropriate title'''
    now = dt.now()
    try:
        with open(r"./templates/init_static_html.html") as tf:
            data = tf.readlines()

        data[1] = data[1] % title
        data[-1] = data[-1] % (now.year, now.month, now.day, now.hour, now.minute, now.second, size)
        return "".join(data)
    except IOError:
        sys.exit("Couldn't find the template file. Make sure the (unmodified) templates directory is " \
                 + "in the same directory as the script and try again...")

def init_table_header(template_file):
    '''Get the html table header from a given template file'''
    try:
        with open(template_file) as tf:
            data = tf.read()
        return data
    except IOError:
        sys.exit(
            f"Couldn't find the template file: {template_file}. Make sure the (unmodified) templates directory is in the same directory as the script and try again..."
        )

def parse_timestamp(tm_stmp):
    try:
        ret_val = dt.fromtimestamp(tm_stmp/1000).ctime()
    except:
        ret_val = "Not Applicable"
    return ret_val


def close_table_html():
    '''Close html tags'''
    return "</tbody></table></center></body></html>"
