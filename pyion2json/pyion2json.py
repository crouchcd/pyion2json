import amazon.ion.simpleion as ion
from base64 import b64encode as base64encode


def _is_ion_null(ion_val):
    return isinstance(ion_val, ion.IonPyNull)


def _is_ion_int(ion_val):
    return isinstance(ion_val, ion.IonPyInt) and ion_val.ion_type == ion.IonType.INT


def _is_ion_bool(ion_val):
    return isinstance(ion_val, ion.IonPyInt) or isinstance(ion_val, ion.IonPyBool) and ion_val.ion_type == ion.IonType.BOOL


def _is_ion_float(ion_val):
    return isinstance(ion_val, ion.IonPyFloat)


def _is_ion_decimal(ion_val):
    return isinstance(ion_val, ion.IonPyDecimal)


def _is_ion_timestamp(ion_val):
    return isinstance(ion_val, ion.IonPyTimestamp)


def _is_ion_symbol(ion_val):
    return isinstance(ion_val, ion.IonPySymbol)


def _is_ion_string(ion_val):
    return isinstance(ion_val, ion.IonPyText)


def _is_ion_clob(ion_val):
    return isinstance(ion_val, ion.IonPyBytes) and ion_val.ion_type == ion.IonType.CLOB


def _is_ion_blob(ion_val):
    return isinstance(ion_val, ion.IonPyBytes) and ion_val.ion_type == ion.IonType.BLOB


def _is_ion_struct(ion_val):
    return isinstance(ion_val, ion.IonPyDict)


def _is_ion_list(ion_val):
    return isinstance(ion_val, ion.IonPyList)


def _default_blob_decoder(blob):
    # TODO: verify this is handles all cases
    return base64encode(blob).decode('utf-8')


def _default_clob_decoder(clob):
    # TODO: verify this is handles all cases
    return clob.decode('utf-8')


def ion_to_json(ion_val, blob_decoder=None, clob_decoder=None):
    """ Down-convert an Ion value into a type that can be serialized by `json.dump`.
    The official rules to perform the conversion are located
    at: http://amzn.github.io/ion-docs/guides/cookbook.html#down-converting-to-json.

    :param ion_val: An Amazon Ion value
    :type ion_val: `IonType(<ANY>)`

    :param blob_decoder: Function that will be used to decode blobs
    :type blob_decoder: `function(blob) -> str`, optional

    :param clob_decoder: Function that will be used to decode clobs
    :type clob_decoder: `function(clob) -> str`, optional

    :raises `Exception`: If the type of `ion_val` isn't handled

    :return: JSON serializable type converted from ion_val
    :rtype: `any`
    """
    if _is_ion_null(ion_val):
        # Nulls of any type are converted to JSON null
        return None
    elif _is_ion_int(ion_val):
        # Arbitrary precision integers are printed as JSON number with precision preserved
        return ion_val
    elif _is_ion_bool(ion_val):
        # Convert BOOL to JSON True/False
        return True if ion_val == 1 else False
    elif _is_ion_float(ion_val):
        # Floats are printed as JSON number with nan and +-inf converted to JSON null
        if 'inf' in str(ion_val) or 'nan' in str(ion_val):
            return None
        return ion_val
    elif _is_ion_decimal(ion_val):
        # Decimals are printed as JSON number with precision preserved
        return float(ion_val)
    elif _is_ion_timestamp(ion_val):
        # Timestamps are printed as JSON string
        return str(ion_val)
    elif _is_ion_symbol(ion_val):
        # Symbols are printed as JSON string
        return ion_val.text
    elif _is_ion_string(ion_val):
        # Strings are printed as JSON string
        return str(ion_val)
    elif _is_ion_clob(ion_val):
        # Clobs are ASCII-encoded for characters between 32 (0x20) and 126 (0x7e),
        # inclusive. Characters from 0 (0x00) to 31 (0x1f) and from 127 (0x7f) to
        # 255 (0xff) are escaped as Unicode code points U+00XX
        if clob_decoder:
            return clob_decoder(ion_val)
        return _default_clob_decoder(ion_val)
    elif _is_ion_blob(ion_val):
        # Blobs are printed as Base64-encoded JSON strings
        if blob_decoder:
            return blob_decoder(ion_val)
        return _default_blob_decoder(ion_val)
    elif _is_ion_struct(ion_val):
        # Structs are printed as JSON object
        return {key: ion_to_json(ion_val[key]) for key in ion_val.keys()}
    elif _is_ion_list(ion_val):
        # Lists are printed as JSON array
        # S-expressions are printed as JSON array
        return list(map(ion_to_json, ion_val))
    raise Exception(f'Unhandled conversion for {type(ion_val)}')


def ion_cursor_to_json(ion_cursor, blob_decoder=None, clob_decoder=None):
    """ Down-convert each row of an iterable of Ion objects
    into a JSON serializable list

    :param ion_cursor: The Ion iterable (e.g. cursor from QLDB)
    :type ion_cursor: `iterable`

    :param blob_decoder: Function that will be used to decode blobs
    :type blob_decoder: `function(blob) -> str`, optional

    :param clob_decoder: Function that will be used to decode clobs
    :type clob_decoder: `function(clob) -> str`, optional

    :return: A JSON list
    :rtype: `list(<JSON>)`
    """
    return list(map(
        lambda row: ion_to_json(row, blob_decoder=blob_decoder,
                                clob_decoder=clob_decoder),
        ion_cursor
    ))
