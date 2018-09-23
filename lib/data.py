import math

def shift_year(year):
    return year - 1982

def add_commas(number):
    return "{:,}".format(int(number))

def single_box(color):
    return "single_box_%s" % color

class LatenciesData(object):

    def __init__(self, year):
        self.year = year

    @staticmethod
    def getPayloadBytes():
        # 1 MB
        return math.pow(10, 6)

    @staticmethod
    def getNetworkPayloadBytes():
        # 2KB
        return 2 * math.pow(10,3)

    def getCycle(self):
        # Clock speed stopped at ~3GHz in ~2005
        # [source: http://www.kmeme.com/2010/09/clock-speed-wall.html]
        # Before then, doubling every ~2 self.years
        # [source: www.cs.berkeley.edu/~pattrsn/talks/sigmod98-keynote.ppt]
        if (self.year <= 2005):
            # 3*10^9 = a*b^(2005-1990)
            # b = 2^(1/2)
            # -> a = 3*10^9 / 2^(2005.5)
            a = 3 * math.pow(10, 9) / math.pow(2, shift_year(2005)*0.5)
            b = math.pow(2, 1.0/2)
            hz = a * math.pow(b, shift_year(self.year))
        else:
            hz = 3 * math.pow(10,9)

        #  1 / HZ = seconds
        #  1*10^9 / HZ = ns
        ns = math.pow(10,9) / hz
        return ns

    def getMemLatency(self):

        # Bus Latency is actually getting worse:
        # [source: http://download.micron.com/pdf/presentations/events/winhec_klein.pdf]
        # 15 self.years ago, it was decreasing 7% / self.year
        # [source: www.cs.berkeley.edu/~pattrsn/talks/sigmod98-keynote.ppt]
        if (self.year <= 2000):
           # b = 0.93
           # 100ns = a*0.93^2000
           #/ -> a = 100 / 0.93^2000
           b = 0.93
           a = 100.0 / math.pow(0.93,shift_year(2000))
           ms = a * math.pow(b, shift_year(self.year))
        else:
           ms = 100 # ns
        return ms

    def getNICTransmissionDelay(self, payloadBytes):
        # NIC bandwidth doubles every 2 self.years
        # [source: http://ampcamp.berkeley.edu/wp-content/uploads/2012/06/Ion-stoica-amp-camp-21012-warehouse-scale-computing-intro-final.pdf]
        # TODO: should really be a step def
        # 1Gb/s = 125MB/s = 125*10^6 B/s in 2003
        # 125*10^6 = a*b^x
        # b = 2^(1/2)
        # -> a = 125*10^6 / 2^(2003.5)
        a = 125 * math.pow(10,6) / math.pow(2,shift_year(2003) * 0.5)
        b = math.pow(2, 1.0/2)
        bw = a * math.pow(b, shift_year(self.year))
        # B/s * s/ns = B/ns
        ns = payloadBytes / (bw / math.pow(10,9))
        return ns

    def getBusTransmissionDelay(self, payloadBytes):
        # DRAM bandwidth doubles every 3 self.years
        # [source: http://ampcamp.berkeley.edu/wp-content/uploads/2012/06/Ion-stoica-amp-camp-21012-warehouse-scale-computing-intro-final.pdf]
        # 1MB / 250,000 ns = 10^6B / 0.00025 = 4*10^9 B/s in 2001
        # 4*10^9 = a*b^x
        # b = 2^(1/3)
        # -> a = 4*10^9 / 2^(2001.33)
        a = 4*math.pow(10, 9) / math.pow(2,shift_year(2001) * 0.33)
        b = math.pow(2,1.0/3)
        bw = a * math.pow(b, shift_year(self.year))
        # B/s * s/ns = B/ns
        ns = payloadBytes / (bw / math.pow(10,9))
        return ns

    def getSSDLatency(self):
        # Will flat-line in one capacity doubling cycle (18 months=1.5self.years)
        # Before that, 20X decrease in 3 doubling cycles (54 months=4.5self.years)
        # Source: figure 4 of http://cseweb.ucsd.edu/users/swanson/papers/FAST2012BleakFlash.pdf
        # 20 us = 2*10^4 ns in 2012
        # b = 1/20 ^ 1/4.5
        # -> a = 2*10^4 / 1/20 ^(2012 * 0.22)
        if (self.year <= 2014):
           a = 2 * math.pow(10,4) / math.pow(1.0/20, shift_year(self.year) * 0.22)
           b = math.pow(1.0/20, 1.0/4.5)
           return a * math.pow(b,shift_year(self.year))
        else:
           return 16000

    def getSSDTransmissionDelay(self, payloadBytes):
        # SSD bandwidth doubles every 3 self.years
        # [source: http://ampcamp.berkeley.edu/wp-content/uploads/2012/06/Ion-stoica-amp-camp-21012-warehouse-scale-computing-intro-final.pdf]
        # 3GB/s = a*b^2012
        # b = 2^(1/3)
        # -> a = 6*10^9 / 2^(2012.33)
        a = 3*math.pow(10, 9) / math.pow(2,shift_year(2012) * 0.33)
        b = math.pow(2, 1.0/3)
        bw = a*math.pow(b, shift_year(self.year))
        # B/s * s/ns = B/ns
        ns = payloadBytes / (bw / math.pow(10,9))
        return ns

    def getSeek(self):
        # Seek + rotational delay halves every 10 self.years
        # [source: http://www.storagenewsletter.com/news/disk/hdd-technology-trends-ibm]
        # In 2000, seek + rotational =~ 10 ms
        # b = (1/2)^(1/10)
        # -> a = 10^7 / (1/2)^(2000*0.1)
        a = math.pow(10,7) / math.pow(0.5,shift_year(2000)*0.1)
        b = math.pow(0.5,0.1)
        ns = a * math.pow(b, shift_year(self.year))
        return ns

    def getDiskTransmissionDelay(self, payloadBytes):
        # Disk bandwidth is increasing very slowly -- doubles every ~5 self.years
        # [source: http://ampcamp.berkeley.edu/wp-content/uploads/2012/06/Ion-stoica-amp-camp-21012-warehouse-scale-computing-intro-final.pdf]
        # Before 2002 (~100MB/s):
        # Disk bandwidth doubled every two self.years
        # [source: www.cs.berkeley.edu/~pattrsn/talks/sigmod98-keynote.ppt]
        if (self.year <= 2002):
          # 100MB/s = a*b^2002
          # b = 2^(1/2)
          # -> a = 10^8 / 2^(2002.5)
          a = math.pow(10,8) / math.pow(2,shift_year(2002) * 0.5)
          b = math.pow(2,1.0/2)
          bw = a * math.pow(b, shift_year(self.year))
        else:
          # 100MB/s = a*b^2002
          # b = 2^(1/5)
          # -> a = 10^8 / 2^(2002-1982 * .2)
          a = math.pow(10,8) / math.pow(2,shift_year(2002) * 0.2)
          b = math.pow(2,1.0/5)
          bw = a * math.pow(b, shift_year(self.year))

        # B/s * s/ns = B/ns
        ns = payloadBytes / (bw / math.pow(10,9))
        return ns

    @staticmethod
    def getDCRTT():
        # Assume this doesn't change much?
        return 500000 # ns

    @staticmethod
    def getWanRTT():
        # Routes are arguably improving:
        #   http://research.google.com/pubs/pub35590.html
        # Speed of light is ultimately fundamental
        return 150000000 # ns

