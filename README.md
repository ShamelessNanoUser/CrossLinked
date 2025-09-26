<div align="center">
    <h1>CrossLinked</h1>
</div>

CrossLinked is a LinkedIn enumeration tool that uses search engine scraping to collect valid employee names from an 
organization. This technique provides accurate results without the use of API keys, credentials, or accessing 
LinkedIn directly!

# Install

### Python
Install the most recent code from GitHub:
```bash
git clone https://github.com/ShamelessNanoUser/CrossLinked
cd CrossLinked
pip3 install -r requirements.txt
playwright install
```

# Prerequisites
CrossLinked assumes the organization's account naming convention has already been identified. This is required for execution and should be added to the CMD args based on your expected output. See the [Naming Format](#naming-format) and [Example Usage](#example-usage) sections below:

### Naming Format
```text
{first}.{last}                      = john.smith
{f}{last}@company.com               = jsmith@company.com
{first}.{middle}.{last}@company.com = john.the.smith@company.com
CMP\{first}{l}                      = CMP\johns
```

# Search
By default, CrossLinked will use `google` and `duckduckgo` search engines to identify employees of the target organization. To do so a playwright browser is used. This playwright browser pauses after opening the starting URL. Doing so, allows the user to perform the CAPTCHA. After completing this, the browser must be continued manually to finish execution. After execution, two files (`names.txt` & `names.csv`) will appear in the current directory, unless modified in the CMD args.

* *names.txt* - List of unique user accounts in the specified format.
* *names.csv* - Raw search data. See the `Parse` section below for more.


## Example Usage
```bash
python3 crosslinked.py -f '{f}.{last}@domain.com' company_name
```


```bash
python3 crosslinked.py -f '{first}.{middle}.{last}@domain.com' -t 15 -j 2 company_name
```
> ⚠️ For best results, use the company name as it appears on LinkedIn `"Target Company"` not the domain name.


# Command-Line Arguments
```
positional arguments:
  company_name        Target company name

options:
  -h, --help          show this help message and exit
  -t TIMEOUT          Max timeout per search (Default=15)
  -j JITTER           Jitter between requests (Default=3)
  -c CLICKS           amount of pages to view on the search engine (Default=5)

Search arguments:
  --search ENGINE     Search Engine (Default='duckduckgo,google,bing')

Output arguments:
  -f NFORMAT          Format names, ex: '{f}.{last}@domain.com', '{first}.{middle}.{last}@domain.com'
  -o OUTFILE          Change name of output file (omit_extension)

Proxy arguments:
  --proxy PROXY       Proxy requests (IP:Port)
  --proxy-file PROXY  Load proxies from file for rotation

```

