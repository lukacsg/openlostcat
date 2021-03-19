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

[Apache 2.0.](./LICENCE)

## Getting started

...

### Requirements, Environment

... python >=3.6 

https://pypi.org/project/immutabledict/



### Your First OpenLostCat Run

bp_hotels = pd.DataFrame([[nwr['id'], 
                           nwr['lat'], nwr['lon'], 
                           nwr['tags'].get('name', 'NoName'),  
                           nwr['tags']] for nwr in budapest_hotels['elements']], 
                         columns = ['id', 'lat', 'lng', 'name', 'tags'])
                         
osm = bp_hotels[["lat", "lng"]].apply(lambda x: ask_osm_around_point_df(x, distance = 300), axis = 1)
bp_hotels["osm"] = osm

categorizer = MainOsmCategorizer('rules/publictransport_rules.json') - instead: direct rules

print(categorizer.get_categories_enumerated_key_map())
print(categorizer)

1st: only one direct coordinate...

bp_hotels["pt_cat"] = [i[0] for i in bp_hotels.osm.map(categorizer.categorize)]


...

### Demo
...
see notebook

## General Usage

The main interface of the OpenLostCat utility library is the class _MainOsmCategorizer_ located in the file _main\_osm\_categorizer.py_. 
It must be initialized with a file path string or a python dictionary of JSON content describing the source category catalog with the rules. 
The initializer parses the given category rules and becomes ready for categorizing locations.

The file _osmqueryutils/ask\_osm.py_ contains OpenStreetMap-specific query strings and functions for single and multiple locations given by coordinates in different type of datasets. The appropriate function should be used to query the map objects with their tags in the required proximity of our locations.

After querying the OpenStreetMap objects around the locations, the _categorize(...)_ method of _MainOsmCategorizer_ must be called for each location separately to assign location category labels based on the parsed rules. 

The returning data is either a tuple (for single-category-matching) or a list of tuples containing the index of the category (in the order of appearance in the rule collection file), the name of the category and, optionally, debug information. If no category matches, the returned index is -1, the name is Null and the debug info remains empty.

```

```

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

Remark: References starting with `##` are _category-level_ (a.k.a. _bool-level_) references, while a single `#` name prefix means a (tag-bundle-)_set-level_ (a.k.a. _filter-level_) reference. See the explanation in the examples below.

### Category Catalog (Rule Collection) Properties

Currently only `evaluationStrategy` is supported in `properties`. Its possible values are:
* `all` : A location is evaluated for matching with each defined category and the labels of all matching categories are assigned. 
* `firstMatching` : A location is evaluated for matching the categories in their order of appearance in the catalog, and the label of the first matching category is assigned.

If no properties are given, `firstMatching` is assumed by default.



## Simple Category Rule Features by Example


### Atomic Filter: Simple Tag-Value Checking

Checks whether a key is present in a tag bundle and the value of the tag equals the desirable value.

For example, the following condition matches all locations where a public transport stop position is present in any of the tag bundles of queried nearby map objects:

```
{ "public_transport": "stop_position" }
```

The tag value be a single value or a list of values in the form of a JSON array, as in the following example. It finds all locations where either a stop position or platform is found:

```
{ "public_transport": ["stop_position", "platform"] }
```

### Value Types and Conversion

...

strings by default... other json types are translated to string

integer-> string

bool-> yes/no

remark on null value, see later...

### Multiple Tag-Value Checking

Multiple tag-value checking conditions (atomic filters) can be but together into a JSON object. In such cases, the condition matches if both of them is met for at least one of the tag bundles of the queried objects at a location (a.k.a. conjunctive, or _AND_ condition). The following condition evaluates to true for every location where a subway stop position is found (there must be a single object having both tags with the given values):

```
{
    "public_transport": "stop_position",
    "subway": true
}
```
A similar rule example follows, which matches locations with at least one wheelchair-accessible (barrier-free) supermarket nearby:

