from __future__ import annotations

from dataclasses import is_dataclass
from inspect import isclass
from pathlib import Path
from typing import Any, Type, TypeVar
from configurationclass.configwriter import JSONConfigParser
from configurationclass.flat_object_filler import ObjectFiller
from configurationclass.main import is_confclass

from configurationclass.nested_obj_filler import DataclassFiller
from os import path


T = TypeVar('T', bound=object)

def confclass(cls: T) -> T:
    if cls is None:
        raise ValueError("Decorator can only be used with parameters")
    if not isclass(cls):
        raise ValueError("Decorator can only be used on a class")

    def wrap(cls: T): # type: ignore 
        setattr(cls, '__IS_CONCLASS__', True) 
        return cls

    return wrap(cls) # type: ignore

def dict_in_dataclass(data: dict[str, Any], type: Type[T]) -> T | None:
    if not is_dataclass(type):
        raise SyntaxError(f"'{type.__name__}' should be a dataclass instance")
    return DataclassFiller(type).fill(data) # type: ignore[return-value]

def dict_in_confclass(data: dict[str, Any], type: Type[T]) -> T | None:
    if not is_confclass(type):
        raise SyntaxError(f"'{type.__name__}' should be a confclass instance") 
    return ObjectFiller(type).fill(data)

def parse_dataclass(filepath: Path, type: Type[T]) -> T | None:
    if not path.exists(filepath):
        raise FileNotFoundError
    
    # only JSON support currently
    attrs = JSONConfigParser().read(filepath)
    
    return dict_in_dataclass(attrs, type)

def parse_config(filepath: Path, type: Type[T]) -> T | None:
    if not path.exists(filepath):
        raise FileNotFoundError
    
    # only JSON support currently
    attrs = JSONConfigParser().read(filepath)
    
    return dict_in_confclass(attrs, type)