import collections
import warnings


class Record(object):
    def __init__(self, site="", location="", parameter="", version="",
                 units="-", startTime=None, interval=-1, ir_block_length=None,
                 times=None, values=None, recordType="INST-VAL", qualities=None):
        # Check interval and times - could improve message wording...
        if interval == -1 and not times:
            raise ValueError("Irregular times or an interval must be specified for record.")
        if not interval == -1 and times:
            warnings.warn("Both interval and times specified. Using interval and startTime")

        self.site = site.upper()
        self.location = location.upper()
        self.parameter = parameter.upper()
        self.version = version.upper()
        self.units = units
        self.startTime = startTime
        self.interval = interval
        self._times = times if interval == -1 else None
        self.ir_block_length = ir_block_length
        self.type = recordType
        self.values = values
        self.qualities = qualities

    @property
    def origin(self):
        if len(self._values) == 1:
            return "sample"
        elif len(self._values) > 1:
            return "logger"
        else:
            return None

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, v):
        if isinstance(v, collections.Sequence):
            self._values = v
        else:
            self._values = [v]
            self.interval = -1

    @property
    def qualities(self):
        return self._qualities

    @qualities.setter
    def qualities(self, q):
        if q is None:
            self._qualities = None
        elif isinstance(q, collections.Sequence):
            self._qualities = q
        else:
            self._qualities = [q]
            
    @property
    def fullName(self):
        return "/{0.site}/{0.location}/{0.parameter}//{0.intervalStr}/{0.version}/".format(self)
    
    @property
    def times(self):
        
        if self._times:  # irregular time series
            return self._times
        elif len(self) > 1:
            # Hrm... you could cache result to self._times here, but what if 
            # startTime or interval changed.... the slight performance boost
            # probably isn't worth the pain of the edge cases, especially
            # consider times is only called a few times.
            return range(self.startTime, 
                         self.startTime + len(self) * self.interval, 
                         self.interval)
        elif len(self) == 1:
            return [self.startTime]
        else:
            return []
        
    @property
    def intervalStr(self):
        """Return interval name as a string.

        Intervals are stored internally as integer minutes(?). This converts
        the integer seconds to a string form for use by DSS.

        """
        if self.interval == -1:
            return self.ir_block_length
        else:
            units = [
                ('MIN', 60),
                ('HOUR', 60 * 24),
                ('DAY', 1e9),
            ]
            factor = 1
            for unit in units:
                if self.interval < unit[1]:
                    unitStr = unit[0]
                    break
                else:
                    factor = unit[1]
            return "{0:d}{1}".format(self.interval / factor, unitStr)
        
    @property
    def endTime(self):
        return self.times[-1]
        
    def __len__(self):
        return len(self._values)
        
    def __repr__(self):
        return "Record: {0.origin} data at {0.location}".format(self)
