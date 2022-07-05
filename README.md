# CPanel AWStats Downloader

Download AWStats pages from behind CPanel servers.

The pages are downloaded as static HTML pages, one per month and saved inside a zip file.

The downloader always starts from the current month and goes back for as many months as you want, specified by `--max-months`.

The script needs a configuration file to be able to download the pages.
Here is the configuration file explained:

```json
{
	"user": "cpanel_user",
	"password": "cpanel_password",
	"domain": "domain",
	"tmp_dir": "/tmp",
	"save_dir": "/ramdisk",
	"smtp": {
		"user": "smtp_user",
		"password": "smtp_password",
		"server": "smtp_server",
		"from": "email-sender-addr",
		"to": "email-destination-addr"
	},
	"login_page": "https://%(domain)s:2083/",
	"awstats": "https://%(domain)s:2083/%(session)s/awstats.pl?databasebreak=month&month=%(month)s&year=%(year)s&output=main&config=%(domain)s&lang=it&ssl=1&framename=mainright&"
}
```

- `user` is the cpanel user name
- `password` is the cpanel password
- `domain` is the domain name you want to download the pages from
- `tmp_dir` is the directory where the script will save the pages
- `save_dir` is the directory where the script will save the zip file
- `smtp` is the SMTP configuration
- `login_page` is the URL of the login page (you should usually not touch this)
- `awstats` is the URL of the AWStats page (you should usually not touch this)


## Usage

```shell
$ downloader.py --help
```

The script can be run with the `--help` option to get the parameters list.

Some parameters will overwrite the same key inside the configuration file.

```shell
$ downloader.py --config=cfg.json --max-months=3
```

The script can be run with the `--config` option to specify the configuration file (so if you have multiple domains, you can specify the configuration file for each domain).

Script parameters are:

```shell
-u --user: cpanel user name
-p --password: cpanel password
-d --domain: domain name
-m --max-months: number of months to download
-c --config: configuration file

--no-email: do not send the email with the zip file
```


The `--user`, `--password` and `--domain` parameters are useful if you want to use the script with multiple domains and you want to specify always the same configuration file (for example, if you want to use the same SMTP server for all the domains).