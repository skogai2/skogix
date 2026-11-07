# curl Command Cheat Sheet

curl moves data over HTTP and a few dozen other protocols from the command line, and is already installed on almost every Linux, macOS, and Windows 10 or later machine. This sheet covers the flags you use daily for APIs, downloads, and finding out why a request fails.

## GET Requests

| Command | What it does |
|----|----|
| curl https://example.com | GET and print the body |
| curl http://example.com:8080/status | GET on a non-default port |
| curl -L URL | Follow redirects |
| curl -s URL | Silent: no progress meter |
| curl -sS URL | Silent, but still print errors |
| curl -f URL | Fail with exit code 22 on HTTP 4xx and 5xx instead of printing the error page |
| curl -sSfL URL | The combination scripts want |
| curl -H "Accept: application/json" URL | Ask for JSON |
| curl -A "Mozilla/5.0" URL | Set the User-Agent |
| curl -e https://example.com/ URL | Set the Referer |
| curl -b "session=abc123" URL | Send a cookie |
| curl -c jar.txt URL | Save cookies from the response to a file |
| curl -b jar.txt URL | Send cookies from that file on the next call |
| curl --compressed URL | Ask for gzip and decode it |
| curl -s URL \| jq . | Pretty-print JSON with jq |
| curl URL1 URL2 | Several URLs in one command |

## POST and JSON

-d implies POST and sets Content-Type: application/x-www-form-urlencoded, so JSON needs the header.

```bash
curl -X POST https://api.example.com/items \
  -H "Content-Type: application/json" \
  -d '{"name":"widget","qty":1}'
```

| Command | What it does |
|---|---|
| `curl -X POST -d "param=value" url` | Send standard form-encoded POST request |
| `curl --json '{"name":"widget"}' url` | Send JSON payload with automatic Content-Type header (curl 7.82+) |
| `curl -H "Content-Type: application/json" -d '{"k":"v"}' url` | Classic syntax for sending JSON data |
| `curl -d @data.json url` | Send file content in POST request body |
| `curl -X PUT -d @data.json url` | Send PUT request with file payload |

## Headers

| Command | What it does |
|---|---|
| `curl -H "Accept: application/json" url` | Pass custom request header |
| `curl -H "X-Custom-Header: value" url` | Add custom application header |
| `curl -H "Header:" url` | Remove default internal header |
| `curl -A "CustomUserAgent/1.0" url` | Set custom User-Agent string |
| `curl -e "https://ref.com" url` | Set HTTP Referer header |

## Authentication

| Command | What it does |
|---|---|
| `curl -u "user:password" url` | Basic HTTP authentication |
| `curl -H "Authorization: Bearer <TOKEN>" url` | Bearer token authorization (OAuth2 / JWT) |
| `curl --digest -u "user:pass" url` | HTTP Digest authentication |
| `curl --negotiate -u : url` | Kerberos / SPNEGO authentication |

## Downloads

| Command | What it does |
|---|---|
| `curl -O https://example.com/file.zip` | Download file saving with remote filename |
| `curl -o local_name.zip url` | Download file saving to custom local filename |
| `curl -C - -O url` | Resume an interrupted file download |
| `curl --remote-name-all url1 url2` | Download multiple URLs to their respective filenames |

## Uploads

| Command | What it does |
|---|---|
| `curl -F "file=@photo.jpg" url` | Multipart form file upload (`multipart/form-data`) |
| `curl -F "file=@photo.jpg;type=image/jpeg" url` | Upload file with custom MIME type |
| `curl -T file.zip ftp://host/` | Upload file via FTP or HTTP PUT |

## Response Headers and Status Codes

| Command | What it does |
|---|---|
| `curl -I https://example.com` | Fetch HTTP response headers only (`HEAD` request) |
| `curl -i https://example.com` | Include response HTTP headers along with response body |
| `curl -s -o /dev/null -w "%{http_code}
" url` | Print HTTP status code only (e.g. `200`, `404`) |
| `curl -D headers.txt url` | Dump response headers into a text file |

Where the time goes:

```bash
curl -s -o /dev/null -w "dns %{time_namelookup}s  connect %{time_connect}s  tls %{time_appconnect}s  first byte %{time_starttransfer}s  total %{time_total}s  code %{http_code}\n" https://example.com
```

## Verbose and Debugging

| Command | What it does |
|---|---|
| `curl -v url` | Verbose mode: display TLS handshake, headers sent and received |
| `curl -vvv url` | Very verbose mode with detailed protocol traces |
| `curl --trace trace.dump url` | Dump full raw byte stream of network session |
| `curl --trace-time url` | Prepend timestamps to each trace log line |

