## Dangerous functions list
This is a reference list of dangerous functions/sinks by language, organized around the vulnerability classes OSWE covers (RCE, deserialization, SSTI, SQLi, etc.).
### PHP
**Code/Command execution**
- `eval()` — executes arbitrary PHP code
- `assert()` — pre-PHP 8, evaluated string arguments as code
- `system()`, `exec()`, `shell_exec()`, `passthru()`, `popen()`, `proc_open()` — OS command execution
- `` `backticks` `` — shell execution operator

**File inclusion (LFI/RFI → RCE)**
- `include()`, `include_once()`, `require()`, `require_once()` — especially with user-controlled paths
- `file_get_contents()`, `file_put_contents()`, `fopen()` — path traversal / log poisoning primitives

**Deserialization**
- `unserialize()` — classic PHP Object Injection (POP chains)
- `phar://` stream wrapper deserialization via file ops (`file_exists`, `is_file`, `filemtime`, etc.)

**Type juggling danger zones**
- `==` (loose comparison) — `"0e123" == "0e456"` magic hash issues
- `in_array()`, `switch` — without strict mode (third param `true`)
- `md5()`/`sha1()` comparisons with `==`

**Other**
- `extract()` — variable injection from arrays (e.g. `$_GET`)
- `create_function()` — deprecated, internally uses `eval()`
- `preg_replace()` with `/e` modifier (removed in PHP 7+, but seen in legacy code)
- `call_user_func()`, `call_user_func_array()` — with user-controlled callback names

### Java
**Deserialization**
- `ObjectInputStream.readObject()` — classic Java deserialization gadget chains (ysoserial)
- `XMLDecoder.readObject()`
- XStream `.fromXML()` without allowlist
- Jackson `ObjectMapper` with `enableDefaultTyping()` / polymorphic type handling

**Code execution**
- `Runtime.getRuntime().exec()`, `ProcessBuilder` — OS command injection
- `ScriptEngine.eval()` (Nashorn/JS engine), Groovy `Eval`/`GroovyShell.evaluate()`
- `MethodInvocation`/reflection with user-controlled class names (`Class.forName()`)

**Expression Language injection**
- OGNL evaluation (Struts) — `Ognl.getValue()`
- SpEL — `SpelExpressionParser.parseExpression().getValue()`
- EL in JSP — `${}`/`#{}` with unsanitized input

**XXE**
- `DocumentBuilderFactory`, `SAXParserFactory`, `XMLInputFactory` — without disabling external entities/DTDs

**SQL**
- `Statement` (vs `PreparedStatement`) with string concatenation

### Python
**Code execution**
- `eval()`, `exec()` — arbitrary code execution
- `compile()` combined with `exec`/`eval`
- `pickle.load()`/`pickle.loads()` — deserialization RCE
- `yaml.load()` without `Loader=yaml.SafeLoader`
- `subprocess.call/run/Popen` with `shell=True` and unsanitized input
- `os.system()`, `os.popen()`

**Template injection (SSTI) / autoescape bypass**
- Jinja2 `Template(user_input).render()` — direct SSTI if user controls template string
- `render_template_string()` (Flask) with unsanitized input
- Jinja2 `|safe` filter, `Markup()`, `{% autoescape false %}` — explicitly disables auto-escaping on a variable/block, reopening XSS even when the engine is otherwise safe
- Flask `Markup(user_input)` / `app.jinja_env.autoescape = False` — global autoescape disable

**Other deserialization**
- `marshal.loads()`
- `shelve` module (uses pickle internally)

**Import/reflection**
- `__import__()` with user-controlled module names
- `getattr()`/`setattr()` chains on user input (attribute-injection primitives)

### Go
**Code/Command execution**
- `os/exec.Command()` — safe if args are passed separately, but dangerous when built via `sh -c` with concatenated user input, or when the command/binary name itself is user-controlled
- `os/exec.CommandContext()` — same risk as above
- `syscall.Exec()` — direct process execution

