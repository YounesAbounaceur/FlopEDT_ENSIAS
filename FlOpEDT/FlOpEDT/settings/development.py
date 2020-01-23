# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
#
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

import os
from .base import *

# DEFAULT POSTGRES CREDENTIALS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_BACKEND = f'redis://{REDIS_HOST}:6379/1'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, 6379)],
        },
    },
}
# "ROUTING": "solve_board.routing.channel_routing",

LOGGING = {  
    'version': 1,  
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{asctime}] - {levelname} - {module} - {message}',
            'style': '{',
        },
    },    
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },        
        'django.db.backends': {
            'level':  os.environ.get('DJANGO_LOG_LEVEL', 'WARNING'),
            'handlers': ['console'],
            'propagate': True,
        }
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'al0bzdna)@6&n9mfn_vlm0wl&38#xrf@h%&^^h-q783g$e&*h!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
