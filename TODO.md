Research:
 - [ ] Auth flow in Tg, Windows, etc.

Notes:
 - [x] Use `fastapi.Query(None)` as default value for any pydantic schema.
    With this approach you can pass any other Query parameters into the
    FastApi route.
 - [x] Если создаешь кастомный Depends, в котором происходит мета-магия (объявление функции, создание некешируемоего класса), то лучше на такой кастомный Depends навесить доп декорато @cache. В противном случае повторные объявления кастомного Depends с одними и теме же аргументами будут считаться как разные (DI пойдет по одному месту). Аналогичного положительного эффекта можно достичь, если при возврате из кастомного Depends передавать в вызываемый Depends неперегенерированный объект, а подтянутый из какого-то кеша (словарь, синглтоны)
```python
@cache
def FilterDepends(schema: type[FilterT]) -> FilterT:
    queried_schema = create_model("Query" + schema.__name__, __base__=schema)
    inject_query(queried_schema)

    def get_schema(filters: queried_schema = Depends()) -> FilterT:
        print(f"got ({id(filters)}) {filters} ")
        return filters

    print(f"initialized {schema.__name__}")
    return Depends(get_schema, use_cache=True)
# ИЛИ
injected = {}
def FilterDepends(schema: type[FilterT]) -> FilterT:
    queried_schema = create_model("Query" + schema.__name__, __base__=schema)
    inject_query(queried_schema)

    def get_schema(filters: queried_schema = Depends()) -> FilterT:
        print(f"got ({id(filters)}) {filters} ")
        return filters

    print(f"initialized {schema.__name__}")
    injected.setdefault(schema, get_schema)
    ret = injected.get(schema, get_schema)
    return Depends(ret, use_cache=True)
 ```