**Deserialization**
- `encoding/gob` — decodes into arbitrary registered types; gadget-chain risk similar to other native serializers if attacker controls the stream and types are registered broadly
- `encoding/json` with `interface{}`/`any` targets — not RCE by itself, but enables type-confusion bugs when downstream code type-asserts unpredictably
- `gopkg.in/yaml.v2` / `yaml.v3` `Unmarshal()` — historically had unsafe defaults in some third-party forks; check for `UnmarshalStrict` usage
- `plugin.Open()` — loads and executes a `.so` file dynamically; if the path or the plugin itself is attacker-influenced, arbitrary code execution

**Template injection (SSTI)**
- `text/template` — **no auto-escaping**; if used for HTML output instead of `html/template`, this is a direct XSS/SSTI-adjacent sink
- `html/template` — auto-escapes, but `template.HTML()`, `template.JS()`, `template.URL()` type conversions on user input bypass that escaping (equivalent to `dangerouslySetInnerHTML`)
- Both packages: if the **template string itself** (not just the data) is built from user input via `template.New().Parse(userInput)`, that's full SSTI

**SQL**
- `database/sql` `Query()`/`Exec()` with `fmt.Sprintf()`-built query strings instead of parameterized placeholders (`?`/`$1`)
- ORM raw query escape hatches — GORM's `.Raw()`, `.Exec()` with string concatenation

**Path traversal / file handling**
- `os.Open()`, `os.ReadFile()`, `ioutil.ReadFile()` — with unsanitized/unjoined user path input (no built-in traversal protection; must use `filepath.Clean()` + prefix check, not `filepath.Join()` alone since `Join` doesn't stop `..`)
- `archive/zip`, `archive/tar` `Reader` — Zip Slip equivalent; extracting entries via `header.Name` without validating against `..` traversal
- `net/http.ServeFile()` — vulnerable to traversal if the path parameter isn't cleaned (Go's docs explicitly warn about this)

**SSRF**
- `net/http.Get()`/`http.Client.Do()` with a user-supplied URL/host and no allowlist or redirect validation
- `net.Dial()`/`net.DialTimeout()` — raw socket connections to user-controlled hosts

**XXE / XML**
- `encoding/xml` — Go's standard XML decoder does **not** expand external entities by default (safer than Java/PHP/.NET out of the box), but third-party libraries (e.g. some libxml2 bindings) may not share that protection — worth verifying which parser is actually in use

**Weak crypto / randomness**
- `math/rand` — **not** cryptographically secure; using it for tokens, session IDs, or password reset codes is a common OSWE-style bug (should be `crypto/rand`)
- `crypto/md5`, `crypto/sha1` — weak for password hashing (should be `bcrypt`/`argon2` via `golang.org/x/crypto`)
- `crypto/des`, ECB mode usage via `crypto/cipher` — weak cipher choices

**Reflection**
- `reflect.Value.Call()` / `reflect.Value.MethodByName()` — invoking methods by attacker-controlled name string, similar risk profile to Java reflection or PHP `call_user_func()`

### Node.js / JavaScript
**Code execution**
- `eval()`
- `Function()` constructor — `new Function(userInput)()`
- `vm.runInContext()`, `vm.runInNewContext()` — sandbox escapes are common
- `child_process.exec()` — shell injection (vs `execFile` which is safer)

**Deserialization / prototype pollution**
- `JSON.parse()` — generally safe, but merge/extend utilities (`lodash.merge`, `_.extend`, custom deep-merge) are classic prototype pollution sinks
- `node-serialize` package `.unserialize()` — known RCE gadget

**Template injection**
- Server-side template engines (`ejs.render()`, `pug.render()`) with user-controlled template strings

**SQL/NoSQL**
- String-concatenated queries; MongoDB operator injection via unsanitized objects (`$where`, `$ne`, etc. from JSON body)

