from typing import (
    Any,
    get_origin,
    get_args,
    Union,
    Callable,
    Tuple,
)

from pydantic.fields import FieldInfo
from pydantic import BaseModel


def type_is_optional(t: type[Any]) -> Callable[[type[Any]], bool]:
    """Return a predicate which checks whether a type is Optional[t]."""
    return lambda f: get_origin(f) is Union and get_args(f) == (t, type(None))


def type_is_optional_satisfying(
    p: Callable[[type[Any]], bool],
) -> Callable[[type[Any]], bool]:
    return (
        lambda f: get_origin(f) is Union
        and (len(args := get_args(f)) == 2)
        and (args[1] == type(None))
        and p(args[0])
    )


def type_is_subclass(
    superclass: Union[type, Tuple[Union[type, Tuple[Any, ...]], ...]],
) -> Callable[[type[Any]], bool]:
    return lambda f: isinstance(f, type) and issubclass(f, superclass)


def type_is_optional_subclass(
    superclass: Union[type, Tuple[Union[type, Tuple[Any, ...]], ...]],
) -> Callable[[type[Any]], bool]:
    return type_is_optional_satisfying(type_is_subclass(superclass))


def field_type_satisfies(p: Callable[[type[Any]], bool]) -> Callable[[FieldInfo], bool]:
    return lambda f: f.annotation is not None and p(f.annotation)


def field_type_is(t: type[Any]) -> Callable[[FieldInfo], bool]:
    return field_type_satisfies(lambda f: f is t)


def field_has_tag(tag: Any) -> Callable[[FieldInfo], bool]:
    return lambda f: tag in f.metadata


def field_is_type_with_tag(typ: type[Any], tag: Any) -> Callable[[FieldInfo], bool]:
    return lambda f: field_type_is(typ)(f) and field_has_tag(tag)(f)


def field_is_optional_type_with_tag(
    typ: type[Any], tag: Any
) -> Callable[[FieldInfo], bool]:
    return lambda f: field_type_satisfies(type_is_optional(typ))(f) and field_has_tag(
        tag
    )(f)


def fields_satisfying(cls: BaseModel, p: Callable[[FieldInfo], bool]) -> list[str]:
    """Return the names of fields which satisfy this predicate on their info."""
    return [
        field_name
        for field_name, model_field in cls.model_fields.items()
        if p(model_field)
    ]


def fields_with_type_satisfying(
    cls: BaseModel, p: Callable[[type[Any]], bool]
) -> list[str]:
    """Return the names of fields which satisfy this predicate on their annotated type."""
    return fields_satisfying(cls, field_type_satisfies(p))


def fields_of_type(cls: BaseModel, t: type[Any]) -> list[str]:
    """
    Return the names of fields in this model of type t.
    Note that this won't work for more complex types such as Optional[Path]; for that, use fields_satisfying(type_is_optional(Path)).
    """
    return fields_with_type_satisfying(cls, lambda f: f is t)
