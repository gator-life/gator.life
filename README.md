[![Build Status](https://travis-ci.org/gator-life/gator.life.svg?branch=master)](https://travis-ci.org/gator-life/gator.life)
[![Coverage Status](https://coveralls.io/repos/gator-life/gator.life/badge.svg?branch=master)](https://coveralls.io/r/gator-life/gator.life?branch=master)

# Gator Life!

This is the codebase of [gator.life](http://www.gator.life)

*WORK IN PROGRESS*

Crawl the web and use machine learning algorithms to provide a personalized list of links. 

## Mission

Whatever your passions are, today, a few gems will appear on the web. How to find them among billions of blog posts, videos and news articles?

*Gator life* aims to explore the web and provide the best content to each person.

### Doesn't it already exist?

Sort of, you have to trust closed platforms and their algorithms to do the job for you. This raises fundamental issues:

Hidding behind the need to learn about you for their algorithms to work, Those platforms track always more of what you do. What do they know about you? What do they do with it?

When they choose something for you, is it what YOU want to see, or what THEY want you to see? Is it the most interesting content or the most monetizable? Who decides to promote or censor?

### How is *Gator life* different?

One word: **OPEN**. We believe it changes everything. Because it leads to another one: **ACCOUNTABLE**.

You can judge if we are true to our mission. You can challenge every change and its rationale. You can fill a issue or make a pull request each time you think we can do better.

## Installation

Tested on Ubuntu 14.04 and 16.04. For more details on how the setup was done on Ubuntu 14.04 and 16.04 see `admin/howto.txt`.

1. Make sure you have installed the dependencies:

	* `Git LFS`
	* `Python` 2.7, `pip` and `virtualenv`
	* `Docker`
	* `PhantomJS`
	* `Java` 7+ JRE

2. Clone this repository:

	```sh
	$ git clone https://github.com/gator-life/gator.life.git
	```

3. Under repo root directory, run setup script:

	```sh
	$ tools/setup_local.sh
	```

	This script will:
	
		* Clean the previous install if needed
		* Create a virtual environment `global_env`
		* Install all dependencies
		* Run unit tests, functional tests and linter to ensure setup is ok

## Contributing

Thank you for your interest for the open source projet *Gator Life*. For now we welcome contributions in two ways:

* Fill an issue on github
* Make a pull request and assign it to one of the main contributors:
	* It should be green on *Travis CI* before it can be merged into master, which means:
		* Passes all unit tests

			```sh
			$ tools/start_tests.sh
			```

		* Passes linter:

			```sh
			$ tools/run_pylint.sh
			```
	* Test coverage should be close to 100%:
		* Unit tests for a package are in directory *tests* besides the package.
		* Each module *{MODULE}.py* is tested by a script named *test_{MODULE}.py*
		* Integration tests are in directory *src/functests*


## Architecture overview

The project contains the following python packages:
* `common`: shared tools (serialization, testing helpers, logging...) between packages. Should be kept minimal. No internal dependency.
* `server`: **gator.life** website backend. Uses `Flask` framework and is deployed on `Google Cloud Platform`. No internal dependency.
* `scraper`: scraping of the web to extract documents. Depends on `common` package only.
* `topicmodeller`: classification of the extracted documents. Depends on `common` package only.
* `learner`: machine learning algorithms to learn users preferences and match classified documents and users. Depends on `common` package only.
* `orchestrator`: coordinatation of the pipeline from scraping to users/documents matching. Depends on `common`, `scraper`, `topicmodeller`, `learner`. It currently depends also on `server` for database access, but this should be extracted in its own package.
