#!/usr/bin/env bash

celery -A tasks:celery_app worker -l info --pool=solo

celery -A tasks:celery_app worker -l info