def get_metrics(year):

    ldata = LatenciesData(year)

    ns = (1, "ns", "", "ns", "")

    # Source for L1: http://cache.freescale.com/files/32bit/doc/app_note/AN2180.pdf
    L1 = (3*ldata.getCycle(), "ns", "L1 cache reference", "L1", "")
    branch = (10*ldata.getCycle(), "ns", "Branch mispredict", "branch", "")

    # Source for L2: http://cache.freescale.com/files/32bit/doc/app_note/AN2180.pdf
    L2 = (13*ldata.getCycle(), "ns", "L2 cache reference", "L2", "")

    mutex = (50*ldata.getCycle(), "ns", "Mutex lock/unlock", "mutex", "")

    ns100 = (100, "ns", "", "ns100", single_box("blue"))

    mem = (ldata.getMemLatency(), "100ns", "Main memory reference", "mem", "")

    micro = (100*10, "100ns", "", "micro", "")
    snappy = (6000 * ldata.getCycle(), "100ns", "Compress 1KB wth Snappy",
                           "snappy", "")
    tenMicro = (100*100, "100ns", "", "tenMicro", single_box("green"))

    network = (
        ldata.getNICTransmissionDelay(ldata.getNetworkPayloadBytes()),
        "10us",
        "Send " + add_commas(ldata.getNetworkPayloadBytes()) + " bytes|over commodity network",
        "network",
        "")

    ssdRandom = (
        ldata.getSSDLatency(),
        "10us", "SSD random read", "ssdRandom", "")

    mbMem = (
        ldata.getBusTransmissionDelay(ldata.getPayloadBytes()),
        "10us",
        "Read " + add_commas(ldata.getPayloadBytes()) + " bytes|sequentially from memory",
        "mbMem", "")

    rtt = (
        ldata.getDCRTT(), "10us", "Round trip|in same datacenter", "rtt", "")

    ms = (
        100*100*100,
        "10us",
        "",
        "ms",
        single_box("red"))
    
    mbSSD = (
        ldata.getSSDTransmissionDelay(ldata.getPayloadBytes()),
        "ms",
        "Read " + add_commas(ldata.getPayloadBytes()) + " bytes|sequentially from SSD",
        "mbSSD",
        ""
        )

    seek = (
        ldata.getSeek(),
        "ms",
        "Disk seek",
        "seek",
        ""
        )

    mbDisk = (
        ldata.getDiskTransmissionDelay(ldata.getPayloadBytes()),
        "ms",
        "Read " + add_commas(ldata.getPayloadBytes()) + " bytes|sequentially from disk",
        "mbDisk",
        "")

    wan = (
        ldata.getWanRTT(),
        "ms",
        "Packet roundtrip|CA to Netherlands",
        "wan",
        "")

    metrics = [
        ns,L1,branch,L2,mutex,ns100,
        mem,micro,snappy,tenMicro,
        network, ssdRandom,mbMem,rtt,ms,
        mbSSD,seek,mbDisk,wan]

    return metrics