## Copy as cURL

Browsers and API clients export a request as a curl command, which is the quickest way to reproduce a call that works in one place and fails in another.

| Source | How to get the curl command |
|----|----|
| Chrome, Edge | Network tab, right-click the request, Copy, then Copy as cURL |
| Firefox | Network tab, right-click, Copy Value, Copy as cURL |
| Safari | Network tab, right-click the request, Copy as cURL |
| Postman | The code snippet button, then cURL |
| Insomnia, Bruno | Right-click the request, Copy as cURL |
| Swagger UI | Try it out, Execute, and the command appears above the response |
| Windows | Copy as cURL (cmd), because the bash version's single quotes break in cmd.exe |

An exported command carries your cookies and Authorization header, so strip those lines before pasting it into a ticket or an online converter. curl --libcurl out.c URL goes the other way and writes the equivalent libcurl C source.

## Certificates and -k

| Command | What it does |
|---|---|
| `curl -k url` or `curl --insecure url` | Allow insecure TLS connections (skips certificate verification) |
| `curl --cacert /path/ca.pem url` | Specify custom CA certificate bundle file |
| `curl --cert client.pem --key key.pem url` | Provide client SSL certificate and private key |

Exit code 60 means the chain did not verify. The [SSL checker](https://sshworkbench.com/tools/ssl-checker) shows what the server is sending, including a missing intermediate, and the [certificate decoder](https://sshworkbench.com/tools/certificate-decoder) reads a .pem you already have.

## Proxies

| Command | What it does |
|---|---|
| `curl -x http://proxy.corp.com:8080 url` | Route request through HTTP/HTTPS proxy |
| `curl -x socks5h://localhost:1080 url` | Route request through SOCKS5 proxy with remote DNS resolution |
| `curl -U "user:pass" -x proxy:8080 url` | Authenticate with proxy |
| `curl --noproxy "*" url` | Bypass all configured proxies |

curl -v prints Uses proxy env variable when one of those variables is set, which explains many mystery failures.

## Query Parameters

| Command | What it does |
|---|---|
| `curl -G -d "search=term" -d "page=1" url` | Construct URL with query parameters appended |
| `curl -G --data-urlencode "q=hello world" url` | Construct GET request with properly URL-encoded parameters |

## Timeouts and Retries

| Command | What it does |
|---|---|
| `curl -m 10 url` | Set maximum total operation timeout to 10 seconds (`--max-time`) |
| `curl --connect-timeout 5 url` | Maximum time allowed to establish connection |
| `curl --retry 3 --retry-delay 2 url` | Retry failed request up to 3 times with 2-second delay |

## Connectivity Checks

| Command | What it does |
|---|---|
| `curl -sSf -o /dev/null url` | Silent healthcheck (fails with non-zero exit code on HTTP errors) |
| `curl -s -o /dev/null -w "%{time_total}
" url` | Measure total round-trip response time in seconds |

For a port you cannot reach from your machine, the [SSH port checker](https://sshworkbench.com/tools/ssh-port-checker) tests it from outside your network.

## Exit Codes

| Exit Code | Meaning | Common Cause |
|---|---|---|
| `0` | Success | Request succeeded |
| `6` | Couldn't resolve host | DNS failure or invalid domain name |
| `7` | Failed to connect to host | Port closed, firewall blocking, or host down |
| `28` | Operation timeout | Server stalled beyond configured `--max-time` |
| `35` | SSL connect error | TLS version mismatch or handshake failure |
| `52` | Nothing returned | Server closed connection without sending any reply |
| `60` | SSL certificate problem | Self-signed certificate or untrusted CA |

echo $? shows the code right after curl exits. Codes are documented in man curl under EXIT CODES.

## Windows and PowerShell

| Shell | Command / Note |
|---|---|
| PowerShell | Use `curl.exe` explicitly (in older PS, `curl` is alias for `Invoke-WebRequest`) |
| CMD / Batch | Wrap JSON strings in escaped double quotes: `"{"key":"value"}"` |
| Windows Terminal | Native UTF-8 support handles all response characters cleanly |

## Install curl

curl: command not found usually means a minimal image rather than a broken machine. Alpine and the Debian slim images ship without curl, which is why it fails inside containers and CI jobs that work fine on your laptop.

| Distribution / OS | Command |
|---|---|
| Debian / Ubuntu | `sudo apt install curl` |
| Arch Linux | `sudo pacman -S curl` |
| Fedora / RHEL | `sudo dnf install curl` |
| Windows (winget) | `winget install curl.curl` |

## Gotchas

- -d already means POST. Adding -X POST is harmless alone, but -X POST with -L forces POST on the redirect target too, where curl would normally switch to GET.
- -I sends HEAD, and some servers answer HEAD with 405 or different headers. curl -sD - -o /dev/null URL shows the headers of a real GET.
- Quote every URL that contains &,?, *, [, or {. Unquoted, the shell backgrounds the command at & and curl globs the brackets. In zsh the URL never even reaches curl: you get zsh: no matches found instead.
- A curl that hangs and prints nothing is usually waiting on the connection, not on the server. --connect-timeout 5 --max-time 10 turns the wait into exit code 28, and -v shows whether it is stuck at DNS, TCP, or TLS. On a streaming endpoint the opposite is true: the data is arriving but buffered, and -N releases it.
- -d @file strips newlines from the file. --data-binary @file sends it byte for byte.
- -k makes the error go away, not the problem. Find the cause with the [SSL checker](https://sshworkbench.com/tools/ssl-checker) and fix the chain or add --cacert.
- -u user:pass is visible in shell history and ps. Use -u user to be prompted, or -n with a.netrc.
- -O overwrites an existing file without asking, and -OJ lets the server choose the file name.
- A curl that works in the terminal but not in cron or CI is usually missing a proxy variable, a.netrc, or the CA bundle the shell had.

## curl FAQ

### How do I get just the HTTP status code from curl?

curl -s -o /dev/null -w "%{http_code}\n" URL prints the code and nothing else: -s hides the progress meter, -o /dev/null throws away the body, and -w prints the variable after the transfer. Add -L if the URL redirects, or you will see 301 instead of the final code. In a script, compare it like any string: [ "$(curl -s -o /dev/null -w '%{http_code}' URL)" = 200 ]. If you want curl itself to fail on a bad code, use -f, which turns 4xx and 5xx into exit code 22; --fail-with-body (curl 7.76 and newer) does the same but still shows the error page.

### Can I run curl commands in PowerShell?

Yes, but type curl.exe, not curl. In Windows PowerShell 5.1 curl is an alias for Invoke-WebRequest, a cmdlet with different parameters, so -H, -d, and -X produce errors about ambiguous or unknown parameters. PowerShell 7 removed the alias, and cmd.exe never had it, so curl works as expected there. Quoting is the other trap: cmd.exe has no single quotes, so JSON goes in double quotes with the inner ones escaped as ", and PowerShell older than 7.3 strips embedded double quotes from arguments to native programs, so use '{"a":1}' there.

### How do I get the curl command for a request from Chrome or Postman?

In Chrome or Edge, open DevTools, pick the request in the Network tab, then right-click it and choose Copy, Copy as cURL. Firefox and Safari have the same item, and Postman emits one from its code snippet button. Two things the export will not tell you: the command carries your session cookies and Authorization header, so delete those lines before pasting it into a ticket or an online converter, and Chrome's bash export uses $'...' quoting that sh and dash reject, so run it under bash or take the dollar signs out. On Windows choose Copy as cURL (cmd), because the bash version's single quotes do not survive cmd.exe.

### How do I make curl ignore an SSL certificate error?

curl -k URL (long form --insecure) skips certificate verification and connects anyway. Use it to confirm the rest of the request works, then remove it. For a private CA, curl --cacert ca.pem URL trusts that CA without giving up verification, and CURL_CA_BUNDLE=ca.pem in the environment does the same for every call. Before reaching for -k at all, find out why verification failed: curl -vI URL prints the certificate's issuer and dates in the lines marked with an asterisk, and the SSL checker linked on this page shows whether the server is sending its intermediate certificate, which is the usual cause on a freshly configured server.

### What do curl exit codes 6, 7, 28, 35, 56, and 60 mean?

6 is DNS: the hostname did not resolve, so check spelling and your resolver. 7 is TCP: nothing accepted the connection, so the port is closed, the service is down, or a firewall refused it. 28 is a timeout from --max-time or --connect-timeout, which often means a firewall silently dropping packets. 35 is a TLS handshake failure, typically HTTPS to a plain HTTP port, a protocol or cipher mismatch, or on Windows a revocation check that could not run (--ssl-no-revoke). 56 means the connection was cut mid-transfer, usually a reset by a proxy, load balancer, or the server. 60 means the certificate did not verify: self-signed, expired, a private CA curl does not know, a missing intermediate, or a wrong system clock.

---
Source: https://sshworkbench.com/cheatsheets/curl
