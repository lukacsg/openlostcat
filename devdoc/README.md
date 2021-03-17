# OpenLostCat Developers' Documentation

## General structure

![class diagram](classdiagram.png)

## Data representation

json string...

tag bundle: dictionary

tag bundle set

immutable ...

atomic values ...

## Operators, Expressions

Type of logic... - univariate first-order, ~tuple calculus

Expressive power..., but extension is possible


Two levels:

Set(Filter)-level operators/subexpressions evaluate to tag bundle sets

Category(Bool)-level operators/subexpressions evaluate to single bool values

Quantifier operators bridge between set(filter)-level subexpressions and category(bool)-level subexpressions
by quantifying the filtered result set into a single bool value.

Universal quantifier - returns True if the filter subexpression equals to its given operand (all elements match)

Existential quantifier - returns True if the filter subexpression is nonempty (any of the elements match)

### Reference dictionary

In both levels ... #filter_ref_name and ##bool_ref_name

![class diagram of operators](classdiagram_operators.png)

### Quantifier wrapping 

If a set(filter)-level operator(subexpression) becomes a top-level operator(subexpression) for a category, 
or becomes an operand of a multi-ary operator having bool-level operands,
the filter-level operator must be wrapped into a bool operator(subexpression) by a quantifier.

Each set(filter)-level operator type has its default wrapper quantifier for the cases wherever a category(bool)-level operator(subexpression) is expected and it must be converted to it:
    wrapper quantifier of an atomic or const filter will default to ANY
    wrapper quantifier of implication will default to ALL
    wrapper quantifier of a 'not' or #ref is inherited from its subexpression
    wrapper quantifier of 'and' will default to ALL if each subexpression defaults to ALL, otherwise it will default to ANY
    wrapper quantifier of 'or' will default to ALL if at least one subexpression defaults to ALL, otherwise it will default to ANY


### Adding new operators or filters

...

for atomic: regex, comparisons with consts etc.

for quantifiers: hash table for exact / at least/most counts

...

## Processing flow

![information flow diagram](infflowdiagram.png)

## Parsing

![information flow diagram for parsing](infflowdiagram_parse.png)


## Tests

...


