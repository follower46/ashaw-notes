## Description

[![Build Status](https://travis-ci.org/follower46/ashaw-notes.svg?branch=master)](https://travis-ci.org/follower46/ashaw-notes)

ashaw-notes was created to allow for quick and easy note taking and retrieval of information and personal context.
With a keen focus on speed of entry and filtering, ashaw-notes allows quick overviews of the previous day, month, and year for time tracking or simple daily standup updates.

Rewritten completely in python 3 (originally a php application), this application supports:
* Multiple backends (flat text file or Redis datastore)
* Note CRUD
* Note Searching/Filtering
* Backend data porting (for trying out various backends)
* Extensibility - Adding in multiple connectors

## Installation

### Clone or download the ashaw-notes github project.

You can easily downlaod the [repository as a zip file here.](https://github.com/follower46/ashaw-notes/archive/master.zip)
Once downloaded, extract it to a local directory.

Make sure you have Python 3 installed on your system, if you don't download the [latest version here.](https://www.python.org/downloads/)

## Install the requirements

```
$ pip3 install -r requirements.txt
```

#### Note to Windows users: quicknote.py uses readline to allow for entry suggestions, it is not possible to install this from the requirements file but instead must be compiled on your local machine.

## Configure ashaw-notes

Edit notes.config, decide if you want to use a redis backend or a local file.
There are benefits to both.

Redis offers:
* global data storage and retrieval 
* an ability to share notes on any network
* future options to create and retrieve notes on mobile devices
* redundancy (when configured with Redis Sentinel)
* atomic updates to data changes (transactions)
* potentially faster filtering on very large datasets

Local files offers:
* secure note storage
* less latency on data retrieval
* offline note taking
* automatic backups on destructive updates

For running ashaw-notes on Redis, you can either run your own Redis container/service or use [a free Redislabs account](https://redislabs.com/) as notes are very small in size. Notes taken from 4 years of use requires about 12MB of memory. The system attempts to use a little memory as possible, resulting in many sets being ziplists. 

## Running ashaw-notes

After configuring the application execute ```quicknote.py```.
You will be presented with an input box to add in your first note.
After pressing "Enter" your note will be saved and the command will terminate.

#### For speedy note inputs it is recommended that quicknote be bound to a shortcut key. A common key combination is "Ctrl + Shift + ~"
