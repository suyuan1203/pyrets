pyrets
======

Using python3, this library implements the login, search, getmetadata, logout function.

rets_session = pyrets.RetsSession(user, passwd, user_agent, rets_version, login_url, user_agent_passwd)
response_text = rets_session.login()
print(response_text)

metadata_text = rets_session.getmetadata()
with open('./12meta.xml','w') as f:
    f.write(metadata_text)

response_text = rets_session.logout()  
print(response_text)