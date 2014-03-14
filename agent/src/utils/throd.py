import time
import urllib
 
 
class ThrottleDownload(object):
    def __init__(self, rate=None):
        """ Specify rate in KB/s. """
        self.set_rate(rate)
 
    def set_rate(self, rate):
        if isinstance(rate, int) or isinstance(rate, float):
            if rate <= 0:
                self._rate = None
            else:
                self._rate = rate
        else:
            self._rate = None
 
    def _throttle_hook(self, blocknum, bs, size):
        if blocknum == 0:
            self.start_time = time.time()
            return
 
        downloaded = (blocknum * bs) / 1000  # In bytes
        elapsed_time = time.time() - self.start_time  # In seconds
 
        current_rate = downloaded / elapsed_time
        #print str(current_rate) + " KB/sec"
 
        if self._rate == None:
            return

        if current_rate > self._rate and self._rate != 0:
            sleep_time = (downloaded / self._rate) - elapsed_time
            if sleep_time < 0:
                sleep_time = 0
 
            #print "Sleep time: " + str(sleep_time)
            time.sleep(sleep_time)
 
    def download(self, url, download_path):
        urllib.urlretrieve(
            url, download_path, reporthook=self._throttle_hook)
