import random
import logging
import time
from collections import defaultdict

# ------------------------------------------------------------------------------- #


class ProxyManager:
    """
    A class to manage and rotate proxies for CloudScraper
    """

    def __init__(self, proxies=None, proxy_rotation_strategy='sequential', ban_time=300):
        """
        Initialize the proxy manager
        
        :param proxies: List of proxy URLs or dict mapping URL schemes to proxy URLs
        :param proxy_rotation_strategy: Strategy for rotating proxies ('sequential', 'random', or 'smart')
        :param ban_time: Time in seconds to ban a proxy after a failure (for 'smart' strategy)
        """
        self.proxies = []
        self.current_index = 0
        self.rotation_strategy = proxy_rotation_strategy
        self.ban_time = ban_time
        self.banned_proxies = {}
        self.proxy_stats = defaultdict(lambda: {'success': 0, 'failure': 0, 'last_used': 0})
        
        # Process the provided proxies
        if proxies:
            if isinstance(proxies, list):
                self.proxies = proxies
            elif isinstance(proxies, dict):
                # Extract unique proxy URLs from the dict
                for scheme, proxy in proxies.items():
                    if proxy and proxy not in self.proxies:
                        self.proxies.append(proxy)
            elif isinstance(proxies, str):
                self.proxies = [proxies]
                
        logging.debug(f"ProxyManager initialized with {len(self.proxies)} proxies using '{proxy_rotation_strategy}' strategy")

    # ------------------------------------------------------------------------------- #

    def get_proxy(self):
        """
        Get the next proxy according to the rotation strategy
        
        :return: A proxy URL or dict mapping URL schemes to proxy URLs
        """
        if not self.proxies:
            return None
            
        # Filter out banned proxies
        available_proxies = [p for p in self.proxies if p not in self.banned_proxies or 
                            time.time() - self.banned_proxies[p] > self.ban_time]
        
        if not available_proxies:
            logging.warning("All proxies are currently banned. Using the least recently banned one.")
            # Use the least recently banned proxy
            proxy = min(self.banned_proxies.items(), key=lambda x: x[1])[0]
            # Reset its ban time
            self.banned_proxies.pop(proxy)
            return self._format_proxy(proxy)
        
        # Choose a proxy based on the strategy
        if self.rotation_strategy == 'random':
            proxy = random.choice(available_proxies)
        elif self.rotation_strategy == 'smart':
            # Choose the proxy with the best success rate and least recent usage
            proxy = max(available_proxies,
                        key=lambda p: self._calculate_proxy_score(p))
        elif self.rotation_strategy == 'weighted':
            # Weighted random selection based on success rate
            proxy = self._weighted_random_selection(available_proxies)
        elif self.rotation_strategy == 'round_robin_smart':
            # Round robin but skip recently failed proxies
            proxy = self._smart_round_robin(available_proxies)
        else:  # sequential
            if self.current_index >= len(available_proxies):
                self.current_index = 0
            proxy = available_proxies[self.current_index]
            self.current_index += 1
            
        # Update last used time
        self.proxy_stats[proxy]['last_used'] = time.time()
        
        return self._format_proxy(proxy)

    # ------------------------------------------------------------------------------- #

    def _format_proxy(self, proxy):
        """
        Format the proxy as a dict for requests
        
        :param proxy: Proxy URL
        :return: Dict mapping URL schemes to proxy URLs
        """
        if proxy.startswith('http://') or proxy.startswith('https://'):
            return {'http': proxy, 'https': proxy}
        else:
            return {'http': f'http://{proxy}', 'https': f'http://{proxy}'}

    # ------------------------------------------------------------------------------- #

    def report_success(self, proxy):
        """
        Report a successful request with the proxy
        
        :param proxy: The proxy that was used
        """
        if isinstance(proxy, dict):
            # Extract the proxy URL from the dict
            proxy_url = proxy.get('https') or proxy.get('http')
        else:
            proxy_url = proxy
            
        if proxy_url:
            self.proxy_stats[proxy_url]['success'] += 1
            if proxy_url in self.banned_proxies:
                del self.banned_proxies[proxy_url]

    # ------------------------------------------------------------------------------- #

    def report_failure(self, proxy):
        """
        Report a failed request with the proxy
        
        :param proxy: The proxy that was used
        """
        if isinstance(proxy, dict):
            # Extract the proxy URL from the dict
            proxy_url = proxy.get('https') or proxy.get('http')
        else:
            proxy_url = proxy
            
        if proxy_url:
            self.proxy_stats[proxy_url]['failure'] += 1
            self.banned_proxies[proxy_url] = time.time()

    # ------------------------------------------------------------------------------- #

    def _calculate_proxy_score(self, proxy_url):
        """
        Calculate a score for proxy selection in smart mode

        :param proxy_url: The proxy URL to score
        :return: Score (higher is better)
        """
        stats = self.proxy_stats[proxy_url]
        total_requests = stats['success'] + stats['failure']

        if total_requests == 0:
            # New proxy gets high score
            return 1.0

        # Success rate component (0-1)
        success_rate = stats['success'] / total_requests

        # Recency component (prefer less recently used proxies)
        time_since_last_use = time.time() - stats['last_used']
        recency_score = min(time_since_last_use / 300, 1.0)  # Normalize to 5 minutes

        # Combine scores (weighted)
        return (success_rate * 0.7) + (recency_score * 0.3)

    def _weighted_random_selection(self, available_proxies):
        """
        Select proxy using weighted random based on success rates

        :param available_proxies: List of available proxy URLs
        :return: Selected proxy URL
        """
        if not available_proxies:
            return None

        weights = []
        for proxy in available_proxies:
            score = self._calculate_proxy_score(proxy)
            weights.append(max(score, 0.1))  # Minimum weight to give all proxies a chance

        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(available_proxies)

        r = random.uniform(0, total_weight)
        cumulative_weight = 0

        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if r <= cumulative_weight:
                return available_proxies[i]

        return available_proxies[-1]  # Fallback

    def _smart_round_robin(self, available_proxies):
        """
        Smart round robin that skips recently failed proxies

        :param available_proxies: List of available proxy URLs
        :return: Selected proxy URL
        """
        if not available_proxies:
            return None

        # Filter out proxies that failed recently
        current_time = time.time()
        good_proxies = []

        for proxy in available_proxies:
            stats = self.proxy_stats[proxy]
            if stats['failure'] == 0:
                good_proxies.append(proxy)
            else:
                # Check if enough time has passed since last failure
                time_since_failure = current_time - self.banned_proxies.get(proxy, 0)
                if time_since_failure > 60:  # 1 minute cooldown
                    good_proxies.append(proxy)

        # Use good proxies if available, otherwise fall back to all available
        proxies_to_use = good_proxies if good_proxies else available_proxies

        # Round robin through the filtered list
        if self.current_index >= len(proxies_to_use):
            self.current_index = 0
        proxy = proxies_to_use[self.current_index]
        self.current_index += 1

        return proxy

    def get_proxy_health_report(self):
        """
        Get a health report of all proxies

        :return: Dictionary with proxy health information
        """
        report = {
            'total_proxies': len(self.proxies),
            'available_proxies': 0,
            'banned_proxies': len(self.banned_proxies),
            'proxy_details': {}
        }

        current_time = time.time()

        for proxy in self.proxies:
            stats = self.proxy_stats[proxy]
            total_requests = stats['success'] + stats['failure']
            success_rate = (stats['success'] / total_requests) if total_requests > 0 else 0

            is_banned = proxy in self.banned_proxies
            ban_time_left = 0

            if is_banned:
                ban_time_left = max(0, self.ban_time - (current_time - self.banned_proxies[proxy]))
            else:
                report['available_proxies'] += 1

            report['proxy_details'][proxy] = {
                'success_count': stats['success'],
                'failure_count': stats['failure'],
                'success_rate': success_rate,
                'total_requests': total_requests,
                'last_used': stats['last_used'],
                'is_banned': is_banned,
                'ban_time_left': ban_time_left,
                'score': self._calculate_proxy_score(proxy)
            }

        return report

    # ------------------------------------------------------------------------------- #

    def add_proxy(self, proxy):
        """
        Add a new proxy to the pool
        
        :param proxy: Proxy URL to add
        """
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            logging.debug(f"Added proxy: {proxy}")

    # ------------------------------------------------------------------------------- #

    def remove_proxy(self, proxy):
        """
        Remove a proxy from the pool
        
        :param proxy: Proxy URL to remove
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            if proxy in self.banned_proxies:
                del self.banned_proxies[proxy]
            if proxy in self.proxy_stats:
                del self.proxy_stats[proxy]
            logging.debug(f"Removed proxy: {proxy}")

    # ------------------------------------------------------------------------------- #

    def get_stats(self):
        """
        Get statistics about proxy usage
        
        :return: Dict with proxy statistics
        """
        return {
            'total_proxies': len(self.proxies),
            'available_proxies': len([p for p in self.proxies if p not in self.banned_proxies or 
                                     time.time() - self.banned_proxies[p] > self.ban_time]),
            'banned_proxies': len(self.banned_proxies),
            'proxy_stats': dict(self.proxy_stats)
        }