### .NET / C#
**Deserialization** (huge OSWE focus area)
- `BinaryFormatter.Deserialize()` — the classic one, deprecated but everywhere in legacy code
- `LosFormatter.Deserialize()` — ViewState deserialization
- `ObjectStateFormatter`
- `JavaScriptSerializer` with `SimpleTypeResolver`
- `Json.NET` (`Newtonsoft.Json`) with `TypeNameHandling` set to `Auto`/`All`/`Objects`
- `XmlSerializer`/`SoapFormatter.Deserialize()`
- `DataContractSerializer` with known types manipulation

**Code execution**
- `Process.Start()` — command execution
- `CSharpCodeProvider`/`Microsoft.CodeAnalysis` (Roslyn) dynamic compilation
- Reflection: `Activator.CreateInstance()` with user-controlled type names

**SQL**
- `SqlCommand` built via string concatenation instead of parameterized queries

### PostgreSQL
- `COPY ... FROM PROGRAM` — direct OS command execution from SQL
- `lo_import`/`lo_export` (large object functions) — file read/write primitives
- `CREATE FUNCTION ... LANGUAGE plpgsql/plpythonu` — if untrusted procedural languages are enabled, arbitrary code execution
- `dblink`/`dblink_connect` — can be abused for SSRF-like internal connections

### JWT
- `jwt.decode(token, options={"verify_signature": False})` (PyJWT) — signature check disabled
- `jwt.decode(token, verify=False)` — older PyJWT API, same issue
- `jsonwebtoken.verify()` (Node) called with `algorithms` not pinned — allows `alg: none` or RS256/HS256 confusion (attacker signs with public key as HMAC secret)
- `jjwt`/`java-jwt` `.setSigningKey()` accepting the algorithm from the token header instead of pinning it server-side

### Mass Assignment Binders
- ASP.NET MVC `UpdateModel()`/`TryUpdateModel()` without an explicit include-list — over-posting lets attacker set fields not shown on the form (e.g. `IsAdmin`)
- Django `ModelForm` with `fields = '__all__'` or `exclude` instead of an explicit `fields` allowlist
- Rails-style `.new(params[...])`/`assign_attributes` without strong-parameter filtering (pattern shows up in Rails-influenced frameworks generally)
- Any ORM's `Model.create(req.body)` / `Model.update(req.body)` pattern — binds the entire request body straight to model attributes

### Hardcoded Secrets / Credentials
- API keys, DB passwords, JWT signing secrets, encryption keys embedded directly in source (`.env` committed to VCS, config files with literal secrets, connection strings with plaintext credentials)
- Default/example secrets shipped in framework boilerplate and never rotated (e.g. Flask/Django `SECRET_KEY` left as scaffold default)
## Bad practices list
This is a reference list of bad-practices breakdown by vulnerability type.
### SQL
- **`SELECT *`** — leaks columns you didn't intend to expose (password hashes, tokens, internal flags) if the result set is ever serialized to JSON/API output; also breaks blind-SQLi enumeration assumptions when column count matters for `UNION` attacks, and makes it harder to reason about what an injected query actually returns
- **String concatenation/interpolation into queries** instead of parameterized queries/prepared statements — the root cause of virtually all SQLi
- **Dynamic table/column names built from user input** — parameterization doesn't help here since identifiers can't be bound as params; needs allowlisting
- **Blind trust in ORM "raw" escape hatches** (`.raw()`, `.extra()`, `text()` in SQLAlchemy, `Model.query()` in Sequelize with string interpolation) — devs assume the ORM protects them everywhere, but raw/literal methods bypass that
- **Second-order SQLi** — sanitizing input on write but trusting it blindly on a later read/reuse (classic OSWE exam trap)
- **Overly permissive DB user privileges** — app DB user with `FILE`, `SUPER`, or `COPY PROGRAM`-equivalent rights turns SQLi into RCE
- **Verbose SQL error messages returned to the client** — enables error-based injection instead of forcing blind techniques
- **Stored procedures built via dynamic SQL internally** (`EXEC(@sql)` in MSSQL, similar in Postgres `EXECUTE`) — pushes the injection risk into the DB layer where devs feel falsely safe

