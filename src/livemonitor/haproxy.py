import csv
import time
import urllib2


class HAProxy(object):

    url = 'http://localhost:8092/admin/stats;csv'

    last_update = 0
    _errors = 0
    errors = 0
    frontend_request_rate = 0

    def update(self):
        data = urllib2.urlopen(self.url)
        reader = csv.DictReader(data, delimiter=',')
        errors = 0
        for stat in reader:
            if stat['svname'] == 'FRONTEND':
                self.request_rate = int(stat['req_rate'])
            if stat['svname'] == 'BACKEND':
                errors += int(stat['eresp'])
                errors += int(stat['hrsp_4xx'])
                errors += int(stat['hrsp_5xx'])

        update = time.time() * 1000
        self.errors = (errors-self._errors) / ((update-self.last_update)/1000)
        self._errors = errors

        self.last_update = update

    def metrics(self):
        yield ('haproxy_requests', self.request_rate, self.last_update)
        yield ('haproxy_errors', self.errors, self.last_update)
