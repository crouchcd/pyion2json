import unittest
import json
import amazon.ion.simpleion as ion
from pyion2json import ion_cursor_to_json

_ION_NULLS = """[
    null,
    null.null,       // Identical to unadorned null
    null.bool,
    null.int,
    null.float,
    null.decimal,
    null.timestamp,
    null.string,
    null.symbol,
    null.blob,
    null.clob,
    null.struct,
    null.list,
    null.sexp
]"""
_JSON_NULLS = json.dumps([
    None
] * 14)

_ION_BOOLS = """[
    true,
    false
]"""
_JSON_BOOLS = json.dumps([
    True,
    False
])

_ION_INTS = """[
    0,          // Zero.  Surprise!
    -0,         //   ...the same value with a minus sign
    123,        // A normal int
    -123,       // Another negative int
    0xBeef,     // An int denoted in hexadecimal
    0b0101,    // An int denoted in binary
    1_2_3,     // An int with underscores
    0xFA_CE,    // An int denoted in hexadecimal with underscores
    0b10_10_10, // An int denoted in binary with underscores
]"""
_JSON_INTS = json.dumps([
    0,
    -0,
    123,
    -123,
    0xBeef,
    0b0101,
    123,
    0xFACE,
    0b101010
])

_ION_DECIMALS = """[
    0.123,
    -0.12d4,
    0D0,
    0.,
    -0d0,
    -0.,
    -0d-1,
    123_456.789_012
]"""
_JSON_DECIMALS = json.dumps([
    0.123,
    -0.12e4,
    0e0,
    0.,
    -0e0,
    -0.,
    -0e-1,
    123456.789012
])

_ION_TIMESTAMPS = """[
    2007-02-23T12:14Z,            // Seconds are optional, but local offset is not
    2007-02-23T12:14:33.079-08:00,    // A timestamp with millisecond precision and PST local time
    2007-02-23T20:14:33.079Z,         // The same instant in UTC ("zero" or "zulu")
    2007-02-23T20:14:33.079+00:00,    // The same instant, with explicit local offset
    2007-02-23T20:14:33.079-00:00,   // The same instant, with unknown local offset
    2007-01-01T00:00-00:00,           // Happy New Year in UTC, unknown local offset
    2007-01-01,                       // The same instant, with days precision, unknown local offset
    2007-01-01T,                      //    The same value, different syntax.
    2007-01T,                         // The same instant, with months precision, unknown local offset
    2007T,                            // The same instant, with years precision, unknown local offset
    2007-02-23,                       // A day, unknown local offset 
    2007-02-23T00:00Z,                // The same instant, but more precise and in UTC
    2007-02-23T00:00+00:00,           // An equivalent format for the same value
    2007-02-23T00:00:00-00:00       
]"""
_JSON_TIMESTAMPS = json.dumps([
    '2007-02-23 12:14:00+00:00',
    '2007-02-23 12:14:33.079000-08:00',
    '2007-02-23 20:14:33.079000+00:00',
    '2007-02-23 20:14:33.079000+00:00',
    '2007-02-23 20:14:33.079000',
    '2007-01-01 00:00:00',
    '2007-01-01 00:00:00',
    '2007-01-01 00:00:00',
    '2007-01-01 00:00:00',
    '2007-01-01 00:00:00',
    '2007-02-23 00:00:00',
    '2007-02-23 00:00:00+00:00',
    '2007-02-23 00:00:00+00:00',
    '2007-02-23 00:00:00'
])

_ION_STRINGS = """[
    "",                     // An empty string value
    " my string ",          // A normal string
    "\\"",                   // Contains one double-quote character
    "\uABCD",               // Contains one unicode character
    xml::"<e a='v'>c</e>",  // String with type annotation 'xml'
    
    ( '''hello '''     // Sexp with one element
  '''world!'''  ),
    ("hello world!"),   // The exact same sexp value
    // This Ion value is a string containing three newlines. The serialized
    // form's first newline is escaped into nothingness.
    '''\
    The first line of the string.
    This is the second line of the string,
    and this is the third line.
    '''
]"""
_JSON_STRINGS = json.dumps([
    '',
    ' my string ',
    '"',
    '\uABCD',
    '<e a=\'v\'>c</e>',
    ['hello world!'],
    ['hello world!'],
    '''\
    The first line of the string.
    This is the second line of the string,
    and this is the third line.
    '''
])

_ION_SYMBOLS = """[
    'myVar2',     // A symbol
    myVar2,       // The same symbol
    myvar2,       // A different symbol
    'hi ho',      // Symbol requiring quotes
    '\\'ahoy\\'',   // A symbol with embedded quotes
    ''           // The empty symbol
]"""
_JSON_SYMBOLS = json.dumps([
    'myVar2',
    'myVar2',
    'myvar2',
    'hi ho',
    '\'ahoy\'',
    ''
])

