[![Build Status](https://travis-ci.org/gator-life/gator.life.svg?branch=master)](https://travis-ci.org/gator-life/gator.life)
[![Coverage Status](https://coveralls.io/repos/gator-life/gator.life/badge.svg?branch=master)](https://coveralls.io/r/gator-life/gator.life?branch=master)

# Gator Life!

This is the codebase of [gator.life](http://www.gator.life)

*WORK IN PROGRESS*

Crawl the web and use machine-learning algorithms to provide a personalized list of links. 

## Mission

Whatever your passions are, today, a few gems will appear on the web. How to find them among billions of blog posts, videos and news articles?

Gator.life aims to exlpore the web and provide the best content to each person.

### Doesn't it exist already?

Sort of, you have to trust closed platforms and their algorithms to do the job for you. This raises fundamental issues:

Hidding behind to need to learn about you for their algorithms to work, Those platforms track always more of what you do. What do they know about you? What do they do with it?

When they choose something for you, is it what YOU want to see, or what THEY want you to see? Is it the most interesting content or the most monetizable? Who decides to promote or censor?

### How is *Gator life* different?

One word: **OPEN**. We believe it changes everything. Because it leads to another one: **ACCOUTABLE**.

You can judge if we are true to our mission. You can challenge every change and its rational. You can fill a issue or make a pull request each time you think we can do better.

## Installation

1. Make sure you have installed the dependencies:

	* `git`
	* `python` 2.7
	* `virtualenv`
	* `pip`
	* `docker`
	* `google cloud` SDK
	* `PhantomJS`

2. Clone this repository:

	```sh
	$ git clone https://github.com/gator-life/gator.life.git
	```

3. Under repo root directory, create and activate virtualenv *global_env*

	```sh
	$ virtualenv global_env
	$ source global_env/bin/activate
	```

3. Under repo root directory, run script:

	```sh
	$ tools/install_envs.sh
	```

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
