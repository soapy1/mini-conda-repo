# Mini Conda Repo (mcr)

This little repo aims to provide a simple test conda repository that supports basic authentication.

## Run the server

To run the server with auth
```
$ pixi run serve
```

This server will be available at http://localhost:8000 with the credentials username `admin`, and password `password123`.

Or, run the server without auth
```
MCR_NO_AUTH=true pixi run serve
```

## Try it out with conda

Use the provided `condarc` at the root of this project to auth against the test channel.

```
$ CONDARC=<path to this repo>/condarc conda search test-package
Loading channels: done
# Name                       Version           Build  Channel             
test-package                     0.1               0       
```

You can also check that without providing auth, the channel rejects the search request:
```
 $ conda search test-package -c http://localhost:8000 --override-channels
Loading channels: failed

CondaHTTPError: HTTP 401 Unauthorized for url <http://localhost:8000/linux-64/repodata.json>
Elapsed: 00:00.002285

The remote server has indicated you are using invalid credentials for this channel.

You may need to:
  (a) Remove or update the invalid token from your configuration, or
  (b) Provide conda with a valid token directly.

Further configuration help can be found at <https://conda.io/docs/config.html>.
```
