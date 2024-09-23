




# TODO: change name   NO
# TODO: pass schema instead of validator?
def validate_examples(validator, good_ones, bad_ones):    # NWS
    for thing in good_ones:
        assert validator.is_valid(thing)
    for thing in bad_ones:
        assert not validator.is_valid(thing)


def validation_practice_nws():    # NWS
  try:
    components = get_component_schemas_nws()
    parameters = components['parameters']
    schemas = components['schemas']
    aa = parameters['AlertArea']
#     msg = f'''
#     components.schemas N == {len(cs_keys)}
#     components.parameters N == {len(cprs_keys)}
#     components.parameters - components.schemas N == {len(fu)}
#     '''
#     print(msg)

    # Now for some actual validation.
    validator = Draft7Validator(parameters['AlertZone'], format_checker=FormatChecker())
    # zones.
    # Note: incompatible with area, point, region, region_type.
    good_ones = [[], ['COC123'], ['COZ123']]
    bad_ones = ['' ,['CO'] ,['CO123'] ,'' ]
    validate_examples(validator, good_ones, bad_ones)

    rc = schemas['RegionCode']
    al = schemas['Alert']

    assert schemas['Time'] == parameters['Time']

    vt = Draft7Validator(schemas['Time'], format_checker=FormatChecker())
    vt.schema = schemas['Time']
    good_ones = ['0000', '1955', '2359']
    bad_ones = ['2400', '2500', '09', '1111111', 'x']
    validate_examples(vt, good_ones, bad_ones)

    vd = Draft7Validator(schemas['Date'], format_checker=FormatChecker())
    good_ones = ['2000-01-01']
    bad_ones = ['1999', 'x', 1999, 1111111, 99]
    validate_examples(vd, good_ones, bad_ones)

    vp = Draft7Validator(schemas['Point'], format_checker=FormatChecker())
    vp.schema = schemas['Point']     # ugh.  complex

    vz = Draft7Validator(schemas['Zone'], format_checker=FormatChecker())
    vz.schema = schemas['Zone']
    good_ones = [{}, dict(timeZone=['MT'])]
    bad_ones = ['', 
                dict(foo=1)  # because additionalProperties is False
                ]
    validate_examples(vz, good_ones, bad_ones)

    return schemas
  finally:
    globals().update(locals())


