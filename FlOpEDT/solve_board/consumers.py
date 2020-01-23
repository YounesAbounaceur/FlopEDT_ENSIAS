# -*- coding: utf-8 -*-

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

# from django.http import HttpResponse
# from channels.handler import AsgiHandler
# from channels import Group, Channel
# from tasks import run

import json
import logging

from threading import Thread
from django.core.exceptions import ObjectDoesNotExist
from MyFlOp.MyTTModel import MyTTModel
from base.models import TrainingProgramme
import TTapp.models as TTClasses

# from multiprocessing import Process
import os
import io
import traceback
import signal
import time

from django.core.cache import cache
from django.conf import settings


from channels.generic.websocket import WebsocketConsumer
import json, sys

_solver_child_process = 0

logger = logging.getLogger(__name__)

class SolverConsumer(WebsocketConsumer):

    def get_constraint_class(self, str):
        return getattr(sys.modules[TTClasses.__name__], str)

    def connect(self):
        # ws_message()
        self.accept()
        self.send(text_data=json.dumps({
            'message': 'hello',
            'action': 'info',
        }))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        logger.debug(f" WebSocket receive data : {data}")

        if data['action'] == 'go':

            # Save constraints state
            for constraint in data['constraints']:
                try:
                    type = self.get_constraint_class(constraint['model'])
                    instance = type.objects.get(pk=constraint['pk'])
                    instance.is_active = constraint['is_active']
                    instance.save()
                except ObjectDoesNotExist:
                    print(f"unable to find {constraint['model']} for id {constraint['pk']}")    
                except AttributeError:
                    print(f"error while importing {constraint['model']} model")    

            # Get work copy as stabilization base
            try:
                stabilize = int(data['stabilize'])
            except:
                stabilize = None

            # Start solver
            time_limit = data['time_limit'] or None

            Solve(
                data['department'],
                data['week'],
                data['year'],
                data['timestamp'],
                data['train_prog'],
                self,
                time_limit,
                data['solver'],
                stabilize_work_copy=stabilize
                ).start()

        elif data['action'] == 'stop':
            solver_child_process = cache.get("solver_child_process")
            if solver_child_process:
                self.send(text_data=json.dumps({
                    'message': 'sending SIGINT to solver (PID:'+str(solver_child_process)+')...',
                    'action': 'aborted'
                }))
                os.kill(solver_child_process, signal.SIGINT)
            else:
                self.send(text_data=json.dumps({
                    'message': 'there is no running solver!',
                    'action': 'aborted'
                }))



def solver_subprocess_SIGINT_handler(sig, stack):
    # ignore in current process and forward to process group (=> gurobi)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    os.kill(0, signal.SIGINT)


class Solve():
    def __init__(self, department_abbrev, week, year, timestamp, training_programme, chan, time_limit, solver, stabilize_work_copy=None):
        super(Solve, self).__init__()
        self.department_abbrev = department_abbrev
        self.week = week
        self.year = year
        self.timestamp = timestamp
        self.channel = chan
        self.time_limit = time_limit
        self.solver = solver
        self.stabilize_work_copy = stabilize_work_copy

        # if all train progs are called, training_programme=''
        try:
            self.training_programme = TrainingProgramme.objects.get(abbrev=training_programme)
        except ObjectDoesNotExist:
            self.training_programme = None
    
    def start(self):
        solver_child_process = cache.get("solver_child_process")
        if solver_child_process:
            self.channel.send(text_data=json.dumps({'message': "another solver is currently running (PID:"+str(solver_child_process)+"), let's wait"}))
            return
        try:
            (rd,wd) = os.pipe()
            solver_child_process = os.fork()
            if solver_child_process == 0:
                os.dup2(wd,1)   # redirect stdout
                os.dup2(wd,2)   # redirect stderr
                try:
                    t = MyTTModel(self.department_abbrev, self.week, self.year, train_prog=self.training_programme, stabilize_work_copy = self.stabilize_work_copy)
                    os.setpgid(os.getpid(), os.getpid())
                    signal.signal(signal.SIGINT, solver_subprocess_SIGINT_handler)
                    t.solve(time_limit=self.time_limit, solver=self.solver)
                except:
                    traceback.print_exc()
                    print("solver aborting...")
                    os._exit(1)
                finally:
                    print("solver exiting")
                    os._exit(0)
            else:
                cache.set("solver_child_process", solver_child_process, None)
                print("starting solver sub-process " + str(solver_child_process))
                if solver_child_process != cache.get("solver_child_process"):
                    print("unable to store solver_child_process PID, cache not working?")
                    self.channel.send(text_data=json.dumps(
                        {'message': "unable to store solver_child_process PID, you won't be able to stop it via the browser! Is Django cache not working?", 'action': 'error'}))
                os.close(wd)
                
                with io.TextIOWrapper(io.FileIO(rd)) as tube:
                    for line in tube:
                        self.channel.send(text_data=json.dumps({'message': line, 'action': 'info'}))
                
                while 1:
                    (child,status) = os.wait()
                    if child == solver_child_process and os.WIFEXITED(status):
                        break
                
                cache.delete('solver_child_process')
                if os.WEXITSTATUS(status) != 0:
                    self.channel.send(text_data=json.dumps({'message': f'solver process has aborted with a {os.WEXITSTATUS(status)} error code', 'action': 'error'}))
                else:
                    self.channel.send(text_data=json.dumps({'message': 'solver process has finished', 'action': 'finished'}))

        except OSError as e:
            print("Exception while launching a solver sub-process:")
            traceback.print_exc()
            print("Continuing business as usual...")

    
# https://vincenttide.com/blog/1/django-channels-and-celery-example/
# http://docs.celeryproject.org/en/master/django/first-steps-with-django.html#django-first-steps
# http://docs.celeryproject.org/en/master/getting-started/next-steps.html#next-steps



# send a signal
# https://stackoverflow.com/questions/15080500/how-can-i-send-a-signal-from-a-python-program#20972299
# output file+console
# https://stackoverflow.com/questions/11325019/output-on-the-console-and-file-using-python
# redirect pulp
# https://stackoverflow.com/questions/26642029/writing-coin-or-cbc-log-file
# start function in new process
# https://stackoverflow.com/questions/7207309/python-how-can-i-run-python-functions-in-parallel#7207336
# generate uuid: import uuid ; uuid.uuid4()



# channel init
# https://blog.heroku.com/in_deep_with_django_channels_the_future_of_real_time_apps_in_django


# moving to production
# https://channels.readthedocs.io/en/1.x/backends.html
# port 6379?






# docker image
# sudo apt-get install redis-server
