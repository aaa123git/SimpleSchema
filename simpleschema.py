"""
Data parsing and validation.
"""
import builtins
from typing import Union, Optional, Callable, Any


class Field:
    __No_Default = object()
    OPTIONAL = object()

    def __init__(self, type_: Union[str, type, list, tuple] = object, *,
                 description: Optional[str] = None,
                 default: Union[Callable[[], Any], object] = __No_Default,
                 converter: Optional[Callable[[Any], Any]] = None):
        """
        init

        Args:
            type_: type of the field
            description: description of the field
            default: default value of the field。
                If there's no default value and the field is missed, FieldValidationError will be raised.
            converter: a callable object.
                If it's not None, the field will be replaced by `converter(value)`.
        """
        if isinstance(type_, str):
            type_ = getattr(builtins, type_)
            assert isinstance(type_, type)
        elif isinstance(type_, type):
            pass
        else:
            assert isinstance(type_, (list, tuple)) and type_
            type_ = list(type_)
            for i, t in enumerate(type_):
                if isinstance(t, str):
                    t = getattr(builtins, t)
                assert isinstance(t, type)
                type_[i] = t
            type_ = tuple(type_)
        assert converter is None or callable(converter)

        self._type = type_
        self._default = default
        self._description = description
        self._process = converter

    def isinstance(self, obj):
        return isinstance(obj, self._type)

    def has_default_value(self):
        return self._default != self.__class__.__No_Default


class _Fields(dict):
    """A collection of fields."""


class FieldValidationError(Exception):
    def __init__(self, key=None, value=None, expected_type=None, msg=''):
        super().__init__(key, value, expected_type, msg)

    def __repr__(self):
        return f"{self.__class__.__name__}(key=%s, value=%s, expected_type=%s, msg=%s)" % self.args


class ModelMetaClass(type):
    def __new__(cls, *args, annotation_as_field=False, **kwargs):
        """
        Create new class and set _fields.

        Args:
            *args: name, bases and attrs
            annotation_as_field: If True, annotations are regarded as fields.
        """
        name, bases, attrs = args
        _fields = _Fields()

        # inherit '_fields' of base classes
        for base_class in bases[::-1]:
            if hasattr(base_class, '_fields') and isinstance(base_class._fields, _Fields):
                _fields.update(base_class._fields)

        new_attrs = {}
        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Field):
                _fields[attr_name] = attr_value
            else:
                new_attrs[attr_name] = attr_value

        annotations = new_attrs.get('__annotations__', {})
        if annotation_as_field and annotations:
            for attr_name, type_ in annotations.items():
                if attr_name in _fields or attr_name in new_attrs:
                    continue
                try:
                    field = Field(type_)
                except AssertionError:
                    raise TypeError(
                        "If `annotation_as_field` is true, each annotation, which is regarted as a field, must be a type."
                        f" But annotation of {attr_name} is {type_}") from None
                _fields[attr_name] = field
        new_attrs['_fields'] = _fields
        return super().__new__(cls, name, bases, new_attrs, **kwargs)


class BaseModel(dict, metaclass=ModelMetaClass):
    __doc__ = __doc__

    def __new__(cls, *args, **kwargs):
        # self.__dict__ is self, so that self.attr is self['attr']
        self = super().__new__(cls, *args, **kwargs)
        self.__dict__ = self
        return self

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in type(self)._fields.items():
            if field_name in self:
                if not field.isinstance(self[field_name]):
                    raise FieldValidationError(key=field_name, value=self[field_name], expected_type=field._type,
                                               msg="type error")
                if field._process is not None:
                    self[field_name] = field._process(self[field_name])
            elif field.has_default_value():
                if field._default == Field.OPTIONAL:
                    """missing this attribute is OK"""
                else:
                    msg = f"`field._default`: {field._default} must be an instance of {field._type}. " \
                          f"Otherwise, it must callable and returns an instance of {field._type}"
                    if field.isinstance(field._default):
                        self[field_name] = field._default
                    elif callable(field._default):
                        default = field._default()
                        assert field.isinstance(default), msg
                        self[field_name] = default
                    else:
                        raise TypeError(msg)
            else:
                raise FieldValidationError(
                    key=field_name,
                    expected_type=field._type,
                    msg=f"missing `{field_name}`, which is a {'or'.join(map(str, (field._type if not isinstance(field._type, type) else [field._type])))} object.")

    __init__.__text_signature__ = dict.__init__.__text_signature__
