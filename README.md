# ao3.py

A fork of alexwlchan's unofficial Python API for AO3.

This Python package provides a scripted interface to some of the data on
[AO3](https://archiveofourown.org/) (the Archive of Our Own).

It is **not** an official API.

Following the advice of the following July 2020 note, I am attempting to restructure some of the repo and add to it in places.

> **Maintenance note, 19 July 2020:** This isn't actively maintained, and it hasn't been for a long time. I created this library/repo to accompany a [blog post I wrote in 2018](https://alexwlchan.net/2017/01/scrape-logged-in-ao3/), but I haven't looked at it much since then and I don't have much time for open source these days.
>
> FWIW, if I were to work on this again, I'd start by decoupling the HTML parsing and the I/O logic (see my PyCon UK talk about [sans I/O programming](https://alexwlchan.net/2019/10/sans-io-programming/)).

(via [alexwlchan](https://github.com/alexwlchan/ao3))

**Note:** I am an engineering major, not a programmer, and I am much more comfortable with data science than with HTML or I/O. I also have very limited experience with creating usable packages. That being said, fandom analysis and history *is* very much my wheelhouse, so hopefully that interest makes up for some of my lack of knowledge. We'll see.

## Motivation

Write Python scripts that use data from AO3.

An official API for AO3 data has been [on the roadmap](http://archiveofourown.org/admin_posts/295) for a couple of years. Until that appears, I've cobbled together my own page-scraping code that does the job. It's a bit messy and fragile, but it seems to work most of the time.

If/when we get the proper API, I'd drop this in a heartbeat and do it properly.

## Installation
If you're looking for a stable, usable version of this code, please use the [original repo](https://github.com/alexwlchan/ao3) rather than this fork. At least at this point, this fork is very much still in development.

## License

The project is licensed under the MIT license.