### XSS
- **Directly writing user input into HTML** without context-aware output encoding (HTML entity encode for body, JS-string escape for `<script>` context, URL-encode for attributes/URLs)
- **Using `innerHTML`, `document.write()`, `outerHTML`** instead of `textContent`/`innerText` on untrusted data
- **`dangerouslySetInnerHTML` (React), `v-html` (Vue), `[innerHTML]` (Angular bypass)** — explicit escape hatches devs reach for without sanitizing first
- **Blacklist-based filtering** (stripping `<script>` tags) instead of allowlist encoding — trivially bypassed with alternate vectors (`onerror`, `svg`, `javascript:` URIs)
- **Reflecting input into JS context without escaping** — e.g. `var x = "USER_INPUT";` lets an attacker break out with a quote
- **Trusting `Content-Type` sniffing** — serving user-uploaded files without a strict `Content-Type`/`X-Content-Type-Options: nosniff`, allowing HTML/JS execution from uploaded files
- **Weak/missing CSP**, or CSP with `unsafe-inline`/`unsafe-eval` — defeats the point of the mitigation
- **DOM XSS sinks** — `location.href`, `document.URL`, `document.referrer` fed into `eval`, `innerHTML`, `setTimeout(string)`, `setAttribute('href'/'src')` without validation

### PHP Type Juggling
- **Loose comparison (`==`, `switch`) on attacker-controlled values**, especially against hashes — `"0e12345" == "0e67890"` both juggle to `0`
- **`in_array()`/`array_search()` without strict mode** (missing third `true` param)
- **Comparing user password/token input with `==` instead of `hash_equals()`** — also opens timing-attack risk
- **Relying on `is_numeric()` alone** for validation — accepts scientific notation, hex-like strings in older PHP, leading to unexpected juggling downstream

### Deserialization
- **Deserializing user-controlled input at all**, in any language, without integrity verification (HMAC/signature) beforehand
- **PHP**: `unserialize()` on cookies/session data/cache values; autoloading classes that have exploitable `__wakeup()`/`__destruct()`/`__toString()` magic methods
- **Java**: using `ObjectInputStream` on untrusted streams; polymorphic deserialization left enabled in Jackson/XStream/Fastjson without a class allowlist
- **.NET**: `BinaryFormatter`/`SoapFormatter`/`LosFormatter` on any untrusted data; `JSON.NET` with `TypeNameHandling.All`; unencrypted/unsigned ViewState (`MachineKey` misconfig or defaults)
- **Python**: `pickle` on anything from a network boundary, cache, or queue message; `yaml.load()` instead of `safe_load()`
- **General**: trusting that "it's internal" data (Redis cache, message queue, cookie) is safe to deserialize just because it didn't come directly from an HTTP body

### SSTI
- **Passing user input directly as the template string** (`Template(user_input)`, `render_template_string(user_input)`) instead of only as template _variables_
- **Concatenating user input into a template before rendering** — even indirectly, e.g. building an email/report template from a user-supplied "name" field
- **Trusting "harmless" template contexts** (search results pages, error messages, "welcome {name}" banners) — these are the classic places SSTI hides
- **Not sandboxing the template engine** when user-authored templates are a legitimate feature (e.g. letting users customize an email template) — needs a restricted execution environment, not the default engine

### XXE
- **Not disabling DTDs/external entities** on XML parsers — this is the default-insecure state for many older Java (`DocumentBuilderFactory`), .NET, and libxml-based parsers
- **.NET specifically**: `XmlDocument.XmlResolver` left as default (non-null) — pre-.NET Framework 4.5.2 this resolves external entities out of the box; even on patched versions, explicitly setting `XmlResolver = new XmlUrlResolver()` reintroduces the hole
- **Accepting XML from any user-facing endpoint that "shouldn't" involve XML** — SOAP fallbacks, SVG uploads (SVG is XML), DOCX/XLSX uploads (zipped XML), RSS/Atom import features
- **Enabling external entity resolution "just in case"** for legacy SOAP interoperability without an allowlist
- **Trusting client-supplied `Content-Type`** to decide whether to parse as XML

