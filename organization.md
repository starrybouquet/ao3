
# Top-Down Organization Planning

### Important:
- separating HTML and I/O
- making sense organizationally
- working for an eventual package (?needs more research?)
- consider: separating AO3-specific and general fanwork requirements to allow for integration of other archives for historical analysis

### Tree

```
src
|
+-- init
|
+-- utils
|     |
|     +-- I/O utils
|     +-- parse utils
|     +-- other utils
|
+-- I/O
|     |
|     +-- get work data
|     +-- get tag data
|     +-- get user-specific data
|
+-- parsing
|     |
|     +-- work class
|     |     data on an AO3 work
|     |     |
|     |     +-- possible private work subclass?
|     |
|     +-- user class
|           store access codes
|           kudos
|           bookmarks
```
