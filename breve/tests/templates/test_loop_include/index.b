html [
    head [ title [ v.title ] ],
    body [
        [ include ( 'include', params = { 'count': _v } )
          for _v in range ( 3 ) ]
    ]
] 
