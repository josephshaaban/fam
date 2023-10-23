"""
A module for some helper functions and classes.
"""


def dict_depth(d) -> int:
    """
    A helper function to discover the depth of multi-level dictionary.

    If the field has value of type list of dicts, this function
    will calculate the depth of list's dicts with the upper levels.

    Returns the depth of d
    """
    if isinstance(d, list) and len(d):
        return 0 + max(dict_depth(item) for item in d)
    if isinstance(d, dict) and len(d):
        return 1 + max(dict_depth(item) for item in d.values())
    return 0

def dict_fields_with_levels(d, object_fields=set(), array_fields=set()):
    """
    A helper function to explores all nested fields with respect to its type
    (dict field or list field).
    This helps to deal with fields that need to normalize and the ones that
    need to cast its dtype for SQLAlchemy.

    Returns a tuple of two sets represented as object_fields, array_fields
    """
    for r in d:
        if not isinstance(r,(dict, list)):
            continue
        for k, val in r.items():
            if isinstance(val, dict):
                object_fields.add(k)
                if dict_depth(val):
                    dict_fields_with_levels(val, object_fields, array_fields)
            elif isinstance(val, list):
                array_fields.add(k)
                if dict_depth(val):
                    dict_fields_with_levels(val, object_fields, array_fields)
    return object_fields, array_fields

def sub_fields_depth(data_dict, fields, prefix='data'):
  deep_fields = []
  for field in fields:
    depth = dict_depth(data_dict[field])
    if depth:
      deep_fields.append(field)
      print(f'{field} has depth of: {depth}')

  if len(deep_fields) == 0:
    print(f'All {prefix} fields with 0 depth.')


# see https://stackoverflow.com/a/19829714
class AutoVivification(dict):
    """
    A class that implements nested dictionaries

    Implementation of perl's autovivification feature.
    """
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


class CustomDict(AutoVivification):
    """A helper class adds depth property"""
    @property
    def depth(self):
        return dict_depth(self)