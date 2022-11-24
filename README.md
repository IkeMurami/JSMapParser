# SourceMap downloader

That small util:

- gets a list of javascript's urls 
- downloads sourcemap files (if they are accessable)
- other way that util downloads javascript files and beautify them 
- parses sourcemap files

/js_src — downloaded javascript files  
/sourcemap_src — downloaded sourcemap files  
/sourcemap_src/src — recovered a javascript project from sourcemap files

# Usage

1. Set the `base_dir` path in `main.py` script:

```
PS D:\MyProjects\BugBounty\web\partners\services\partners> dir

    Directory: D:\MyProjects\BugBounty\web\partners\services\partners

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---          24.11.2022    19:50           3274 js.list
```

2. Put a `js.list` file with urls to js-files. Example of `js.list` file:

```
https://example.com/client/static/vendor.23f32.js
https://example.com/blabla/test/static123/client.28aab32.js
```

3. Install requirements and run script:

```
python3 -m pip install requirements.txt
python3 .\main.py
```