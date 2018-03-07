""" Custom form widgets """

import wtforms


class FileInput(wtforms.widgets.FileInput):
    """Render a file chooser input.
    :param multiple: allow choosing multiple files
    :param accept: Pass in a list to limit which file types are accepted (see https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#attr-accept)

    From https://github.com/lepture/flask-wtf/issues/181#issuecomment-356906548 
    """

    def __init__(self, multiple=False, accept=None):
        super(FileInput, self).__init__()
        self.multiple = multiple
        self.accept = accept

    def __call__(self, field, **kwargs):
        if self.multiple:
            kwargs['multiple'] = True

        if self.accept:
            kwargs['accept'] = ', '.join(self.accept)

        return super(FileInput, self).__call__(field, **kwargs)