### CSRF / CORS
- **Missing or predictable CSRF tokens**, or tokens not tied to session/validated server-side
- **Accepting CSRF token from a request param but not enforcing it on state-changing GET requests**
- **`Access-Control-Allow-Origin: *` combined with `Access-Control-Allow-Credentials: true`** — technically invalid per spec but misconfigured proxies/frameworks sometimes allow it
- **Reflecting the `Origin` header back into `Access-Control-Allow-Origin`** without an allowlist — makes CORS trust _any_ origin
- **Relying on `SameSite` cookies alone** without CSRF tokens for high-value actions — `SameSite=Lax` still allows top-level navigation GETs
- **Trusting `Referer`/`Origin` header presence/absence as the sole CSRF defense** — headers can be stripped by some clients/proxies

### SSRF
- **No allowlist on outbound request destinations** — app fetches any URL the user supplies (webhooks, "import from URL", PDF generators, image proxies)
- **Blacklisting `127.0.0.1`/`localhost` only** — misses `0.0.0.0`, IPv6 `::1`, decimal/octal/hex IP encodings, DNS rebinding, and cloud metadata IPs (`169.254.169.254`)
- **Not validating redirects** — first request passes the filter, but the server follows a redirect to an internal resource
- **Trusting internal services to not need auth** "because SSRF can't reach them anyway" — the false assumption that causes real damage once SSRF lands

### WebSocket
- **No origin validation on the WebSocket handshake** — allows cross-site WebSocket hijacking (CSWSH), since the browser's SOP doesn't restrict WS connections the way it does `fetch`/XHR
- **Relying on cookies alone for WS auth** without a CSRF-equivalent token in the handshake, given CSWSH bypasses SOP
- **Treating WebSocket messages as inherently trusted** once the connection is authenticated — not re-validating/sanitizing each message server-side (injection points reappear per-message)

### NoSQL Injection
- **Passing raw JSON body/query params directly into query objects** (e.g. MongoDB `find(req.body)`) — lets attackers inject operators like `$ne`, `$gt`, `$where`
- **`$where` clauses built from string concatenation** — this is basically `eval()` inside MongoDB
- **Not type-checking input** before it reaches the query builder — a string field expecting a scalar receiving an object silently changes query semantics

### Prototype Pollution
- **Deep-merge/extend utilities operating on user-controlled keys** without blocking `__proto__`, `constructor`, `prototype`
- **Recursive `JSON.parse()` + merge patterns** for config/settings objects sourced from user input
- **Trusting that pollution "just breaks things"** rather than treating it as a gadget chain precursor — in Node apps it frequently chains into RCE via polluted `child_process` options or template engine settings

### LDAP Injection
- **Java**: `DirContext.search()`, `NamingEnumeration` built from concatenated filter strings
- **PHP**: `ldap_search()`, `ldap_bind()` with unsanitized DN/filter strings
- **.NET**: `DirectorySearcher.Filter` set via string concatenation
- **Python**: `ldap3`/`python-ldap` `search_s()` with unsanitized filters

### XPath Injection
- **Java**: `XPath.evaluate()`, `XPathExpression.evaluate()`
- **PHP**: `SimpleXMLElement->xpath()`, `DOMXPath->query()`
- **.NET**: `XmlDocument.SelectNodes()`/`SelectSingleNode()` with concatenated XPath
- **Python**: `lxml.etree.XPath()` with user input

### Open Redirect
- **PHP**: `header("Location: " . $_GET['url'])`
- **Java**: `response.sendRedirect()`
- **.NET**: `Response.Redirect()`, `RedirectResult`
- **Node**: `res.redirect()`
- **Python**: Flask `redirect()`, Django `HttpResponseRedirect()`

### Zip Slip / Archive Path Traversal
- **Python**: `tarfile.extractall()`, `zipfile.extractall()` — extracted entry names can contain `../`
- **Java**: `ZipInputStream` + manual `getName()` used to build output paths without normalization
- **Node**: `extract-zip`, `adm-zip` used without path validation
- **PHP**: `ZipArchive::extractTo()`

