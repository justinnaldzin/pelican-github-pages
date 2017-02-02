Title: Create a website using GitHub Pages and Pelican
Date: 2017-2-1
Category: Guides

Using [Pelican](http://docs.getpelican.com) with [GitHub Pages ](https://pages.github.com), this guide shows how to set up a static site for hosting and sharing projects.

Pelican is a static site generator, written in Python, that requires no database or server-side logic.

GitHub Pages allows you to host website content directly from your GitHub repository.

---
### Create a Pelican source project repository
Login to your GitHub account and create a new repository named `pelican-github-pages`.  This will be the Pelican source project that will generate the static HTML pages.

Clone the repo
```sh
git clone https://github.com/username/pelican-github-pages
cd pelican-github-pages
```

---
## Create a GitHub Pages repo
Head over to [GitHub Pages ](https://pages.github.com/) and follow the simple instructions to create a new repository named `username.github.io` substituting your GitHub username, obviously.  This will contain the HTML files for the static site that GitHub hosts.

---
## Install and setup Pelican

Install Pelican and Markdown
```sh
pip install pelican markdown
```

Create a skeleton project via the `pelican-quickstart` script
```sh
pelican-quickstart
```
Here is an example of the script output:
```
Welcome to pelican-quickstart v3.7.1.

This script will help you create a new Pelican-based website.

Please answer the following questions so this script can generate the files
needed by Pelican.


> Where do you want to create your new web site? [.]
> What will be the title of this web site? Justin Naldzin
> Who will be the author of this web site? Justin Naldzin
> What will be the default language of this web site? [en]
> Do you want to specify a URL prefix? e.g., http://example.com   (Y/n) y
> What is your URL prefix? (see above example; no trailing slash) http://justinnaldzin.github.io
> Do you want to enable article pagination? (Y/n) y
> How many articles per page do you want? [10]
> What is your time zone? [Europe/Paris] America/New_York
> Do you want to generate a Fabfile/Makefile to automate generation and publishing? (Y/n) y
> Do you want an auto-reload & simpleHTTP script to assist with theme and site development? (Y/n) y
> Do you want to upload your website using FTP? (y/N) n
> Do you want to upload your website using SSH? (y/N) n
> Do you want to upload your website using Dropbox? (y/N) n
> Do you want to upload your website using S3? (y/N) n
> Do you want to upload your website using Rackspace Cloud Files? (y/N) n
> Do you want to upload your website using GitHub Pages? (y/N) y
> Is this your personal page (username.github.io)? (y/N) y
Done. Your new project is available at /Users/justin/Desktop/pelican-github-pages
```

Create a Markdown document saving with a `.md` extension within the `content` directory
```txt
Title: Hello World
Date: 2017-2-1
Category: Guides

Hello World
```

---
## Pelican Themes

Add the **Pelican Themes** repo as a submodule of your Pelican source project
```sh
git submodule add https://github.com/getpelican/pelican-themes
```

Also add the **Pelican Plugins** repo as a submodule
```sh
git submodule add https://github.com/getpelican/pelican-plugins
```

Set the `THEME` variable in your `pelicanconf.py` file to the absolute or relative path to the theme.  For example, here is the **Bootstrap 3** theme:
```sh
THEME = "pelican-themes/pelican-bootstrap3"
```

And set the following variables to support the Bootstrap 3 theme
```sh
JINJA_EXTENSIONS = ['jinja2.ext.i18n']
PLUGIN_PATHS = ['pelican-plugins']
PLUGINS = ['i18n_subsites']
```

Add the GitHub pages repo that you created above as a submodule, naming it `output` to match Pelican's default output directory.
```sh
git submodule add https://github.com/username/username.github.io output
```

Change the following setting to False in your `publishconf.py` file to prevent the deletion of the output directory when running the `pelican` command.
```sh
DELETE_OUTPUT_DIRECTORY = False
```

---
##Generating the static site files and run a devserver

Create a Markdown file saving with a `.md` extension within the `content` directory.  For example:
```txt
Title: Hello World
Date: 2017-2-1
Category: Guide

Hello World
```

Within the project's main directory, generate the HTML files and serve the site locally
```sh
make devserver
```

Navigate to http://localhost:8000

---
## Publish the static HTML files to GitHub

Initialize the output directory, add the remote, add the files, commit, and push the changes
```sh
cd output
$ git init
$ git remote add origin https://github.com/username/username.github.io.git
$ git add --all
$ git commit -m "inital commit"
$ git push origin master
```

Now navigate to http://username.github.io

Also push the Pelican source project to the `pelican-github-pages` repo
```sh
cd ..
git add .
git commit -m "First commit."
git push -u origin master
```

Be sure the Pelican source project ignores this directory`
``sh
echo "output/" >> .gitignore
```