_ION_BLOBS = """[
    // A valid blob value with zero padding characters.
    {{
        +AB/
    }},

    // A valid blob value with one required padding character.
    {{ VG8gaW5maW5pdHkuLi4gYW5kIGJleW9uZCE= }},

    // A valid blob value with two required padding characters.
    {{ dHdvIHBhZGRpbmcgY2hhcmFjdGVycw== }}
]"""
_JSON_BLOBS = json.dumps([
    '+AB/',
    'VG8gaW5maW5pdHkuLi4gYW5kIGJleW9uZCE=',
    'dHdvIHBhZGRpbmcgY2hhcmFjdGVycw=='
])

_ION_CLOBS = """[
    {{ "This is a CLOB of text." }},

    shift_jis ::
    {{
    '''Another clob with user-defined encoding, '''
    '''this time on multiple lines.'''
    }}
]"""
_JSON_CLOBS = json.dumps([
    'This is a CLOB of text.',
    'Another clob with user-defined encoding, this time on multiple lines.'
])

_ION_STRUCTS = """[
    { },                                 // An empty struct value
    { first : "Tom" , last: "Riddle" },  // Structure with two fields
    {"first":"Tom","last":"Riddle"},     // The same value with confusing style
    {center:{x:1.0, y:12.5}, radius:3},  // Nested struct
    { x:1, },                            // Trailing comma is legal in Ion (unlike JSON)
    { "":42 },                           // A struct value containing a field with an empty name
    { field_name: annotation:: value }
]"""
_JSON_STRUCTS = json.dumps([
    {},
    {'first': 'Tom', 'last': 'Riddle'},
    {'first': 'Tom', 'last': 'Riddle'},
    {'center': {'x': 1.0, 'y': 12.5}, 'radius': 3},
    {'x': 1, },
    {'': 42},
    {'field_name': 'value'}
])

_ION_LISTS = """[
    [],                // An empty list value
    [1, 2, 3],         // List of three ints
    [ 1 , two ],       // List of an int and a symbol
    [a , [b]]         // Nested list
]"""
_JSON_LISTS = json.dumps([
    [],
    [1, 2, 3],
    [1, 'two'],
    ['a', ['b']],
])

_ION_SEXPS = """[
    (),                // An empty expression value
    (cons 1 2),        // S-expression of three values
    ([hello][there]),  // S-expression containing two lists
    (a+-b),
    ( 'a' '+-' 'b' ),
    (a.b;),
    ( 'a' '.' 'b' ';')
]"""
_JSON_SEXPS = json.dumps([
    [],
    ['cons', 1, 2],
    [['hello'], ['there']],
    ['a', '+-', 'b'],
    ['a', '+-', 'b'],
    ['a', '.', 'b', ';'],
    ['a', '.', 'b', ';']
])


class TestPyIonToJson(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.maxDiff = None

    def test_ion_null(self):
        """Check that Ion `null` types convert to JSON `null`
        """
        ion_cursor = ion.loads(_ION_NULLS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_NULLS)

    def test_ion_bool(self):
        """Check that Ion `bool` types convert to JSON `bool`
        """
        ion_cursor = ion.loads(_ION_BOOLS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_BOOLS)

    def test_ion_int(self):
        """Check that Ion `int` types convert to JSON `number`
        """
        ion_cursor = ion.loads(_ION_INTS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_INTS)

    def test_ion_decimal(self):
        """Check that Ion `decimal` types convert to JSON `number`
        """
        ion_cursor = ion.loads(_ION_DECIMALS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_DECIMALS)

    def test_ion_timestamp(self):
        """Check that Ion `timestamp` types convert to JSON `string`
        """
        ion_cursor = ion.loads(_ION_TIMESTAMPS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_TIMESTAMPS)

    def test_ion_string(self):
        """Check that Ion `string` types convert to JSON `string`
        """
        ion_cursor = ion.loads(_ION_STRINGS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_STRINGS)

    def test_ion_symbol(self):
        """Check that Ion `symbol` types convert to JSON `string`
        """
        ion_cursor = ion.loads(_ION_SYMBOLS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_SYMBOLS)

    def test_ion_blob(self):
        """Check that Ion `blob` types convert to JSON `string`
        """
        ion_cursor = ion.loads(_ION_BLOBS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_BLOBS)

    def test_ion_clob(self):
        """Check that Ion `clob` types convert to JSON `string`
        """
        ion_cursor = ion.loads(_ION_CLOBS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_CLOBS)

    def test_ion_struct(self):
        """Check that Ion `struct` types convert to JSON `object`
        """
        ion_cursor = ion.loads(_ION_STRUCTS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_STRUCTS)

    def test_ion_list(self):
        """Check that Ion `list` types convert to JSON `array`
        """
        ion_cursor = ion.loads(_ION_LISTS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_LISTS)

    def test_ion_sexp(self):
        """Check that Ion `sexp` types convert to JSON `array`
        """
        ion_cursor = ion.loads(_ION_SEXPS)
        json_rows = ion_cursor_to_json(ion_cursor)
        self.assertEqual(json.dumps(json_rows), _JSON_SEXPS)


if __name__ == '__main__':
    unittest.main()
