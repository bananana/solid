# vim: fileencoding=utf-8 ai ts=4 sts=4 et sw=4
def no_email_required(function):
    function.no_email_required = True
    return function
