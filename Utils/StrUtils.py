from re import sub


class StrUtils:
    @staticmethod
    def CamelCase(s):
        s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
        return "".join([s[0].lower(), s[1:]])
