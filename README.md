Export Banyan events to DataDog
===============================

This Python script pulls events from the Banyan API and sends them to SumoLogic as multiline JSON, where you can see them in the Log Viewer.
Based on https://github.com/banyansecurity/integrations/tree/master/siem/datadog

It's designed to be run every 10 minutes as an AWS Lambda function.

## Prerequisites

* Python 3.9 (At least 3.7 is required, but see notes below)
* `pybanyan` module
* Environment variables set up as below

## Environment Variables

* `BANYAN_REFRESH_TOKEN` - get one from your [Banyan profile] page
* `BANYAN_API_URL` - (optional) defaults to `https://net.banyanops.com`
* `SUMO_WEBHOOK` - the webhook URL for your Sumo HTTP source

## Notes

* The `cryptography` and `cffi` modules (which come along with `pybanyan`) are OS specific, so unless you are devloping this on the same OS that Lambda uses, you will have problems with them when you upload to Lambda.
* Use the following Pip commands to download the packages specific to the Amazon linux OS, then extract the whl and copy to your distro package.
You may end up with v3.9 packages depending on your dev environment, so make sure to set the python interpreter accordingly to match.

##### Downloads for `cryptography` and `cffi` packages  

```pip download cffi --platform manylinux2014_x86_64 --no-deps -d path_to_save_download```
```pip download cryptography --platform manylinux2014_x86_64 --no-deps -d path_to_save_download```
