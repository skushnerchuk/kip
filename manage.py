#!/usr/bin/env python

import os
import sys

from dotenv import load_dotenv

from kip.settings import DEBUG

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kip.settings")
    if DEBUG:
        load_dotenv('.env')
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
