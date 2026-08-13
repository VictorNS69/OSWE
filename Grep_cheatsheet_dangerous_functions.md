# Grep Cheatsheet — Dangerous Functions & Bad Practices

Companion to `Dangerous_functions_and_bad_practices.md`. Every block: `grep -rnE` (recursive, line numbers, extended regex) scoped by file extension. Adjust path (`.` below) to target dir. Drop `-r .` for single-file scans.

**Noise reduction**: prepend `--exclude-dir={node_modules,vendor,.git,dist,build}` to any command below to skip dependency/build trees, e.g.:
```bash
grep -rnE --exclude-dir={node_modules,vendor,.git,dist,build} --include=*.php 'eval\s*\(' .
```

**Faster alternative**: if `rg` (ripgrep) is installed, it respects `.gitignore` automatically and is a drop-in replacement — same `-E` pattern, no `--include`/`--exclude-dir` needed:
```bash
rg -n --type php 'eval\s*\('
```

## PHP

```bash
# Code/command execution
grep -rnE --include=*.php 'eval\s*\(|assert\s*\(|system\s*\(|exec\s*\(|shell_exec\s*\(|passthru\s*\(|popen\s*\(|proc_open\s*\(|`[^`]+`' .

# File inclusion (LFI/RFI)
grep -rnE --include=*.php '\b(include|include_once|require|require_once)\s*\(|file_get_contents\s*\(|file_put_contents\s*\(|fopen\s*\(' .

# Deserialization
grep -rnE --include=*.php 'unserialize\s*\(|phar://|file_exists\s*\(|is_file\s*\(|filemtime\s*\(' .

# Type juggling
grep -rnE --include=*.php '==[^=]|in_array\s*\(|switch\s*\(|md5\s*\(.*==|sha1\s*\(.*==' .

# Other sinks
grep -rnE --include=*.php 'extract\s*\(|create_function\s*\(|preg_replace\s*\([^)]*/e|call_user_func(_array)?\s*\(' .
```

## Cross-Language: JWT

```bash
# Disabled signature verification (PyJWT-style)
grep -rnE '(verify_signature[\x27"]?\s*[:=]\s*False|verify\s*=\s*False)' .

# Locate all decode/verify call sites for manual algorithm-pinning check
grep -rnE 'jwt\.decode\s*\(|jsonwebtoken|jwt\.verify\s*\(' .

# alg:none acceptance
grep -rnE 'alg.{0,10}none|"none"' . | grep -i jwt

# Java jjwt — algorithm sourced from token vs pinned
grep -rnE 'setSigningKey\s*\(|getAlgorithm\s*\(' .
```

## Cross-Language: Mass Assignment

```bash
# ASP.NET MVC
grep -rnE 'TryUpdateModel\s*\(|UpdateModel\s*\(' .

# Django ModelForm
grep -rnE "fields\s*=\s*['\"]__all__['\"]|exclude\s*=\s*\[" .

# Generic ORM bound directly to request body
grep -rnE '\.create\s*\(\s*req\.body\s*\)|\.update\s*\(\s*req\.body\s*\)' .

# Rails-style patterns
grep -rnE 'assign_attributes\s*\(|\.new\s*\(\s*params\[' .
```

## Cross-Language: Hardcoded Secrets / Credentials

```bash
# Literal key/value assignments for secrets
grep -rnE '(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*["\x27][A-Za-z0-9+/=_-]{8,}["\x27]' .

# Flask/Django default-left-unchanged secret
grep -rnE 'SECRET_KEY\s*=\s*["\x27].+["\x27]' .

# Locate committed .env files (not a grep, but the natural next step)
find . -name '.env' -o -name '*.env'

# .env ever committed, even if later removed
git log --all --full-history -- '**/.env' 2>/dev/null
```

## Java

```bash
# Deserialization
grep -rnE --include=*.java 'readObject\s*\(|XMLDecoder|XStream|fromXML\s*\(|enableDefaultTyping\s*\(|ObjectMapper' .

# Code execution
grep -rnE --include=*.java 'Runtime\.getRuntime\(\)\.exec|ProcessBuilder|ScriptEngine|GroovyShell|\.eval\s*\(|Class\.forName\s*\(' .

# Expression Language injection
grep -rnE --include=*.java 'Ognl\.getValue|SpelExpressionParser|parseExpression\s*\(|\$\{.*\}|#\{.*\}' .

# XXE
grep -rnE --include=*.java 'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory' .

# SQL
grep -rnE --include=*.java '\bStatement\b.*createStatement|executeQuery\s*\(.*\+' .
```

## Python

```bash
# Code execution
grep -rnE --include=*.py '\beval\s*\(|\bexec\s*\(|compile\s*\(|pickle\.(load|loads)\s*\(|yaml\.load\s*\(|subprocess\.(call|run|Popen)\s*\(.*shell\s*=\s*True|os\.system\s*\(|os\.popen\s*\(' .

# SSTI / autoescape bypass
grep -rnE --include=*.py 'Template\s*\(|render_template_string\s*\(' .
grep -rnE --include=*.py --include=*.html '\|\s*safe\b|Markup\s*\(|autoescape\s*=\s*False|\{%\s*autoescape\s+false\s*%\}' .

# Other deserialization
grep -rnE --include=*.py 'marshal\.loads\s*\(|\bshelve\b' .

# Import/reflection
grep -rnE --include=*.py '__import__\s*\(|getattr\s*\(|setattr\s*\(' .

# Bonus: unsafe yaml.load without SafeLoader (needs manual check)
grep -rnE --include=*.py 'yaml\.load\s*\(' . | grep -vE 'SafeLoader'
```

## Go

```bash
# Code/command execution
grep -rnE --include=*.go 'exec\.Command(Context)?\s*\(|syscall\.Exec\s*\(' .

# Deserialization
grep -rnE --include=*.go 'encoding/gob|gob\.NewDecoder|yaml\.Unmarshal\s*\(|plugin\.Open\s*\(' .

# Template injection
grep -rnE --include=*.go 'text/template|template\.New\s*\(.*\.Parse\s*\(|template\.(HTML|JS|URL)\s*\(' .

# SQL
grep -rnE --include=*.go 'fmt\.Sprintf\s*\(.*(SELECT|INSERT|UPDATE|DELETE)|\.Raw\s*\(|db\.Exec\s*\(' .

# Path traversal / file handling
grep -rnE --include=*.go 'os\.Open\s*\(|os\.ReadFile\s*\(|ioutil\.ReadFile\s*\(|filepath\.Join\s*\(|http\.ServeFile\s*\(' .

# SSRF
grep -rnE --include=*.go 'http\.Get\s*\(|http\.Client\{|net\.Dial(Timeout)?\s*\(' .

# Weak crypto/randomness
grep -rnE --include=*.go 'math/rand|crypto/md5|crypto/sha1|crypto/des' .

# Reflection
grep -rnE --include=*.go 'reflect\.Value|MethodByName\s*\(' .
```

## Node.js / JavaScript

```bash
# Code execution
grep -rnE --include=*.js --include=*.ts '\beval\s*\(|new Function\s*\(|vm\.runIn(Context|NewContext)\s*\(|child_process\.exec\s*\(' .

# Prototype pollution / deserialization
grep -rnE --include=*.js --include=*.ts 'lodash\.merge|_\.extend\s*\(|node-serialize|\.unserialize\s*\(' .

# Template injection
grep -rnE --include=*.js --include=*.ts 'ejs\.render\s*\(|pug\.render\s*\(' .

# SQL/NoSQL
grep -rnE --include=*.js --include=*.ts '\$where|\$ne\b|\$gt\b|find\s*\(\s*req\.(body|query)' .
```

## .NET / C#

```bash
# Deserialization
grep -rnE --include=*.cs 'BinaryFormatter|LosFormatter|ObjectStateFormatter|JavaScriptSerializer|TypeNameHandling|XmlSerializer|SoapFormatter|DataContractSerializer' .

# Code execution
grep -rnE --include=*.cs 'Process\.Start\s*\(|CSharpCodeProvider|Activator\.CreateInstance\s*\(' .

# SQL
grep -rnE --include=*.cs 'SqlCommand\s*\(.*\+|new SqlCommand' .

# XXE — XmlResolver left enabled
grep -rnE --include=*.cs 'XmlResolver\s*=\s*new XmlUrlResolver|XmlDocument\s*\(' .
```

## PostgreSQL (SQL files / inline queries)

```bash
grep -rnE --include=*.sql 'COPY .* FROM PROGRAM|lo_import|lo_export|LANGUAGE\s+(plpgsql|plpythonu)|dblink(_connect)?' .
```

---

# Bad Practices — Grep Patterns by Vulnerability Class

Many of these are pattern/heuristic hunts, not exact sinks — expect false positives, use as a triage starting point.

## SQL

```bash
grep -rnE 'SELECT\s+\*' .                                       # over-fetching columns
grep -rnE '"\s*\+\s*\w+|\.format\s*\(.*SELECT|f"[^"]*SELECT|%s.*SELECT' .   # string-built queries
grep -rnE '\.raw\s*\(|\.extra\s*\(|text\s*\(' .                  # ORM raw escape hatches
grep -rnE 'EXEC\s*\(\s*@|EXECUTE\s+' .                           # dynamic SQL in stored procs
```

## XSS

```bash
grep -rnE 'innerHTML\s*=|document\.write\s*\(|outerHTML\s*=' .   # unsafe DOM writes
grep -rnE 'dangerouslySetInnerHTML|v-html|\[innerHTML\]' .        # framework escape hatches
grep -rnE 'unsafe-inline|unsafe-eval' .                           # weak CSP
grep -rnE 'location\.href|document\.URL|document\.referrer' .     # DOM XSS sources feeding sinks
```

## PHP Type Juggling

```bash
grep -rnE --include=*.php '==\s*\$|\$\w+\s*==' .                                                  # loose comparison
grep -rnE --include=*.php 'in_array\s*\([^,]+,[^,]+\)\s*;|array_search\s*\([^,]+,[^,]+\)\s*;' .   # missing strict 3rd param
grep -rnE --include=*.php 'is_numeric\s*\(' .                                                      # weak numeric validation
```

## Deserialization (cross-language, generic)

```bash
grep -rnE 'unserialize\s*\(|ObjectInputStream|BinaryFormatter|pickle\.(load|loads)|yaml\.load\s*\(' .   # untrusted-input deserialization sinks
grep -rnE '__wakeup|__destruct|__toString' .                     # PHP magic methods
```

## SSTI

```bash
grep -rnE 'Template\s*\(\s*\w*(input|param|request)|render_template_string\s*\(' .
```

## XXE

```bash
grep -rnE 'setFeature\s*\(.*external-general-entities|DTD|DocumentBuilderFactory|XmlDocument\(' .   # parser config not hardened
grep -rnE '\.svg"|\.docx"|\.xlsx"|Content-Type.*xml' .           # XML-bearing upload paths
```

## CSRF / CORS

```bash
grep -rnE 'Access-Control-Allow-Origin' .                         # CORS header handling — check for wildcard/reflection
grep -rnE 'SameSite\s*=\s*(Lax|None)' .                           # cookie attribute weaker than Strict
grep -rnE 'request\.headers\[.Origin.\]|req\.get\s*\(.Origin.\)' . # Origin reflected without allowlist check
```

## SSRF

```bash
grep -rnE '127\.0\.0\.1|localhost' . | grep -iE 'block|deny|filter'   # incomplete blacklists
grep -rnE 'requests\.get\s*\(|http\.Get\s*\(|urlopen\s*\(|fetch\s*\(' .   # outbound requests to user-supplied URLs
```

## WebSocket

```bash
grep -rnE 'WebSocket|new WebSocket|ws://|wss://' .                # handshake/connection sites — check origin validation nearby
grep -rnE 'origin\s*===|checkOrigin|verifyClient' .               # existing origin-check logic to audit
```

## NoSQL Injection

```bash
grep -rnE '\$where|find\s*\(\s*req\.(body|query|params)\s*\)' .
```

## Prototype Pollution

```bash
grep -rnE '__proto__|constructor\.prototype|Object\.assign\s*\(.*req\.(body|query)' .   # pollution-prone key access
grep -rnE 'merge\s*\(|deepmerge\s*\(|_\.extend\s*\(' .                                   # deep-merge utilities to audit for key blocking
```

## LDAP Injection

```bash
grep -rnE 'DirContext\.search|NamingEnumeration|ldap_search\s*\(|ldap_bind\s*\(|DirectorySearcher|search_s\s*\(' .
```

## XPath Injection

```bash
grep -rnE 'XPath\.evaluate|XPathExpression|->xpath\s*\(|DOMXPath|SelectNodes|SelectSingleNode|etree\.XPath' .
```

## Open Redirect

```bash
grep -rnE 'header\s*\(\s*"Location:|sendRedirect\s*\(|Response\.Redirect\s*\(|res\.redirect\s*\(|HttpResponseRedirect\s*\(' .
```

## Zip Slip / Archive Path Traversal

```bash
grep -rnE 'extractall\s*\(|ZipInputStream|getName\s*\(\s*\)|extract-zip|adm-zip|ZipArchive::extractTo' .
```

## JNDI Injection / Log Injection (Log4Shell-class)

```bash
grep -rnE 'InitialContext\.lookup\s*\(|\$\{jndi:|logger?\.(info|warn|error|debug)\s*\(' .
```

## ReDoS

```bash
grep -rnE 'Regex\.Match\s*\(|re\.(match|search)\s*\(|preg_match\s*\(|Pattern\.compile\s*\(|new RegExp\s*\(' .
```

## Weak Cryptography / Insecure Randomness

```bash
grep -rnE 'mt_rand\s*\(|\brand\s*\(|md5\s*\(|sha1\s*\(' .                    # PHP
grep -rnE 'java\.util\.Random|MessageDigest\.getInstance\s*\(\s*"MD5"' .     # Java
grep -rnE '\brandom\.(random|randint|choice)\s*\(|hashlib\.(md5|sha1)\s*\(' . # Python
grep -rnE 'Math\.random\s*\(' .                                              # Node
grep -rnE 'System\.Random' .                                                 # .NET
grep -rnE '\bECB\b|\bDES\b|\bRC4\b' .                                        # weak ciphers, all langs
```

## File Upload / Path Traversal

```bash
grep -rnE 'move_uploaded_file\s*\(|Files\.copy\s*\(|FileOutputStream|multer\s*\(|SaveAs\s*\(' .
```
