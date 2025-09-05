# nicelib
How do I know a particular module is a sensible choice for my app? Once decided that it fulfills my needs, I want to make sure it is stable and mature enough and is actively developed. I look for factors like the number of contributors, when was the last commit made, number of releases and so on. For that purpose, I made *nicelib*.

*nicelib* runs from command line, it will quickly lookup the module on PyPI, then check its source code and make a coincise report with the basic data I'm looking for. It will cache the results locally, to speed up calls.
