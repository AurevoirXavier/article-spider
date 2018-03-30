import sys
import os
from scrapy.cmdline import execute

# Set project directory, make execute available.
sys.path.append(os.path.dirname(os.path.abspath('main.py')))
execute(['scrapy', 'crawl', 'jobbole'])
