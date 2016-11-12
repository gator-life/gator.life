# Project roadmap

This document sums up the short and middle term objectives of the project

## Short term goal: MVP for 'friend' user

The website should be:
* __Usable__
* __Iterable__

### Usable

It means a user can:

- [x] Register
- [x] Log in 
- [x] Enter preferences in the form of keywords
- [ ] Modify his preferences
- [ ] See its preferences taken into account in displayed documents
- [ ] See the list of links updated regularly

### Iterable

It means that we can improve the site:
* Within a few minutes of downtime
* Without deleting data

In particular, infrastructure and database should be structured to enable below middle term goals. Specifically, we must:

- [ ] Be able to update topic model
- [ ] Be able to add other features than topic model classification
- [ ] Separate personal data from data used by machine learning so that we cannot connect them without access to user password 
- [ ] Be able to modify all personal data (email, password...) after account creation

## Middle term: MVP for 'real' user

The website should be user-friendly. It means:
* Modern and professional design
* User can modify its personal data
* User can delete its account
* User can give feedback on links (votes)
* Zero downtime objective
* professional privacy / security setup (strong password encryption, https)
* Qualitative links suggestion (not only relevant on topic matching, wihtout redundancies on subject...)
* Impacts of user actions (preferences, votes) are visible immediatly