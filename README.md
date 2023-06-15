# Smugmug API Gallery Content Creator

## Ideology

This library is an exercise of taking existing galleries and importing them into
various CMSes as a way of rapidly generating content on various platforms.

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
