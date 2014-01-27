#!/usr/bin/env python

from glob import glob
from pprint import pprint
import json
import subprocess
import sys
import argparse
import os
import time


class SensuSpec:

  def __init__(self):
    self.status_count = {
      'ok': 0,
      'warning': 0,
      'critical': 0,
      'unknown': 0
    }

    self.options = {}

  def args(self,args):
    self.options = vars(args)

  def run(self):
    self.read_files()
    self.print_output()

  def read_files(self):
    for file in glob(os.path.join(self.options['path'],"*.json")):
      fh = open(file)
      json_data = json.load(fh)
      fh.close()

      for check in json_data['checks']:
        self.run_test(check,json_data['checks'][check])


  def run_test(self, check, data):
    command = data['command']
    sys.stdout.write(check+" ")

    for i in range(self.options['retry'] + 1):
      process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
      exit_code = process.wait()
      (stdout,stderr) = process.communicate()

      if exit_code == 0:
        break
      elif i > 0:
        time.sleep(self.options['sleep'])

    if (exit_code == 0):
      print "OK"
      self.status_count['ok'] += 1
    elif (exit_code == 1):
      print "WARNING"
      print stdout
      self.status_count['warning'] += 1
    elif (exit_code == 2):
      print "CRITICAL"
      print stdout
      self.status_count['critical'] += 1
    else:
      print "UNKNOWN"
      print stdout
      self.status_count['unknown'] += 1

    return exit_code

  def print_output(self):
    total = sum(self.status_count.values())

    if (total == 0):
      print "No tests run"
      sys.exit(0)
    elif (self.status_count['ok'] == 0):
      print "All tests failed"
      sys.exit(1)
    elif (total != self.status_count['ok']):
      print "Some tests failed"
      sys.exit(1)
    else:
      print "All tests passed"
      sys.exit(0)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-p", "--path", help="Path containing sensu client config", default="/etc/sensu/conf.d/")
  parser.add_argument("-r", "--retry", help="Number of times to retry a test", type=int, default=0)
  parser.add_argument("-s", "--sleep", help="Seconds to sleep between test retries", type=float, default=5.0)

  sensu_spec = SensuSpec()
  sensu_spec.args(parser.parse_args())
  sensu_spec.run()
