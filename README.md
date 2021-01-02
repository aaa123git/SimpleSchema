# SimpleSchema
SimpleSchema is a simply implemented data validation tool.
For more powerful tools, see [pydantic](https://github.com/samuelcolvin/pydantic) or [schema](https://github.com/keleshev/schema).

## Requirements
Nothing but python.

## Installation
SimpleSchema hasn't been published to pypi, so you should clone it and run `pip install .`.
Since there's only **one** `.py` file, you can also copy simpleschema.py into your project.

## Example
Because I don't like writing documents, you may read the code yourself or try some 
simple examples to understand how it works.

```python
from simpleschema import BaseModel, Field


class Person(BaseModel, annotation_as_field=True):
    name = Field(str)
    age = Field((int, float), default=8, converter=int)
    gender: str
    salary = Field([int, float], default=float)
    other_attrs = Field(dict, default=Field.OPTIONAL)


if __name__ == '__main__':
    person = Person({'name': 'Bob', "gender": 'male', 'age': 21.9})
    print(person)  # {'name': 'Bob', 'gender': 'male', 'age': 21, 'salary': 0.0}
    print(person.age)  # 21
    print(person['salary'])  # 0.0
```
