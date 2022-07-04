#!/usr/bin/env python3

import os
import sys
import requests
import json
import datetime
import shutil
import zipfile

from cfg import cfg

DEST_DIR = "/tmp"

def dir_init ( dest_dir ):
	os.makedirs( os.path.join ( dest_dir, "awstats" ), exist_ok=True )

	# copy images to awstats dir
	shutil.copytree ( "images", os.path.join ( dest_dir, "awstats", "images" ) )

dir_init ( DEST_DIR )

sess = requests.Session()

# load the login page
p = sess.post(cfg["login_page"] + '/login/?login_only=1', data={
	'user': cfg["user"],
	'pass': cfg["password"]
})

cfg [ 'session' ] = json.loads ( p.text ) [ 'security_token' ]

# get current year from datetime
now = datetime.datetime.now()
year = now.year
month = now.month

count = 12

while count:
	count -= 1

	cfg [ 'month' ] = '%02d' % month
	cfg [ 'year' ] = '%04d' % year

	print( "Downloading: %(month)s/%(year)s" % cfg )

	p = sess.get(cfg["awstats"] % cfg)

	html = p.text.replace( '/images', 'images' )

	open ( os.path.join ( DEST_DIR, "awstats", '%(year)s-%(month)s.html' % cfg ), 'w' ).write ( html )

	month -= 1
	if month == 0:
		month = 12
		year -= 1


# recursively compress all files in DEST_DIR in zip file
z = zipfile.ZipFile ( os.path.join ( "/ramdisk", "awstats.zip" ), 'w' )
os.chdir( DEST_DIR )
for root, dirs, files in os.walk ( "awstats" ):
	for file in files:
		z.write ( os.path.join ( root, file ) )
z.close()



