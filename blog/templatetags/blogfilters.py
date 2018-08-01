from django import template


register = template.Library()

@register.filter(name='splitlongwords')
def splitlongwords(value, arg):
    arg = int(arg)
    value = str(value)
    "puts spaces into long words to avoid layout issues"
    lines = [x.split(" ") for x in value.split("\n")]
    newlines = []
    for x in lines:
        l = []
        for xx in x:
            if len(xx) > arg:
                for i in range(0, (len(xx)/arg)+1):
                    l.append(xx[i*arg:i*arg+arg])
            else:
                l.append(xx)
        newlines.append(" ".join(l))
    return "\n".join(newlines)