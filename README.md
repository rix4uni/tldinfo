## tldinfo

Accurately separates a URL's subdomain, domain, and public suffix, using the Public Suffix List (PSL).

### Performance

tldinfo is optimized for high-performance processing of large URL lists:
- **Parallel processing**: Automatically utilizes all CPU cores for processing multiple URLs
- **Optimized extraction**: Single instance reuse eliminates repeated PSL loading overhead
- **Batch I/O**: Efficient output handling reduces system call overhead
- **100x+ faster** on multi-core systems when processing large URL lists

## Installation
```
git clone https://github.com/rix4uni/tldinfo.git
cd tldinfo
python3 setup.py install
```

## pipx
Quick setup in isolated python environment using [pipx](https://pypa.github.io/pipx/)
```
pipx install --force git+https://github.com/rix4uni/tldinfo.git
```

## Usage
```
usage: tldinfo [-h] [-e EXTRACT] [-r] [-f] [-j] [-s] [-v]

Accurately separates a URL’s subdomain, domain, and public suffix, using the Public Suffix List (PSL).

options:
  -h, --help            show this help message and exit
  -e EXTRACT, --extract EXTRACT
                        Comma-separated list of parts to extract (subdomain, domain, suffix)
  -r, --registered_domain
                        Get the registered domain
  -f, --fqdn            Get the fqdn
  -j, --json            Output result in JSON format
  -s, --silent          Run without printing the banner
  -v, --version         Show current version of tldinfo
```

## Example usages
Single Domains:
```bash
▶ echo "http://forums.news.cnn.com/" | tldinfo --silent --extract subdomain
forums.news

▶ echo "http://forums.news.cnn.com/" | tldinfo --silent --extract domain
cnn

▶ echo "http://forums.news.cnn.com/" | tldinfo --silent --extract suffix
com

▶ echo "http://forums.news.cnn.com/" | tldinfo --silent --extract domain,suffix
cnn.com

▶ echo "http://forums.news.cnn.com/" | tldinfo --silent --extract subdomain,domain,suffix
forums.news.cnn.com

▶ echo "http://forums.news.cnn.com/" | tldinfo --silent --extract subdomain,domain,suffix --json
{"input": "http://forums.news.cnn.com/", "subdomain": "forums.news", "domain": "cnn", "suffix": "com"}

▶ echo "http://forums.news.cnn.com/" | tldinfo --silent --registered_domain
cnn.com

▶ echo "http://forums.news.cnn.com/" | tldinfo --silent --fqdn
forums.news.cnn.com
```

Multiple Domains:
```bash
▶ cat targets.txt
forums.news.cnn.com
forums.bbc.co.uk
www.worldbank.org.kg
```

```bash
▶ cat targets.txt | tldinfo --silent --extract subdomain
forums.news
forums
www
```

## Thanks :pray:
- [tldextract](https://github.com/john-kurkowski/tldextract)