```
{
    "shop": "supermarket",
    "wheelchair": true
}
```

### Optional Tag-Value Checking

If `null` is added to a tag value list, it means the tag key is not mandatory to be present among the tags, but if present then its value must be one of the other elements in the list.
An obvious example is to find locations which are candidates for wheelchair-shopping (there is a supermarket with either explicit wheelchair-accessibility or limited accessibility, or no wheelchair information, i.e. no explicit negation of wheelchair accessibility):

```
{
    "shop": "supermarket",
    "wheelchair": [true, "limited", null]
}
```

### Negative Condition

An explicit negation may be added to the positive key-value conditions, stating a location matches only if there is at least one nearby object matching the listed positive condition(s) and not matching the condition(s) written inside the negated part at the same time. The following example matches all locations where a supermarket is found without an explicit statement of wheelchair inaccessibility (this is in fact, equivalent with the above example, if there are no more possible values of _wheelchair_ than listed above and here): 

```
{
    "shop": "supermarket",
    "__NOT_": { "wheelchair": false }
}
```

Note: the keyword `__NOT_` can be enhanced with an arbitrary, distinctive index or name of its (sub)condition, especially if there are multiple not-conditions in one level. This is because a JSON object must have distinct keys. ...

```
{
    "shop": "supermarket",
    "__NOT_inaccessible": { "wheelchair": false },
    "__NOT_...": { "...": ... }
}
```

### Checking the Existence or the Absence of a Tag

.....


tag must not exist:

```
{
    "public_transport": true,
    "subway": null
}
```

tag must exists without any prescribed value:

```
{
    "__NOT_": { "public_transport": null }
}
```

### Alternative Tag-Value Checking

Multiple key-value matching conditions can be combined as alternatives (a.k.a. disjunctive or _OR_ conditions), using standalone JSON arrays. The following example evaluates to true for a location if one of the queried nearby map objects have either one of the listed tag-values (either light-rail-, or subway-, or train-tagged): 


```
[
    { "light_rail": true },
    { "subway": true },
    { "train": true }
]
```

In order to get meaningful conditions, the conjunctive and disjunctive conditions can be combined with each other, such as in the following example, where a stop position is looked for, with either one of the specified transport modes:

```
[
    { "public_transport": "stop_position", "light_rail": true },
    { "public_transport": "stop_position", "subway": true },
    { "public_transport": "stop_position", "train": true }
]
```
The above condition is equivalent with the following, where the special key `__OR` introduces the alternative (sub)conditions:

```
{                
    "public_transport": "stop_position",
    "__OR_": [
        {"light_rail": true},
        {"subway": true},
        {"train": true}
    ]
}
```

Note: the keyword `__OR_` can be enhanced with an arbitrary, distinctive index or name of the (sub)conditions, especially if there are multiple of them in one level, such as in the following example. Here, a nearby map object matching both OR-conditions must be found in order for the location to meet the combined condition:

```
{
    "__OR_1": [ 
        {"public_transport": "stop_position"},
        {"railway": "platform"},
    ],
    "__OR_2": [
        {"light_rail": true},
        {"subway": true},
        {"train": true}
    ]
}
```

Note: there is also a keyword `__AND_`, in a similar fashion. It is mainly for language completeness, as it is usually not necessary to be used.

## Reusing Subexpressions by References

... # 

### Default (Fallback) Category

The default categorization strategy is `firstMatch`, which means the rules of category definitions are evaluated for a location in the order of appearance in the JSON category catalog, and the first matching category is assigned, without further evaluation. If no category is matched, OpenLostCat returns the category index -1. By adding a default fallback category with a simple _bool constant_ rule, this can be substituted with a named category for locations not matching any of the other categories. 

The following example defines two categories for public transport accessibility and non-accessibility. 

```
     "categoryRules": [
        {
            "pt_accessible": [
                {"public_transport": ["stop_position", "platform"] },
                {"amenity": "ferry_terminal"}
            ]
        },
        {
            "pt_nonaccessible": true
        }
     ]
```

