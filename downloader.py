#!/usr/bin/env python3

import os
import sys
import requests
import json
import datetime
import shutil
import zipfile

from cfg import cfg

DEST_DIR = cfg [ 'tmp_dir' ]

def dir_init ( dest_dir ):
	"""
	initialize destination directories
	"""
	dest_path = os.path.join ( dest_dir, "awstats" )
	shutil.rmtree(dest_path, ignore_errors=True)
	os.makedirs(dest_path)

	# copy images to awstats dir
	shutil.copytree ( "images", os.path.join ( dest_dir, "awstats", "images" ) )

dir_init ( DEST_DIR )
sess = requests.Session()

def login_to_cpanel ():
	"""
	Logs in into cpanel and get the session id
	"""
	url = '%(login_page)s/login/?login_only=1' % cfg

	# load the login page
	p = sess.post( url, data={
		'user': cfg["user"],
		'pass': cfg["password"]
	})

	cfg [ 'session' ] = json.loads ( p.text ) [ 'security_token' ]


def download_stats ( max_months = 12 ):
	"""
	download single awstats pages
	"""
	# get current year from datetime
	now = datetime.datetime.now()
	year = now.year
	month = now.month

	max_months = 12

	while max_months:
		max_months -= 1

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

def create_stats_zip ():
	# recursively compress all files in DEST_DIR in zip file
	z = zipfile.ZipFile ( os.path.join ( cfg [ 'save_dir' ], "awstats.zip" ), 'w' )
	os.chdir( DEST_DIR )
	for root, dirs, files in os.walk ( "awstats" ):
		for file in files:
			z.write ( os.path.join ( root, file ) )
	z.close()

if __name__ == "__main__":
	login_to_cpanel()
	download_stats()
	create_stats_zip()
	print( "Done!" )
	sys.exit( 0 )



