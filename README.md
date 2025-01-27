# Smugmug API Gallery Content Creator

## Ideology

This library is an exercise of taking existing galleries and importing them into
various CMSes as a way of rapidly generating content on various platforms.

## Setup

- A SmugMug [API Key](https://api.smugmug.com/api/v2/doc/tutorial/api-key.html)
- A target CMS that is externally accessible, AND has a POST style create API mechanism


## Current workflow

Currently I upload galleries to a SmugMug hosted environment using the
built-in export tooling found in Lightroom that allows for rapid deployment to a
statically generated site hosted by SmugMug.

While this makes images quickly available, certain elements of the built-in
SmugMug platform leave a few items to be desired, specifically:

- Blogging / Text
  - Adding header text or descriptive text to the gallery is a cumbersome experience
- Layout / Design
  - Stuck using (granted a perfectly acceptable design paradigm) SmugMug built-in
  layouts.

## Goals

- Take an existing array of gallery nodes and populate a CMS of choice.
(currently starting with ghost.org)
- Automate the process by running a cron process so that updates made on SmugMug
can be reflected on the CMS(es) of choice.
- Familiarize myself with Python (coming from a primarily Ruby background),
as this language is compatible with pipedream.com, the service that will be used
to run the automation.
