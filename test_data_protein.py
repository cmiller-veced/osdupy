

# valid UniProtKB accession

proteins = {
    'good': [
        { 'accession': 'A2BC19', },
        { 'accession': 'P12345', },
        { 'accession': 'A0A023GPI8', },
        { 'accession': 'P62988', },
    ],
    'bad': [ 
        [],
        'xxxxxxx',
        { 'accession': 'xxxxxxxx', },
    ],
}
proteins['bad'] = []
proteins_accession = {
    'good': proteins['good'],
    'bad': [ ],
}

epitope = {
    'good': proteins['good'],
    'bad': proteins['bad'],
}

proteome = {
    'good': [
        { 'upid': 'UP000005640', },    # but empty result
    ],
    'bad': proteins['bad'],
}


test_parameters = {
    '/proteins': proteins ,
    '/proteins/{accession}': proteins_accession ,
#    '/antigen/{accession}': antigen ,
    '/epitope': epitope ,
    '/proteomes': proteome ,
    '/proteomes/{upid}': proteome ,
    '/proteomics': proteome ,
} 


