html [
    head [ title [ v.title ] ],
    body [
        div [
            include ( 'include' ),
	    check ( v.do_fail ) and span [ "_x should be undefined %s" % _x ]
        ]
    ]  
]