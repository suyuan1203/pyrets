pyrets
======

Using python3, it supports the login, search, getmetadata and logout transaction.

    rets_session = pyrets.RetsSession(user, passwd, user_agent, rets_version, login_url, user_agent_passwd)
    response_text = rets_session.login()
    print(response_text)

	#getmetadata
    metadata_text = rets_session.getmetadata()
    with open('./12meta.xml','w') as f:
        f.write(metadata_text)
    
    #getobject    
    object_bin = rets_session.getobject('Photo','Property','40621107:1')
	with open('./a.jpg', 'wb') as f:
	    f.write(object_bin)
	    
	#search
	response = rets_session.search('Property', 'RE_1', '(L_ListingID=40621107)', 1, 'L_UpdateDate')
	print(response)

    response_text = rets_session.logout()  
    print(response_text)

