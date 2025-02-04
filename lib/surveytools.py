import sys
import math

RHO = 200 / math.pi


class SWVersion(object):

    def __init__(self, release: int, version: int, sub_version: int):
        self.release = release
        self.version = version
        self.sub_version = sub_version

    def __str__(self):
        return "Version {0:02d}.{1:02d}.{2:02d}".format(self.release, self.version, self.sub_version)


class Angle(object):

    def __init__(self, rad: int = 0):
        self.value_rad = rad

    @staticmethod
    def from_gon(gon_value):
        r = Angle()
        r.set_gon(gon_value)
        return r

    def set_gon(self, gon):
        self.value_rad = gon / RHO
        return

    def get_gon(self):
        return self.value_rad * RHO

    def add_half_circle(self):
        r = Angle()
        r.value_rad = self.value_rad + math.pi
        r.normalise()
        return r

    def add_full_circle(self):
        r = Angle()
        r.value_rad = self.value_rad + 2 * math.pi
        r.normalise()
        return r

    def supplementary_angle(self):
        r = Angle()
        r.value_rad = 2 * math.pi - self.value_rad
        return r

    def abs(self):
        r = Angle()
        r.value_rad = abs(self.value_rad)
        return r

    def __add__(self, o):
        if isinstance(o, Angle):
            r = Angle()
            r.value_rad = self.value_rad + o.value_rad
            return r
        else:
            raise TypeError("unsupported operand type(s) for +: 'Angle' and '" + type(o).__name__ + "'")

    def __sub__(self, o):
        if isinstance(o, Angle):
            r = Angle()
            r.value_rad = self.value_rad - o.value_rad
            return r
        else:
            raise TypeError("unsupported operand type(s) for -: 'Angle' and '" + type(o).__name__ + "'")

    def __mul__(self, o):
        r = Angle()
        if isinstance(o, Angle):
            raise TypeError("unsupported operand type(s) for *: 'Angle' and '" + type(o).__name__ + "'")
        else:
            r.value_rad = self.value_rad * o
        return r

    def __truediv__(self, o):
        r = Angle()
        if isinstance(o, Angle):
            raise TypeError("unsupported operand type(s) for /: 'Angle' and '" + type(o).__name__ + "'")
        else:
            r.value_rad = self.value_rad / o
        return r

    def __str__(self):
        return '{0:.7} gon'.format(self.get_gon())

    def normalise(self):
        self.value_rad %= 2 * math.pi

    def sin(self):
        return math.sin(self.value_rad)

    def cos(self):
        return math.cos(self.value_rad)


class MeasurementTarget(object):

    def __init__(self, target, direction: Angle, zenith: Angle, distance):
        self.target_number = target
        self.direction = direction
        self.distance = distance

        self.zenith = zenith
        self.face1 = []
        self.face2 = []

    def direction_second_face(self):
        return self.direction.add_half_circle()

    def zenith_second_face(self):
        return self.zenith.supplementary_angle()

    def __str__(self):
        return "Target: " +  str(self.target_number) + " hz: " + str(self.direction) + " vz: " + str(self.zenith) + " s: " + str(self.distance)


class Coordinate(object):

    def __init__(self, pkt_nr, x, y, z):
        self.pkt_nr = pkt_nr
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, o):
        if isinstance(o, Coordinate):
            return Coordinate(self.pkt_nr, self.x + o.x, self.y + o.y, self.z + o.z)
        else:
            raise TypeError("unsupported operand type(s) for +: 'Coordinate' and '" + type(o).__name__ + "'")

    def __sub__(self, o):
        if isinstance(o, Coordinate):
            return Coordinate(self.pkt_nr, self.x - o.x, self.y - o.y, self.z - o.z)
        else:
            raise TypeError("unsupported operand type(s) for -: 'Coordinate' and '" + type(o).__name__ + "'")

    def __mul__(self, o):
        if isinstance(o, Coordinate):
            return Coordinate(self.pkt_nr, self.x * o.x, self.y * o.y, self.z * o.z)
        else:
            raise TypeError("unsupported operand type(s) for *: 'Coordinate' and '" + type(o).__name__ + "'")

    def __truediv__(self, o):
        if isinstance(o, Coordinate):
            return Coordinate(self.pkt_nr, self.x / o.x, self.y / o.y, self.z / o.z)
        else:
            return Coordinate(self.pkt_nr, self.x / o, self.y / o, self.z / o)

    def __str__(self):
        return "[y: " + str(self.y) + ", x: " + str(self.x) + " , z: " + str(self.z) + "]"


class Measurement(object):

    def __init__(self, target, direction: Angle, zenith: Angle, sd, atmospheric_data, measure_time):
        self.target_number = target
        self.direction = direction
        self.zenith = zenith
        self.slope_distances = sd
        self.atmospheric_data = atmospheric_data
        self.measure_time = measure_time

    def __str__(self):
        return "[target: " + str(self.target_number) + ", direction: " + str(self.direction) + " , zenith: " \
               + str(self.zenith) + ", slope_distances: " + str(self.slope_distances) + ", atmospheric_data: "\
               + str(self.atmospheric_data) + "Measure Time: " + self.measure_time + "]"

    def get_horizontal_distances(self):
        return self.slope_distances * self.zenith.sin()

    def get_delta_height(self):
        return self.slope_distances * self.zenith.cos()

    def get_local_coordinate(self):
        hd = self.get_horizontal_distances()
        y = hd * self.direction.sin()
        x = hd * self.direction.cos()
        z = self.get_delta_height()
        return Coordinate(self.target_number, x, y, z)

    def calc_average(self, other):
        d = (self.direction + other.direction).add_half_circle() / 2
        z = ((self.zenith - other.zenith).abs()).supplementary_angle() / 2
        sd = (self.slope_distances + other.slope_distances) / 2
        return Measurement(self.target_number, d, z, sd)


class FullAngleMeasurement(object):

    def __init__(self):
        self.hz = Angle()
        self.v = Angle()
        self.angle_accuracy = Angle()
        self.angle_time = 0
        self.cross_incline = Angle()
        self.length_incline = Angle()
        self.accuracy_incline = Angle()
        self.incline_time = 0
        self.face_def = 0

    def __str__(self):
        return "[hz: " + str(self.hz) + ", v: " + str(self.v) + " , angle_accuracy: " + str(self.angle_accuracy) + \
               ", angle_time: " + str(self.angle_time) + ", cross_incline: " + str(self.cross_incline) +\
               ", length_incline: " + str(self.length_incline) + ", accuracy_incline: " + str(self.accuracy_incline) + "]"
