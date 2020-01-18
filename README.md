# pyion2json

Convert an [Amazon Ion](http://amzn.github.io/ion-docs/) document(s) to JSON

## Install

```
pip install pyion2json
```

## Usage

### Convert individual Ion values

```
import json
import amazon.ion.simpleion as ion
from pyion2json import ion_to_json

json_doc = ion_to_json(
    ion.loads('{ first: "Tom" , last: "Riddle" }')
)
json.dumps(json_doc, indent=' ')

```

> Outputs:

```
{
 "first": "Tom",
 "last": "Riddle"
}
```

### Convert a cursor from QLDB

```
from pyion2json import ion_cursor_to_json

with create_qldb_session() as qldb_session:
    qldb_cursor = qldb_session.execute_statement('SELECT first,last FROM Users')
    json_rows = ion_cursor_to_json(qldb_cursor)
    json.dumps(json_rows, indent=' ')

```

> Outputs:

```
[
 {
  "first": "Harry",
  "last": "Potter"
 },
 {
  "first": "Tom",
  "last": "Riddle"
 }
]
```

## TODO:

1. Verify BLOB conversion meets expectations
2. Verify CLOB conversion meets expectations
