# pdm-audit

<!--- BADGES: START --->
[![PyPI version](https://badge.fury.io/py/pdm-audit.svg)](https://pypi.org/project/pdm-audit)
<!--- BADGES: END --->

A PDM plugin that scans your Python project dependencies for known vulnerabilities. It leverages pip-audit to provide security auditing capabilities within your PDM workflow.

## Features

* Multiple vulnerability data sources support
  * PyPI vulnerability database via the [PyPI JSON API](https://warehouse.pypa.io/api-reference/json.html)
  * [OSV](https://osv.dev/docs/) database support
* Multiple output formats:
  * Columnar (default)
  * JSON
  * Markdown
* Caching support with configurable time-to-live (TTL)
* Seamless integration with PDM's dependency management

## Installation

```bash
pdm self add pdm-audit-plugin
```

## Usage

Run `pdm audit` in your project directory:

```bash
pdm audit --help
```

### Command Options

```
Options:
  -s, --service           The audit source. Default is PyPI, can be pypi, osv.
  -f, --format           The format to emit audit results in (choices: columns, json, markdown)
  --desc                 Include vulnerability descriptions (auto, on, off)
  --enable-cache         Enable the vulnerability query result cache
  --cache-ttl           The cache time-to-live in seconds (default: 1800)
```

## Examples

Basic audit of project dependencies:
```bash
pdm audit
```

Using OSV as the vulnerability database:
```bash
pdm audit -s osv
```

Output in JSON format:
```bash
pdm audit -f json
```

Output in Markdown format:
```bash
pdm audit -f markdown
```

Disable caching:
```bash
pdm audit --enable-cache false
```

Customize cache TTL to 1 hour:
```bash
pdm audit --cache-ttl 3600
```

## Security Model

This plugin inherits its security model from pip-audit. Please note:

* It identifies known vulnerabilities in your dependencies based on data from vulnerability databases
* It cannot detect undisclosed vulnerabilities or perform static code analysis
* The audit is only as accurate as the vulnerability data available in the chosen service (PyPI or OSV)

## Cache Management

The plugin maintains a cache of vulnerability data to improve performance:

* Default cache location: `.audit_cache` in your project directory
* Default TTL: 1800 seconds (30 minutes)
* Cache can be disabled or customized via command options

## Troubleshooting

### Slow Audit Performance
* First-time audits may be slower due to cache population
* Subsequent audits will be faster if caching is enabled
* Consider adjusting cache TTL if needed

### Connection Issues
If you encounter connection errors:
* Verify your internet connection
* Check if you're behind a corporate proxy
* Try switching between PyPI and OSV services

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
