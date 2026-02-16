# Jon Frankel's Extremely Overengineered Résumé

This is my résumé based on the [Cloud Resume Challenge](https://cloudresumechallenge.dev).
It's purposefully overengineered to demonstrate a skillset for full-stack, cloud-based app development.
You can find the live production deployment [here](https://resume.frankel.dev).

## The Résumé

The résumé itself is built in plain-old [HTML](public/index.html) and [CSS](public/style.css).
(This may change to React or Svelte in the future.) It is hosted AWS S3.

## The API

There is a single endpoint, [written in Python](api/main.py), to support a visit counter.
There is also a [small bit of TypeScript](src/index.ts) to hit that endpoint on page load
and update the counter on the page. This is [compiled with Webpack](webpack.config.ts) and
placed in the `public` directory next to the HTML file.

## The Database

The Python API uses DynamoDB to store the visit counter. Right now there is only a single global
counter, incremented and read within the same request.

## Deployment

The "cloud" for this is AWS.
 
## Tests

Python integration tests are written in [Pytest](api/integration_tests/test_main.py).

