# tasks.py
# author(s): Anton Erholt - <antonaut@github>
# ========
# Used to load up celery aswell as to define the taskmgr
# for the tasks.

from __future__ import absolute_import

from celery import Celery

from ..crawler import crawlInterface as ci

taskmgr = Celery(main='veracitor.tasks.tasks.taskmgr',
                 include=['veracitor.tasks.crawler',
                          'veracitor.tasks.algorithms',
                          'veracitor.tasks.search',
                          'veracitor.tasks.test'])

try:
    import os
    taskmgr.config_from_object("celeryconf")
except:
    try:
        taskmgr.config_from_envvar(os.environ['VERACITOR_CELERY_SETTINGS'])
    except:
        raise Error("Unable to load celery configuration.'")

ci.init_interface()


if __name__ == '__main__':
    taskmgr.start()
