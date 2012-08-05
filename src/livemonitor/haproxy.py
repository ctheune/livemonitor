import csv
import livemonitor.measures
import time
import urllib2


class Source(object):

    url = 'http://localhost:8092/admin/stats;csv'

    def update(self):
        data = urllib2.urlopen(self.url)
        reader = csv.DictReader(data, delimiter=',')
        self.status = list(reader)
        self.timestamp = time.time()

    def _filter(self, include=(), exclude=()):
        values = []
        assert not (include and exclude)
        for line in self.status:
            value = line['svname']
            if include and value in include:
                values.append(line)
            if exclude and value not in exclude:
                values.append(line)
        return values

    def get_frontend(self):
        return self._filter(include=('FRONTEND',))[0]

    def get_backend(self):
        return self._filter(include=('BACKEND',))[0]

    def get_servers(self):
        return self._filter(exclude=('BACKEND', 'FRONTEND'))


class RequestRate(livemonitor.measures.Measure):

    value = 0

    def update(self):
        frontend = self.source.get_frontend()
        self.value = int(frontend['req_rate'])
        self.timestamp = self.source.timestamp


class ErrorRateBase(livemonitor.measures.Measure):

    field = None

    value = 0
    timestamp = 0
    last_absolute = None

    def update(self):
        backend = self.source.get_backend()
        errors = int(backend[self.field])
        if self.last_absolute is None:
            self.last_absolute = errors
            self.timestamp = self.source.timestamp
            return
        self.value = (errors - self.last_absolute) / (self.source.timestamp - self.timestamp)
        self.last_absolute = errors
        self.timestamp = self.source.timestamp


class ErrorResponses(ErrorRateBase):
    field = 'eresp'


class Error4xx(ErrorRateBase):
    field = 'hrsp_4xx'


class Error5xx(ErrorRateBase):
    field = 'hrsp_5xx'


class Health(livemonitor.measures.Measure):

    def update(self):
        total = 0
        alive = 0
        for server in self.source.get_servers():
            total += 1
            if server['status'] == 'UP':
                alive += 1
        self.value = alive / total * 100
        self.timestamp = self.source.timestamp


def configure():
    source = Source()
    request_rate = RequestRate()
    request_rate.source = source
    health = Health()
    health.source = source
    error_responses = ErrorResponses()
    error_responses.source = source
    error_4xx = Error4xx()
    error_4xx.source = source
    error_5xx = Error5xx()
    error_5xx.source = source
    return [source, request_rate, health, error_responses, error_4xx, error_5xx]
