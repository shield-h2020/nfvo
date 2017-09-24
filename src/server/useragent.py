def get_user_agent(request):
    user_agent = ""
    try:
        user_agent = request.environ["HTTP_USER_AGENT"]
    except:
        pass
    return user_agent
