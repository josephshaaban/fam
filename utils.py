def dict_depth(d):
    if isinstance(d, list) and len(d):
        return 0 + max(dict_depth(item) for item in d)
    if isinstance(d, dict) and len(d):
        return 1 + max(dict_depth(item) for item in d.values())
    return 0

def dict_fields_with_levels(d, object_fields=set(), array_fields=set()):
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

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


class CustomDict(AutoVivification):
    @property
    def depth(self):
        return dict_depth(self)