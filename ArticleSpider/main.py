import sys
import os
from scrapy.cmdline import execute

# Set project directory, make execute available.
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
execute(['scrapy', 'crawl', 'jobbole'])
