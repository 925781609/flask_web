from . import apps

@apps.route('/', methods=['GET'])
def guess_number():
    return "Pls guess a number"

