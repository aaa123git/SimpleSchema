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
