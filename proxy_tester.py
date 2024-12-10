import requests
import time
from concurrent.futures import ThreadPoolExecutor

proxies = {
    "Name1": "http://login:password@host:port",
    "Name2": "http://login:password@host:port",
}

test_urls = {
    "ping": "https://google.com",
    "speed": "https://proof.ovh.net/files/10Mb.dat",
}

stability_test_attempts = 5
timeout_ping = 10
timeout_speed = 20

class ProxyTester:
    def __init__(self, proxies, test_urls, stability_attempts):
        self.proxies = proxies
        self.test_urls = test_urls
        self.stability_attempts = stability_attempts

    def test_ping(self, proxy_url):
        try:
            start_time = time.time()
            response = requests.get(self.test_urls["ping"], proxies={"http": proxy_url, "https": proxy_url}, timeout=timeout_ping)
            if response.status_code == 200:
                return time.time() - start_time
        except Exception as e:
            print(f"Ping test error for {proxy_url}: {e}")
        return None

    def test_stability(self, proxy_url):
        latencies = []
        for _ in range(self.stability_attempts):
            latency = self.test_ping(proxy_url)
            if latency:
                latencies.append(latency)
        if latencies:
            return sum(latencies) / len(latencies)
        return None

    def test_speed(self, proxy_url):
        try:
            start_time = time.time()
            response = requests.get(self.test_urls["speed"], proxies={"http": proxy_url, "https": proxy_url}, stream=True, timeout=timeout_speed)
            if response.status_code == 200:
                return time.time() - start_time
        except Exception as e:
            print(f"Speed test error for {proxy_url}: {e}")
        return None

    def run_tests(self):
        ping_results = []
        stability_results = []
        speed_results = []

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.test_ping, proxy): name for name, proxy in self.proxies.items()}
            for future in futures:
                proxy_name = futures[future]
                latency = future.result()
                if latency:
                    ping_results.append((proxy_name, latency))

        for proxy_name, proxy in self.proxies.items():
            stability = self.test_stability(proxy)
            speed = self.test_speed(proxy)

            if stability:
                stability_results.append((proxy_name, stability))
            if speed:
                speed_results.append((proxy_name, speed))

        ping_results.sort(key=lambda x: x[1])
        stability_results.sort(key=lambda x: x[1])
        speed_results.sort(key=lambda x: x[1])

        self.print_results("PING TEST RESULTS", stability_results)
        self.print_results("SPEED TEST RESULTS", speed_results)

    @staticmethod
    def print_results(title, results):
        print(f"\n==== {title} ====")
        for proxy_name, value in results:
            print(f"{proxy_name}: {value:.2f} sec")


if __name__ == "__main__":
    tester = ProxyTester(proxies, test_urls, stability_test_attempts)
    print("==== PROXY TEST STARTED ====")
    tester.run_tests()
    print("")
