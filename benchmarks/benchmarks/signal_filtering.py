import numpy as np
import timeit
from concurrent.futures import ThreadPoolExecutor, wait

from .common import Benchmark, safe_import

with safe_import():
    from scipy.signal import (lfilter, firwin, decimate, butter, sosfilt,
                              medfilt2d)


class Decimate(Benchmark):
    param_names = ['q', 'ftype', 'zero_phase']
    params = [
        [2, 10, 30],
        ['iir', 'fir'],
        [True, False]
    ]

    def setup(self, q, ftype, zero_phase):
        np.random.seed(123456)
        sample_rate = 10000.
        t = np.arange(int(1e6), dtype=np.float64) / sample_rate
        self.sig = np.sin(2*np.pi*500*t) + 0.3 * np.sin(2*np.pi*4e3*t)

    def time_decimate(self, q, ftype, zero_phase):
        decimate(self.sig, q, ftype=ftype, zero_phase=zero_phase)


class Lfilter(Benchmark):
    param_names = ['n_samples', 'numtaps']
    params = [
        [1e3, 50e3, 1e6],
        [9, 23, 51]
    ]

    def setup(self, n_samples, numtaps):
        np.random.seed(125678)
        sample_rate = 25000.
        t = np.arange(n_samples, dtype=np.float64) / sample_rate
        nyq_rate = sample_rate / 2.
        cutoff_hz = 3000.0
        self.sig = np.sin(2*np.pi*500*t) + 0.3 * np.sin(2*np.pi*11e3*t)
        self.coeff = firwin(numtaps, cutoff_hz/nyq_rate)

    def time_lfilter(self, n_samples, numtaps):
        lfilter(self.coeff, 1.0, self.sig)

class ParallelSosfilt(Benchmark):
    timeout = 100
    timer = timeit.default_timer

    param_names = ['n_samples', 'threads']
    params = [
        [1e3, 10e3],
        [1, 2, 4]
    ]

    def setup(self, n_samples, threads):
        self.filt = butter(8, 8e-6, "lowpass", output="sos")
        self.data = np.arange(int(n_samples) * 3000).reshape(int(n_samples), 3000)
        self.chunks = np.array_split(self.data, threads)

    def time_sosfilt(self, n_samples, threads):
        with ThreadPoolExecutor(max_workers=threads) as pool:
            futures = [
                pool.submit(sosfilt, self.filt, self.chunks[i])
                for i in range(threads)
            ]

            wait(futures)


class Sosfilt(Benchmark):
    param_names = ['n_samples', 'order']
    params = [
        [1000, 1000000],
        [6, 20]
    ]

    def setup(self, n_samples, order):
        self.sos = butter(order, [0.1575, 0.1625], 'band', output='sos')
        self.y = np.random.RandomState(0).randn(n_samples)

    def time_sosfilt_basic(self, n_samples, order):
        sosfilt(self.sos, self.y)


class MedFilt2D(Benchmark):
    param_names = ['threads']
    params = [[1, 2, 4]]

    def setup(self, threads):
        rng = np.random.default_rng(8176)
        self.chunks = np.array_split(rng.standard_normal((250, 349)), threads)

    def _medfilt2d(self, threads):
        with ThreadPoolExecutor(max_workers=threads) as pool:
            wait({pool.submit(medfilt2d, chunk, 5) for chunk in self.chunks})

    def time_medfilt2d(self, threads):
        self._medfilt2d(threads)

    def peakmem_medfilt2d(self, threads):
        self._medfilt2d(threads)
