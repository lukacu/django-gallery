from django.db import models

__author__ = 'lukacu'

class ThumbnailParametersField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 32
        super(ThumbnailParametersField, self).__init__(*args, **kwargs)


    def to_python(self, value):
        if not value:
            return {}

        tokens = value.split( ';')

        if len(tokens) < 3:
            return {}

        return {'scale' : float(tokens[0]), 'x' : float(tokens[1]), 'y' : float(tokens[2])}

    def get_prep_value(self, value):
        if value.empty():
            return ''

        return "%.3f;%.3f;%.3f" % (value.get("scale", 1), value.get("x", 0.5), value.get("y", 0.5))

    def validate(self, value):
        # TODO: better validation
        # Use the parent's handling of required fields, etc.
        super(ThumbnailParametersField, self).validate(value)


from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^gallery\.fields\.ThumbnailParametersField"])