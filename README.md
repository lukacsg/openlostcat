# OpenLostCat - A Location Categorizer Based on OpenStreetMap

## What is it?

OpenLostCat (Open Logic-based Simple Tag-bundle Categorizer) is a utility written in Python for data analysts, engineers and scientists 
who want to determine the characteristics of geolocated points in their datasets. 
OpenLostCat does the job by assigning category labels to each data point 
based on logical rules defined in JSON for tags of OpenStreetMap objects located in the proximity of the point.

### Typical Use Cases

* Given a point dataset of events or incidents, see where they happened in terms of co-located or nearby geographical objects (type of area, nearby streets or point features such as amenities or others).

* Given a point dataset of events or incidents, see whether their attributes correlate with specific location characteristics.

* Given a set of geotagged photos or media posts, determine where they were made in terms of present or absent geographic feature types or constellations (how many of them were posted at which type of location).

* Given a set of candidate locations for specific activities, determine the most or least suitable ones based on what each location provides or features.

* Given the locations of self-managed facilities, create an overview of which (and how many) of them is located at a given type of location, and whether there is any correlation in the type of location and the facility condition. 

* ... and what is your use case...?



## Feature Overwiew

* Query OpenStretMap objects at locations given by WGS 84 coordinates via Overpass API (customizable proximity distance)

* Assignment of user-defined location category labels to the given locations, based on queried OpenStreetMap objects in their proximity

* Comrehensive and extensible location category rule syntax in JSON, where a tag bundle represents an OpenStreetMap object

* Single-category (first matching rule strategy) or multi-category (all matching rule strategy) labeling for locations

* Reusable rules or subexpressions by named references (inside a location category catalog)

* Debug feature with explicit AST (abstract syntax tree) output

* Example category rules showcasing rule definition features

* Demo notebook with the examples, including map visualization

* Rule language of univariate first-order logic with two levels of operations (item and category-level)

  * Filter semantics on the item level: an item-level rule subexpression results in a subset of the tag bundles for a single location
    and the category assignment is based on the eventual (non-)emptiness of this set or its size in relation with the original (non-filtered) tag bundle set specified by a quantifier

  * Boolean semantics on the category-level: a category-level subexpression results in a true/false value for a single location

  * Atomic filters with equality conditions for tag values or allowed value lists (item-level)
  
  * Atomic filters with existence or optionality conditions for specific tags (item-level)

  * Combinations of atomic filters for different tags of tag bundles (item-level)

  * Logical filter operators AND, OR, NOT and implication for tag bundles (item-level)

  * Existential (ANY) and universal (ALL) quantification (from item-level to category-level; ANY matches if the filtered tag bundle set is nonempty, ALL matches if it equals its non-filtered original)
  
  * Common-sense default quantifier wrapping for filters (such as ANY for atomic filters, ALL for implications)

  * Boolean combinations of category-level (quantified) rule subexpressions: AND, OR, NOT and implication for single true/false-valued expressions
  
  * Constant subexpressions for technical use and logical language completeness

  * Named references of item- (filter) or category-level (bool) subexpressions


## Licence

...

## Getting started

...

## Demo

...

## General Usage

The main interface of the OpenLostCat utility library is the class _MainOsmCategorizer_ located in the file _main\_osm\_categorizer.py_. 
It must be initialized with a file path string or a python dictionary of JSON content describing the source category catalog with the rules. 
The initializer parses the given category rules and becomes ready for categorizing locations.

The file _osmqueryutils/ask\_osm.py_ contains OpenStreetMap-specific query strings and functions for single and multiple locations given by coordinates in different type of datasets. The appropriate function should be used to query the map objects with their tags in the required proximity of our locations.

After querying the OpenStreetMap objects around the locations, the _categorize(...)_ method of _MainOsmCategorizer_ must be called for each location separately to assign location category labels based on the parsed rules.



## Category Catalog (Rule Collection) Format

The basic skeleton of the expected JSON structure is as follows. It must be a valid JSON object or file.


