#!/usr/bin/env python3

"""
CPanel AWStats Downloader - by Fabio Rotondo (fabio.rotondo@gmail.com)
Copyright (C) 2022 - Fabio Rotondo

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import argparse
import datetime
import json
import os
import requests
import shutil
import sys
import zipfile

class CPanelAWStatsDownloader:
	cfg  = {}
	sess = None
	no_email = False
	max_months = 12

	def __init__ ( self, cfg_file, max_months, no_email, user, password, domain ):
		self.no_email = no_email
		self.max_months = max_months

		self._read_cfg(	cfg_file )

		if ( user ): self.cfg [ 'user' ] = user
		if ( password ): self.cfg [ 'password' ] = password
		if ( domain ): self.cfg [ 'domain' ] = domain

		self.sess = requests.Session()

	def run ( self ):
		"""
		run the program
		"""
		self._dir_init( self.cfg [ 'tmp_dir' ] )
		self._login_to_cpanel()
		self._download_stats( self.max_months )
		self._create_stats_zip()

		if not self.no_email: self._send_email()

	def _dir_init ( self, dest_dir ):
		"""
		initialize destination directories
		"""
		dest_path = os.path.join ( dest_dir, "awstats" )
		shutil.rmtree(dest_path, ignore_errors=True)
		os.makedirs(dest_path)

		# copy images to awstats dir
		shutil.copytree ( "images", os.path.join ( dest_dir, "awstats", "images" ) )

	def _login_to_cpanel ( self ):
		"""
		Logs in into cpanel and get the session id
		"""
		url =  ( '%(login_page)s/login/?login_only=1' % self.cfg ) % self.cfg

		# load the login page
		p = self.sess.post( url, data={
			'user': self.cfg["user"],
			'pass': self.cfg["password"]
		})

		self.cfg [ 'session' ] = json.loads ( p.text ) [ 'security_token' ]


	def _download_stats ( self, max_months = 12 ):
		"""
		download single awstats pages
		"""
		# get current year from datetime
		now = datetime.datetime.now()
		year = now.year
		month = now.month

		while max_months:
			max_months -= 1

			self.cfg [ 'month' ] = '%02d' % month
			self.cfg [ 'year' ] = '%04d' % year

			print( "Downloading: %(month)s/%(year)s" % self.cfg )

			p = self.sess.get( self.cfg["awstats"] % self.cfg)

			html = p.text.replace( '/images', 'images' )

			open ( os.path.join ( self.cfg [ 'tmp_dir' ], "awstats", '%(year)s-%(month)s.html' % self.cfg ), 'w' ).write ( html )

			month -= 1
			if month == 0:
				month = 12
				year -= 1

	def _create_stats_zip ( self ):
		# recursively compress all files in DEST_DIR in zip file
		z = zipfile.ZipFile ( os.path.join ( self.cfg [ 'save_dir' ], "awstats.zip" ), 'w' )
		os.chdir( self.cfg [ 'tmp_dir' ] )
		for root, dirs, files in os.walk ( "awstats" ):
			for file in files:
				z.write ( os.path.join ( root, file ) )
		z.close()

	def _send_email ():
		"""
		sends the email with the attachment
		"""
		from email.mime.multipart import MIMEMultipart
		from email.mime.base import MIMEBase
		from email.mime.text import MIMEText
		from email import encoders
		import smtplib

		# create the email
		msg = MIMEMultipart()
		msg [ 'Subject' ] = 'Awstats for domain: ' % self.cfg [ 'domain' ]
		msg [ 'From' ] = self.cfg [ 'smtp' ] [ 'from' ]
		msg [ 'To' ] = self.cfg [ 'smtp' ] [ 'to' ]

		# attach the zip file

		z = open ( os.path.join ( self.cfg [ 'save_dir' ], "awstats.zip" ), 'rb' )
		zipped = MIMEBase ( 'application', 'zip' )
		zipped.set_payload ( z.read() )
		z.close()
		encoders.encode_base64 ( zipped )
		zipped.add_header ( 'Content-Disposition', 'attachment', filename = 'awstats.zip' )
		msg.attach ( zipped )

		# send the email

		s = smtplib.SMTP ( self.cfg [ 'smtp' ] [ 'server' ] )
		s.starttls()
		s.login ( self.cfg [ 'smtp' ] [ 'user' ], self.cfg [ 'smtp' ] [ 'password' ] )
		s.sendmail ( self.cfg [ 'smtp' ] [ 'from' ], self.cfg [ 'smtp' ] [ 'to' ], msg.as_string() )
		s.quit()

	def _read_cfg ( self, cfg_file ):
		"""
		read the config file
		"""
		self.cfg = json.loads ( open ( cfg_file, 'r' ).read())

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument( '-u', '--user', help = 'cpanel user' )
	parser.add_argument( '-p', '--password', help = 'cpanel password' )
	parser.add_argument( '-d', '--domain', help = 'cpanel domain' )

	parser.add_argument ( '-m', '--max-months', type=int, default=12 )
	parser.add_argument( '-c', '--config', type=str, default='cfg.json' )
	parser.add_argument( '--no-email', action='store_true' )
	args = parser.parse_args()

	c = CPanelAWStatsDownloader ( args.config, args.max_months, args.no_email, args.user, args.password, args.domain )
	c.run()

	print( "Done!" )



