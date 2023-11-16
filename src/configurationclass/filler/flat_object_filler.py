from __future__ import annotations

from inspect import isclass
from typing import Any, Generic, Type, TypeVar
from configurationclass.row import Row

T = TypeVar('T', bound=object)


class FlatObjectfiller(Generic[T]):
    _class: Type[T]
    _overwrite_defaults: bool

    
    def __init__(self, type: Type[T], overwrite_defaults: bool = True) -> None:
        self._class = type   
        self._overwrite_defaults = overwrite_defaults
        
    def _validate_input_attributes(
        self, data: dict[str, Any], matching_class: Type[Any]
    ) -> None:
        classname: str = matching_class.__name__
        expected: list[str] = list(matching_class.__annotations__.keys())

        diff = [x for x in expected if x not in set(data.keys())]

        if diff:
            raise AttributeError(
                f"Missing input attributes for {classname}: {', '.join(diff)}"
            )
        
    def _should_set_attr(self, cls: type, k: str) -> bool:
        return self._overwrite_defaults or not hasattr(cls, k)

    def _resolve_obj(self, cls: Type[T], data: dict[str, Any]) -> T:
        obj = cls()
        
        for k,v in data.items():
            if type(v) == dict or not self._should_set_attr(cls, k): continue 
            row = Row[T](cls, k, v)
                        
            setattr(obj, k, row.value)
            
        return obj

    def fill(self, data: dict[str, Any]) -> T:
        self._validate_input_attributes(
            data, self._class
        )
        return self._resolve_obj(self._class, data)
    
class ObjectFiller(FlatObjectfiller[T]):
    def _validate_class_annotations(self, row: Row[T]) -> None:        
        if row.key not in row.type.__annotations__:
            raise AttributeError(f"Attribute '{row.key}' not found in class")
        
        isinner: bool = isclass(row.type.__annotations__[row.key])

        if (type(row.value) != row.valuetype) and not isinner:
            raise TypeError(f'Type mismatch for {row.key} attribute')
        

    def _resolve_value(self, row: Row[T]) -> Any:
        if type(row.value) != dict:
            return row.value

        innercls: Type[T] = row.type.__annotations__[row.key]
        data: dict[str, Any] = row.value

        self._validate_input_attributes(
            data, innercls
        )
        return self._resolve_obj(innercls, data)
    
    def _resolve_obj(self, cls: Type[T], data: dict[str, Any]) -> T:
        obj = cls()
        
        for k,v in data.items():
            row = Row[T](cls, k, v)
            self._validate_class_annotations(
                row
            )
            if not self._should_set_attr(cls, k):
                continue
                        
            setattr(obj, k, self._resolve_value(row))
            
        return obj