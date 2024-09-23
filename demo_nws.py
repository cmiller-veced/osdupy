



def nws_education():
  try:
    rs = raw_swagger(local.swagger.nws)
    ep_names = endpoint_names(rs)
    with_refs = jsonref.loads(json.dumps(rs))

    stationId = 'KRCM'    # OK
    stationId = 'CO100'   # OK
    learning_about_parameters = True
    learning_about_parameters = False
    if learning_about_parameters:
        # Learning about the parameters
        ep = '/stations/{stationId}/observations'

        info = rs['paths'][ep]
        assert len(info) in [1, 2]
        info = rs['paths'][ep]['get']

        pinfo = rs['paths'][ep]['get']['parameters']
        xinfo = with_refs['paths'][ep]['get']['parameters']
#            ainfo = xinfo[4]
#            einfo = xinfo[2]
        for param in xinfo:   # list
            binfo = param
            pname = binfo['name']
            assert binfo['in'] == 'query'
            if 'style' in binfo:
                assert binfo['style'] == 'form'
                # `point` does not have style.
                # and has inline schema.
            if 'explode' in binfo:
                assert binfo['explode'] in [True, False]
            print(pname)
        return
  finally:
    globals().update(locals())


def nws_calls():
  try:
    rs = raw_swagger(local.swagger.nws)
    ep_names = endpoint_names(rs)
    with_refs = jsonref.loads(json.dumps(rs))
    with httpx.Client(base_url=local.api_base.nws) as client:

        params = {}
        zones = False
        zones = True
        if zones:
            ep = '/zones'
            r = client.get(ep, params=params)
            things = r.json()['features']
            for zthing in things:
                print(zthing['id'])
            assert r.status_code == 200
        return

        ep = '/alerts'
        ep = '/alerts/active'

        no_parameters = True
        no_parameters = False
        if no_parameters:
            r = client.get(ep)
            assert r.status_code == 200
            foo = r.json()
            assert type(foo) is dict
            # OK.  There is a successful GET request.
            for key in foo:
                print(key, len(str(foo[key])))
            features = foo['features']
            print(len(features))
            for feat in features:
                fprops = feat['properties']
                ns = namespacify(fprops)
                assert type(fprops) is dict
                head = fprops['headline']
    #            print(head)
                zones = fprops['affectedZones']
                # eg ['https://api.weather.gov/zones/county/FLC027']
                # forecast/PZZ475']
                # forecast/PKZ001']
                # county/COC001']
                print(zones)
            print('------------------------')
            for key in feat:
                print(key, len(str(feat[key])))
            # OK.  
            # That was a successful GET request with NO parameters.
            # Sends back a complex json doc.

        with_parameters = False
        with_parameters = True
        if with_parameters:    # GET request with parameters.

            params = {'AlertArea': 'PK'}      # AlertArea not recognized
            params = {'AlertZone': 'PK'}      # AlertZone not recognized
            params = {'area': 'KS'}
            params = {'area': 'PK'}
            params = {'area': 'CO'}
            params = {'area': ['CO']}
            # https://www.weather.gov/nwr/eventcodes
            params = {
                'area': ['CO'],
                'event': ['Winter Weather Advisory'],
                #            'event': ['Freeze Warning'],  No such event ????
                }
            r = client.get(ep, params=params)
            foo = r.json()
            assert r.status_code == 200
            # OK.  That was a successful GET request WITH parameters.
            # TODO: cleanup.
            # This has all been super quick & dirty but now we have successful NWS
            # call with parameters.
            # Much more to learn about the API but the basic work is done.
            feats = foo['features']
            for feat in feats:
                feature_properties = feat['properties']
                feature_event = feat['properties']['event']

        params = {}
        more_alerts = True
        more_alerts = False
        if more_alerts:
            ep = '/alerts/active/count'
            r = client.get(ep, params=params)
            count = r.json()
            assert r.status_code == 200
            # Shows region, area and zone names

            ep = '/alerts/active/zone/'
            zone = 'forecast/COZ082'    # NO
            zone = 'COZ082'    # Pikes Peak
            ep = f'/alerts/active/zone/{zone}'
            r = client.get(ep, params=params)
            pp = r.json()
            assert r.status_code == 200

            ep = f'/alerts/types'
            r = client.get(ep, params=params)
            ets = r.json()['eventTypes']
            assert r.status_code == 200

        glossary = True
        glossary = False
        if glossary:
            ep = '/glossary'
            r = client.get(ep, params=params)
            things = r.json()['glossary']
            for gthing in things:
                print(gthing['term'])
            assert r.status_code == 200

        icons = True
        icons = False
        if icons:
            ep = '/icons'
            r = client.get(ep, params=params)
            things = r.json()['icons']
            for ithing in things:
                print(ithing)
            assert r.status_code == 200

        params = {'area': 'CO'}   # bad parameter.  Find station parameters.
        sinfo = rs['paths']['/stations']['get']['parameters']
        params = {'state': 'CO'}   # 
        stations = True
        stations = False
        if stations:
            ep = '/stations'
            r = client.get(ep, params=params)
            rj = r.json()
            names = r.json()['observationStations']
            things = r.json()['features']
            for sthing in things: 
                print(sthing)
            assert r.status_code == 200
            nom = names[-1]
            station = things[-1]
            # 'stationIdentifier': 'COOPCOS'
            # Colorado Springs Municipal Airport
            # Other interesting info in sthing.


        params = {}
        observations = True
        observations = False
        if observations:
            stationId = 'COOPCOS'   # Not Found
            stationId = 'KRCM'    # OK
            stationId = 'CO100'   # OK
            ep = f'/stations/{stationId}/observations/latest'
            r = client.get(ep, params=params)
            props = r.json()['properties']
            for othing in props:
                print(othing)
            temp = props['temperature']
            assert r.status_code == 200


        products = True
        products = False
        if products:
            ep = '/products'
            r = client.get(ep, params=params)
            context = r.json()['@context']
            things = r.json()['@graph']
            for pthing in things: 
                print(pthing)
            assert r.status_code == 200

  finally:
    globals().update(locals())


# TODO: how to get good stationId ???
