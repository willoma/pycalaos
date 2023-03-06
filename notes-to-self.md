# Notes to self

Some notes, because I do those things too rarely to remember them...

## New release

1. Do not forget to change version in `setup.py`

2. Create the dist:

```plain
python setup.py sdist
```

3. Publish:

```plain
twine upload dist/*
```
