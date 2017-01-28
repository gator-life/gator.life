[![Build Status](https://travis-ci.org/gator-life/gator.life.svg?branch=master)](https://travis-ci.org/gator-life/gator.life)
[![Coverage Status](https://coveralls.io/repos/gator-life/gator.life/badge.svg?branch=master)](https://coveralls.io/r/gator-life/gator.life?branch=master)

*WORK IN PROGRESS*

Crawl the web and use machine learning algorithms to provide a personalized list of links. 

## Installation

Tested on Ubuntu 14.04 and 16.04. For more details on how the setup was done on Ubuntu 14.04 and 16.04 see `admin/howto.txt`.

1. Make sure you have installed the dependencies:

	* `Git LFS`
	* `Python` 2.7, `pip` and `virtualenv`
	* `Docker`
	* `PhantomJS`
	* `Java` 7+ JRE
	* `Node.js` 7, `npm`

2. Clone this repository:

	```sh
	$ git clone https://github.com/gator-life/gator.life.git
	```

3. Under repo root directory, run setup script:

	```sh
	$ scripts/setup_local.sh
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
			$ scripts/start_tests.sh
			```

		* Passes linter:

			```sh
			$ scripts/run_pylint.sh
			```
	* Test coverage should be close to 100%:
		* Unit tests for a package are in directory *tests* besides the package.
		* Each module *{MODULE}.py* is tested by a script named *test_{MODULE}.py*
		* Integration tests are in directory *src/functests*


## Architecture overview

The project contains the following python packages:
* `common`: shared tools (serialization, testing helpers, logging...) between packages. Should be kept minimal. No internal dependency.
* `server`: **gator.life** website backend. Uses `Flask` framework and is deployed on `Google Cloud Platform`. Depends on `common` and `learner`.
* `scraper`: scraping of the web to extract documents. Depends on `common` package only.
* `topicmodeller`: classification of the extracted documents. Depends on `common` package only.
* `learner`: machine learning algorithms to learn users preferences and match classified documents and users. Depends on `common` package only.
* `orchestrator`: coordinatation of the pipeline from scraping to users/documents matching. Depends on `common`, `scraper`, `topicmodeller`, `learner`. It currently depends also on `server` for database access, but this should be extracted in its own package.
