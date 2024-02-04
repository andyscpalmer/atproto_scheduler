# Atproto Post Scheduler

This is a tool that utilizes the [Python AT Protocol SDK](https://atproto.blue/en/latest/) along with [Django](https://www.djangoproject.com/) to create an interface where users can compose draft posts and have them publish at pre-specified times.

It uses an AWS S3 bucket to allow posting images and also has the ability to automatically include rich text hyperlinks and link cards in posts.

This web app is intended for single-person use at the moment and as such it only makes use of Django's built-in `superuser` admin role. Currently all user interactions are handled in Django's admin interface located at `<url>/admin` and there is no "front page". There is functionality for multiple _Bluesky_ accounts, however.

This tool can be run locally with some small modifications but it was primarily developed to run on DigitalOcean. 

For a continuous demo of this app, this is a Bluesky account which will automatically post pictures of my cat Maple at 3AM: [Late Night Maple](https://bsky.app/profile/latenitemaple.bsky.social)

## Installation

At this early stage, there is no straightforward installation. However, [this guide from DigitalOcean](https://docs.digitalocean.com/developer-center/deploy-a-django-app-on-app-platform/) provides the main framework for installation that the bulk of this app was configured around. There are, however, a few significant differences outlined below.

### Requirements

The app will not run properly without the following:
- A Bluesky account with an app password
- An AWS S3 bucket with a folder `/images` for posting images
- Some form of hosting

### Environment Variables

The following environment variables are required, except `DEVELOPMENT_MODE`. Some of them are listed in the DigitalOcean guide linked above, the rest are not.

#### Django-only Environment Variables
- `DATABASE_URL` = `${db.DATABASE_URL}`
- `DJANGO_ALLOWED_HOSTS` = `${APP_DOMAIN}`
- `DEBUG` = `False`
- `DEVELOPMENT_MODE` = `False` (Optional)
  - If this is set to `True` in production, it will use a SQLite database which will be wiped with each deploy. I highly recommend against that.
- `DJANGO_SECRET_KEY` = `<long generated key>` [set encrypted]

#### AWS Environment Variables
- `AWS_S3_IAM_USERNAME` = `<your AWS S3 IAM username>`
- `AWS_S3_IAM_PASSWORD` = `<your AWS S3 IAM password>` [set encrypted]
- `AWS_ACCESS_KEY` = `<your AWS bucket access key>`
- `AWS_SECRET_ACCESS_KEY` = `<your AWS secret access key>` [set encrypted]
- `AWS_BUCKET_NAME` = `<your AWS bucket name>`

## Use

Once the app is up and running with database migrations completed, you will need to log in to the Django admin page with the `superuser` account, open the `Configs` table, and replace the `'placeholder'` data with your Bluesky account credentials. Additionally, the application will not be able to post until the `Allow posts` checkbox is checked.

All the best!

Andy