Note: For this to be evaluated correctly, the  `evaluationStrategy` must be set to `firstMatching` in the `properties` of the category catalog, or left out, as it is the default.

### Implication Condition

(impl with all quantifier)


### All-Condition (universal quantification)
...

### Any-Condition (existential quantification)
...



## Complex Rule Cases and Language Background

### Filter semantics and set(/filter)-level operations 

Basically operators works as filter. Every operator has an apply function which get a list of tags and produces a subset of this list.
It returns with the filtered set.
...

### Quantifier Wrapping 

...

### Boolean semantics and category(/bool)-level operations 

...


### Expressive Power and Algebraic Equivalences

...

... - same category name is possible ...: filter-yes, filter-no, default-yes

### Reusing Subexpressions by References - two-level

... wheelchair... , mix...

## Rule Syntax Reference

The rule syntax is summarized below in the form of a generative grammar:
 

```
CategoryOrRefDef ::= CategoryDef | BoolRefDef | FilterRefDef
BoolRefDef ::= { BoolRefName = StandaloneBoolRule }
BoolRefName ::= "##.*"
FilterRefDef ::= { FilterRefName = StandaloneFilterRule }
FilterRefName ::= "#[^#].*"
CategoryDef ::= { CategoryName = StandaloneRule }
CategoryName ::= "[^#].*"

StandaloneBoolRule ::= bool | BoolAndObj | BoolOrObj | BoolRefName | StandaloneFilterRule
BoolAndObj ::= { KeyValueBoolRule, ... }
BoolOrObj ::= [ StandaloneBoolRule, ... ]
KeyValueBoolRule ::= 
    "__AND_.*"   : BoolAndObj | 
    "__OR_.*"    : BoolOrObj | 
    "__IMPL_.*"  : BoolOrObj | 
    "__NOT_.*"   : StandaloneBoolRule | 
    "__ALL_.*"   : StandaloneFilterRule | 
    "__ANY_.*"   : StandaloneFilterRule | 
    "__REF_.*"   : BoolRefName |
    "__CONST_.*" : bool |
    KeyValueFilterRule

StandaloneFilterRule ::= bool | FilterAndObj | FilterOrObj | FilterRefName
FilterAndObj ::= { KeyValueFilterRule, ... }
FilterOrObj ::= [ StandaloneFilterRule, ... ]
KeyValueFilterRule ::= 
    "__AND_.*"  : FilterAndObj | 
    "__OR_.*"   : FilterOrObj | 
    "__IMPL_.*" : FilterOrObj | 
    "__NOT_.*"  : StandaloneFilterRule | 
    "__REF_.*"  : FilterRefName |
    "__CONST_.*": bool |
    AtomicFilter

AtomicFilter ::= "[^_].*" : ValueOrList
ValueOrList ::= SingleValue | [SingleValue, ...]
SingleValue ::= bool | str | int | null
```

where
 - bool, str, int, null : the corresponding JSON type
 - \[ x, ... \]  :  JSON array (list) of elements of type x
 - { t, ... }  : json object (dict) elements of tuples (key-value pairs of type t
 - x | y : an element of type x or y
 - "..." : JSON string matching the given regexp (.* stands for any sequence of characters, \[^x\] stands for a character not being x)
  
SingleValue conversions/semantics in atomic filters:

 - bool: true is mapped to "yes"; false to "no"
 - str: str (no conversion for strings)
 - int: string representation of int 
 - null: the key is optional in the tag bundle

Printing the categorizer outputs the abstract syntax tree of the parsed category catalog, where the operators on set/filter level are written with lowercase and the operators on category/bool level with uppercase letters.


## Further Info and Contribution

See the Developers' Documentation in [devdoc](devdoc/).

Contact the creators Gábor Lukács ([lukacsg](https://github.com/lukacsg)) and András Molnár ([zarandras](https://github.com/zarandras)) with any questions, suggestions or contributions.


