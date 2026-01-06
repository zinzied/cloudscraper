import os
import re
from setuptools import setup, Extension
try:
    from Cython.Build import cythonize
    import platform
    # Check if we have a compiler (very basic check)
    HAS_COMPILER = True
    if platform.system() == 'Windows':
        # Just a hint, building wheels usually happens in a controlled env
        pass
except ImportError:
    HAS_COMPILER = False
    def cythonize(extensions, **kwargs):
        return []
from io import open

with open(os.path.join(os.path.dirname(__file__), 'cloudscraper', '__init__.py'), 'r', encoding='utf-8') as fp:
    VERSION = re.match(r'.*__version__ = \'(.*?)\'', fp.read(), re.S).group(1)

with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()

setup(
    name = 'ai-cloudscraper',
    author='Zied Boughdir',
    author_email='zied.boughdir@gmail.com',
    version='3.7.6',
    packages = ['cloudscraper', 'cloudscraper.captcha', 'cloudscraper.interpreters', 'cloudscraper.user_agent'],
    ext_modules = [],  # No Cython compilation needed
    py_modules = [],
    python_requires='>=3.8',
    description = 'Enhanced Python library to bypass Cloudflare\'s anti-bot protection with cutting-edge anti-detection technologies, including TLS fingerprinting, ML optimization, and behavioral simulation.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url = 'https://github.com/zinzied/cloudscraper',
    keywords = [
        'cloudflare',
        'scraping',
        'ddos',
        'scrape',
        'webscraper',
        'anti-bot',
        'waf',
        'iuam',
        'bypass',
        'challenge',
        'tls-fingerprinting',
        'anti-detection',
        'stealth',
        'machine-learning',
        'behavioral-simulation',
        'canvas-spoofing',
        'webgl-spoofing',
        'fingerprint-resistance',
        'automation',
        'turnstile'
    ],
    include_package_data = True,
    install_requires = [
        'requests >= 2.31.0',
        'requests_toolbelt >= 1.0.0',
        'pyparsing >= 3.1.0',
        'pyOpenSSL >= 24.0.0',
        'pycryptodome >= 3.20.0',
        'js2py >= 0.74',
        'brotli >= 1.1.0',
        'certifi >= 2024.2.2',
        'ai-urllib4 >= 2.0.0'
    ],
    extras_require={
        'ai': ['ddddocr', 'ultralytics', 'google-generativeai'],
        'browser': ['playwright', 'py-parkour>=3.0.0'],
        'hybrid': ['tls-chameleon>=2.0.0', 'py-parkour>=3.0.0'],
        'all': ['ddddocr', 'ultralytics', 'playwright', 'tls-chameleon>=2.0.0', 'py-parkour>=3.0.0', 'google-generativeai']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'Environment :: Web Environment',
        'Framework :: AsyncIO'
    ]
) 