### JNDI Injection / Log Injection (Log4Shell-class)
- **Java**: `InitialContext.lookup()` on attacker-influenced strings; `Logger.log()`/`logger.info()` when the logging library resolves lookup patterns (`${jndi:...}`) inside logged strings — the actual Log4Shell mechanism
- **General**: any logging call that writes raw user input without neutralizing format-string-like syntax

### ReDoS (Regex Denial of Service)
- **All languages**: `Regex.Match()` (.NET), `re.match()`/`re.search()` (Python), `preg_match()` (PHP), `String.matches()`/`Pattern.compile()` (Java), `RegExp.test()` (JS) — when the pattern itself (not just the input) is attacker-influenced, or when a vulnerable pattern with catastrophic backtracking is applied to attacker-controlled input

### Weak Cryptography / Insecure Randomness
Occasionally touches token-prediction bugs:
- **PHP**: `mt_rand()`, `rand()` (not cryptographically secure — use `random_bytes()`/`random_int()`); `md5()`/`sha1()` for password hashing (use `password_hash()`)
- **Java**: `java.util.Random` (predictable seed — use `SecureRandom`); `MessageDigest.getInstance("MD5")` for passwords
- **Python**: `random` module for tokens/session IDs (use `secrets`); `hashlib.md5()`/`sha1()` for passwords
- **Node**: `Math.random()` for tokens (use `crypto.randomBytes()`)
- **.NET**: `System.Random` (predictable — use `RNGCryptoServiceProvider`/`RandomNumberGenerator`)
- **All**: ECB cipher mode, hardcoded IVs/keys, `DES`/`RC4` usage

### File Upload / Path Traversal (as its own class, not folded into LFI)
- **PHP**: `move_uploaded_file()` with unsanitized destination path; trusting client-supplied `Content-Type` or extension
- **Java**: `Files.copy()`/`FileOutputStream` built from user-supplied filename
- **Node**: `multer` disk storage with user-controlled `filename` callback
- **.NET**: `Request.Files[...].SaveAs()` with unsanitized path

### JWT
- **Accepting `alg: none`** — server skips signature verification entirely if the token header says so and the library isn't pinned to expected algorithms
- **Algorithm confusion (RS256 → HS256)** — server verifies with the public key as if it were an HMAC secret, letting an attacker self-sign a token using the (often-known) public key
- **Not verifying signature at all** during development/debugging (`verify_signature: False`) and shipping that config to production
- **Weak/predictable/short HMAC secrets** — brute-forceable offline once a valid token is captured
- **Trusting claims (`role`, `isAdmin`) without re-validating server-side state** — JWT is a bearer credential, not a source of truth for authorization that can change (revoked/demoted users still "valid" until expiry)
- **No expiry (`exp`) enforcement, or accepting already-expired tokens** due to missing/incorrect validation

### Mass Assignment
- **Binding the entire request body/params object directly to a model/entity** without an explicit allowlist of bindable fields — lets an attacker set fields never exposed on the form (`isAdmin`, `role`, `balance`, `userId` on someone else's record)
- **Relying on the client to only send expected fields** — the request is attacker-controlled; extra JSON keys are free for the attacker to add
- **Framework "convenience" binders** (`ModelForm(fields='__all__')`, `UpdateModel()` without includes, ORM `create(req.body)`) — designed for trusted input, misapplied to user input

### Hardcoded Secrets / Credentials
- **Committing `.env`, config files, or connection strings with real credentials** to version control — history persists even after later removal/rotation
- **Shipping framework scaffold secrets unchanged** (default `SECRET_KEY`, default admin passwords) to production
- **Embedding API keys/tokens in client-side JS** — anything shipped to the browser is public regardless of minification/obfuscation
- **Logging secrets** (auth headers, full request bodies with tokens) to application logs that have broader read access than the secret itself warrants