```
{
     "type": "CategoryRuleCollection",
     "properties": {
         "evaluationStrategy": "all"
     },
     "categoryRules": [
        {
            "category_or_reference_1_name": ...rules_of_category_or_reference_1...
        },
        {
            "category_or_reference_2": ...rules_of_category_or_reference_2...
        },
        ...further_category_or_reference_definitions...
     ]
}
```

The attribute `type` must always be given in the above form, in order to make sure the intention of the JSON object/file is a category rule collection for OpenLostCat.

Rule definitions must be given in the form of a JSON array, each of its elements containing a category or a reference (named reusable subexpression) definition with its rules.
Such a definition must be a json object with a single key, which is the name of the category or reference. An identifier starting with `#` denotes a reference, otherwise a category. Rules follow as JSON objects or arrays as shown below.

The `properties` part is optional, where general directives can be specified for the whole categorization process.

### References: named subexpressions

If a name (JSON key) starts with the character `#` under the definitions of `categoryRules`, it is treated as a _reference_, that is, a named subexpression (part of a rule), which can be referenced from multiple category definitions. This way, repeated parts of rules do not have to be explicitly duplicated and whenever a change is necessary, it can be done at one place.

Remark: References starting with `##` are category-level (a.k.a. bool-level) references, while a single `#` name prefix means a set-level (a.k.a. filter-level) reference. See the explanation at the examples below.

### Category Catalog (Rule Collection) Properties

Currently only `evaluationStrategy` is supported. Its possible values:
* `all` : A location is evaluated for matching with each defined category and the labels of all matching categories are assigned. 
* `firstMatching` : A location is evaluated for matching the categories in their order of appearance in the catalog, and the label of the first matching category is assigned.

If no properties are given, `firstMatching` is assumed by default.



## Category Rule Features by Example

...

### Atomic filter
Checks whether a key is present in the tag bundle and the value of the tag equals the desirable value. 

Values could be a single value or a list of single values.


attributes: 

 - key: the name of the tag which has to be investigated
 - values: the possibly values of the tags

```
{
    highway = tertiary
}
```

If null is presented in the list means that the key is not mandatory to be presented in the tags but it is than the values can be only in the values set.


...

Basically operators works as filter. Every operator has an apply function which get a list of tags and produces a subset of this list.
It returns with the filtered set.

##### FilterNOT
FilterNOT can be use as negation. It provides the complementary set of the underlying operator result.

##### FilterAND
##### FilterOR
##### FilterConst

##### BoolConst
#### Category
#### CategoryCatalog







## Rule Syntax Reference

...

Category ::= BoolConst | FilterAND (Rule with a restriction to FilterAND) | [Rule, ...]
BoolConst ::= bool (true | false)
Rule ::= FilterAND | FilterOR
FilterNOT ::= FilterAND | FilterOR
FilterOR ::= [FilterAND | FilterOR, ...]
FilterAND ::= {Tuple, ...}
Tuple ::= "__AND..." : FilterAND | "__OR..." : FilterOR | "__NOT..." : FilterNOT | SimpleOp
SimpleOp ::= str (starts not with "__AND", "__OR", "__NOT") : SingleValue | [SingleValue, ...]
SingleValue ::= bool | str | int | null


where
 - bool, str, int, null : the corresponding json type
 - [x,..]  :  json list of elements x
 - {tuple,.. }  : json dict elements of tuples  /(key, value) pairs/
 - x | y : x or y elements can be presented here
 - (...) : some additional notes
 - "txt..." : json string which starts by "txt"
 
SingleValue conversions in AtomicFilter operator:

 - bool: "yes" if true; "no" if false
 - str: str
 - int: string representation of int 
 - null: it means that the key must not be represented in the tag list



## Further Info and Contribution

See the Developers' Documentation in [devdoc](devdoc/).

Contact the creators Gábor Lukács ([lukacsg](https://github.com/lukacsg)) and András Molnár ([zarandras](https://github.com/zarandras)) with any questions, suggestions or contributions.


