
detect = {
    'good': [
        { 'q': 'What language is this?', },
        { 'q': 'Que idioma es?', },
    ],
}
detect['bad'] = []

translate = {
    'good': [
        { 'q': 'What language is this?', 'source': 'en', 'target': 'es', },
    ],

    'bad': detect['bad'],
}

languages = {
    'good': [],
    'bad': [],
}

test_parameters = {
    '/detect': detect ,
    '/languages': languages ,
    '/translate': translate ,
} 

