""" Custom form fields """ 

import flask_wtf.file
from werkzeug.datastructures import FileStorage

from .widgets import FileInput

 
class MultipleFileField(flask_wtf.file.FileField):
    """A :class:`FileField` that allows choosing multiple files.
    
    From https://github.com/lepture/flask-wtf/issues/181#issuecomment-356906548 
    """

    widget = FileInput(multiple=True)

    def process_formdata(self, valuelist):
        data = list(x for x in valuelist if isinstance(x, FileStorage) and x)

        if data is not None:
            self.data = data
        else:
            self.raw_data = ()
