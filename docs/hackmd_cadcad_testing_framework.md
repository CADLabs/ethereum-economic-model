# cadCAD Generalised Dynamical System Testing Framework

## Types of Tests

### Static code analysis

* Function return types
* Composition of types

### Typing tests

Pre-execution, part of CI pipeline.

* State Variable types and structure
* System Parameter types and structure

### Runtime tests

Sanity checks, of for example:
* Conservation laws
* Invariants
* Domains

#### Assertions
```python
assert x > 0, f"{x=}"
```

#### Custom Exceptions
```python
class XLessThanZeroError(Exception):
    pass

...

if not x > 0: raise XLessThanZeroError
```

#### Exception Handling
```python
try:
    x = get_x(state)
    assert x > 0
except AssertionError:
    # Handle error
    logger.warning("x is not greater than zero!")
    x = 0
```

### Unit tests

Testing of modular logic within policy and state update functions. This is made easier by having functions implementing the core specification logic outside the cadCAD policy and state update functions.

### Integration tests

Essentially model simulation, experiments. Run-time tests ensure model operating as expected as an integrated system.

### Data tests

Simulation result data post-processing and analysis.

* Comparing to referrence model for expected results

### Notebook tests

Test that all notebooks execute end-to-end.
