DBConfigDict = {
    "Atlas": {
        "user": "user2",  # enter your own user name
        "password": "j8eqXWPwskf0uNoO",  # enter your own user name
        "database": "HF_SP",
        "userReadonly": "user_readonly",
        "passwordReadonly": "qpG4qYs6JImwyRmc",
    },
}

DBConfigDict["Atlas"]["endpoint"] = (
    f"mongodb+srv://{DBConfigDict['Atlas']['user']}:{DBConfigDict['Atlas']['password']}@cluster0.1yhkhhb.mongodb.net",
)

DBConfigDict["Atlas"]["endpointReadonly"] = (
    f"mongodb+srv://{DBConfigDict['Atlas']['userReadonly']}:{DBConfigDict['Atlas']['passwordReadonly']}@cluster0.1yhkhhb.mongodb.net",
)
