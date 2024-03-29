<img src="./openlostcat_logo.png" alt="[Logo]" width="25%" height="25%">

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

* Comprehensive and extensible location category rule syntax in JSON, where a tag bundle represents an OpenStreetMap object

* Single-category (first matching rule strategy) or multi-category (all matching rule strategy) labeling for locations

* Target categories indexed in the order of rules, mapped to category names

* Reusable rules or subexpressions by named references (inside a location category catalog)

* Visualization of the category catalog (set of parsed expression rules)

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
  
  * Common-sense default quantifier wrapping for filters (such as ANY for atomic filters, ALL for implications) with logical robustness yielding similar default quantifiers for equivalent subformulae

  * Boolean combinations of category-level (quantified) rule subexpressions: AND, OR, NOT and implication for single true/false-valued expressions
  
  * Constant subexpressions for technical use and logical language completeness

  * Named references of item- (filter) or category-level (bool) subexpressions


## Licence

[Apache 2.0.](./LICENCE)

## Getting started

### Requirements, Environment

OpenLostCat requires `python >= 3.6`, due to the following issue:

[https://pypi.org/project/immutabledict/](https://pypi.org/project/immutabledict/)

You may either use a _jupyter notebook_ or standalone python as well.

Utilizing _pandas_ makes using OpenLostCat simpler and more effective, but it is not necessary.

After cloning the OpenLostCat github repository, you may install it in your environment from the repository root folder by running the command `pip install .` .

### Your First OpenLostCat Run

Use the following python commands to try out OpenLostCat for a simple location categorization, 
where two geolocated points (a central railway station and a picnic area outside the city) are categorized 
according to their public transport accessibility:

```
from openlostcat.main_osm_categorizer import MainOsmCategorizer
from openlostcat.osmqueryutils.ask_osm import ask_osm, ask_osm_around_point
import json
                         
# Query the OpenStreetMap objects in the proximity of the two points:  
osm_neighborhood_railway_station = ask_osm_around_point(47.5001, 19.0247, distance = 300)
osm_neighborhood_picnic_area     = ask_osm_around_point(47.4945, 18.9464, distance = 300)

# Create the categorizer by parsing JSON rules:  
categorizer = MainOsmCategorizer(json.loads('{ "type": "CategoryRuleCollection", "categoryRules": [ { "pt_accessible": { "public_transport": "stop_position" } }, { "pt_inaccessible": true } ] }'))

# Print the list of categories:  
print(categorizer.get_categories_enumerated_key_map())

# Do the categorization of the railway station and print its category:  
category_railway_station = categorizer.categorize(osm_neighborhood_railway_station)
print(category_railway_station)

# Do the categorization of the railway station and print its category:  
category_picnic_area = categorizer.categorize(osm_neighborhood_picnic_area)
print(category_picnic_area)

# Print the categorizer with the syntax tree of the parsed categorizing rules:  
print(categorizer)

```
If you have reached this point successfully: Congrats! 
You are ready to use OpenLostCat and do some more interesting stuff!
Keep on reading...

### Demo and Examples

See and run our jupyter notebook [examples/Budapest\_hotels\_categorization.ipynb](examples/Budapest_hotels_categorization.ipynb) 
using example rulesets in the directory [examples/rules/](examples/rules) for trying out different scenarios and features OpenLostCat provides.
Detailed explanations of features and possibilities can be found below.


## General Usage

The main interface of the OpenLostCat utility library is the class _MainOsmCategorizer_ located in the file _main\_osm\_categorizer.py_. 
It must be initialized with a file path string or a python dictionary of JSON content describing the source category catalog with the rules. 
The initializer parses the given category rules and becomes ready for categorizing locations.

The file _osmqueryutils/ask\_osm.py_ contains OpenStreetMap-specific query strings and functions for single and multiple locations given by coordinates in different type of datasets. The appropriate function should be used to query the map objects with their tags in the required proximity of our locations.

After querying the OpenStreetMap objects around the locations, the _categorize(...)_ method of _MainOsmCategorizer_ must be called for each location separately to assign location category labels based on the parsed rules. 

The returning data is either a tuple (for single-category-matching) or a list of tuples containing the index of the category (in the order of appearance in the rule collection file), the name of the category and, optionally, debug information. If no category matches, the returned index is -1, the name is Null and the debug info remains empty.

Refer to the Quick User Reference at the bottom of this document for a listing of functions and operators.

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
Such a definition must be a json object with a single key, which is the name of the category or reference. An identifier starting with `#` denotes a reference, otherwise a category. The order of items in the array is important, and any reference used in a rule must be defined in advance. Rules follow as JSON objects or arrays as shown below. 

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

Such conditions can be directly used to define a category, as in the following example, or used to compose more complex conditions (see later).

```
"categoryRules": [
    {
        "pt_accessible": { "public_transport": ["stop_position", "platform"] }
    }
]
```

### Value Types and Conversion

OpenStreetMap tags are strings. OpenLostCat can consume other JSON data types and it converts them to strings in the following way:

* numbers are translated to strings in the conventional way,
* booleans are translated to strings, in the OpenStreetMap style: true to "yes" and false to "no",
* null values are treated in a specific way: if a null value is added to the list of accepted values for a tag then the absence of the tag counts as a match (optionality). If a single null value is specified as a value, then the tag must be missing. See more details and examples in further sections.
* an empty JSON object (opening and closing curly braces) is interpreted as a placeholder for any value, that means the filter matches if the tag is present regardless of its actual value. 

For instance, the following example condition matches any location where a map object with OpenStreetMap tag `subway=yes` is found:

```
{ "subway": true }
```

The following example condition matches any location where a `public_transport` tag found with any value:

```
{ "public_transport": {} }
```

### Multiple Tag-Value Checking (_AND_)

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

Note that a JSON object with multiple key-value pairs is parsed as an _AND_ condition, while a singleton JSON object is directly translated to the single condition it contains.

Additional remark: An _AND_ condition can also be expressed using an explicit JSON keyword prefix `__AND_`. The above exampe is equivalent with this expression:

```
{
    "__AND_":
        {
            "shop": "supermarket",
            "wheelchair": true
        }
}
```

Note that these combinations apply together for each map object (tag bundle) in the proximity. If you want to formulate a condition referring to different map objects, such as stating a supermarket and a (maybe another) wheelchair-accessible asset is nearby, then these two conditions must be formulated and bracketed as separate subexpressions, each (or at least one of them) wrapped into an ANY quantifier and combined together with a (boolean/category-level) conjunction. Details follow (see the section about the ANY quantifier below).

### Optional Tag-Value Checking (_null_ in value list)

If `null` is added to a tag value list, it means the tag key is not mandatory to be present among the tags, but if present then its value must be one of the other elements in the list.
An obvious example is to find locations which are candidates for wheelchair-shopping (there is a supermarket with either explicit wheelchair-accessibility or limited accessibility, or no wheelchair information, i.e. no explicit negation of wheelchair accessibility):

```
{
    "shop": "supermarket",
    "wheelchair": [true, "limited", null]
}
```

### Negative Condition (_NOT_)

An explicit negation may be added to the positive key-value conditions, stating a location matches only if there is at least one nearby object matching the listed positive condition(s) and not matching the condition(s) written inside the negated part at the same time. The following example matches all locations where a supermarket is found without an explicit statement of wheelchair inaccessibility (this is in fact, equivalent with the above example, if there are no more possible values of _wheelchair_ than listed above and here): 

```
{
    "shop": "supermarket",
    "__NOT_": { "wheelchair": false }
}
```

Note: the keyword `__NOT_` can be enhanced with an arbitrary, distinctive index or name of its (sub)condition, especially if there are multiple not-conditions in one level. This is because a JSON object must have distinct keys. 

In the following example, a supermarket must be found with no explicit wheelchair inaccessibility and no required membership for shopping:

```
{
    "shop": "supermarket",
    "__NOT_inaccessible": { "wheelchair": false },
    "__NOT_membership": { "membership": true }
}
```

If there is no positive condition in direct conjunction with one or more negated (NOT) conditions, then the way of rule interpretation changes:
Applying to sets of tag bundles, the negation (or multiple negations) will become a universal condition, that is, a category defined by a single negation or a conjunction of atomic negations will match only if all queried map elements in its proximity matches the condition. With the following example, it means each element must not be a supermarket, that is, if used directly as a category definition, it matches only the locations without any supermarkets: 

```
{
    "__NOT_": { "shop": "supermarket" }
}
```

Similarly, the following condition used as a direct category definition will match only if there is no barrier-free supermarket in the vicinity. See more details in the section about quantifier wrapping in detail below.


```
{
    "__NOT_1": { "shop": "supermarket" },
    "__NOT_2": { "wheelchair": [ true, "designated" ] }
}
```


### Checking the Existence or Absence of a Tag (_null_ value and empty object as value)

Using a _null_ JSON value as a tag value in OpenLostCat conditions means a no-value, that is, the tag named should be missing (or, if not missing, must have the other values listed).

In the following example, matching means a map object must be present in the proximity of the location in question with _public\_transport=yes_ having no subway tag at all (in other terms, it means a non-subway public transport availability):

```
{
    "public_transport": true,
    "subway": null
}
```

Here, the _subway_ tag must either have the value of "no" or is missing (by at least one map object nearby):

```
{
    "public_transport": true,
    "subway": [false, null]
}
```

If we want to formulate a condition for the existence of a tag without any prescribed value(s), we use the empty object notation.
The following example matches wherever a map object is found nearby with a _public\_transport_ tag with any value:

```
{
    "public_transport": {}
}
```

This is equivalent with negating the null-condition (see below) if used together with other filters, however, only if at least one positive condition is added in conjunction so that it will not turn into a universal filter (see the previous section):

```
{
    "__NOT_": { "public_transport": null }
}
```

While the above two formulae if kept standalone are not equivalent with each other, the following two formulae are equivalent as they become both existential (looking for at least one matching element, which is a barrier-free and has a public transport tag with any value). See more details in the section about quantifier wrapping in detail below.


```
{
    "public_transport": {},
    "wheelchair": [ true, "designated" ]
}
```

```
{
    "__NOT_": { "public_transport": null }
    "wheelchair": [ true, "designated" ]
}
```

### Alternative Tag-Value Checking (_OR_)

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
The above condition is equivalent with the following, where the special key `__OR_` introduces the alternative (sub)conditions:

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
        {"railway": "platform"}
    ],
    "__OR_2": [
        {"light_rail": true},
        {"subway": true},
        {"train": true}
    ]
}
```

Note that a JSON array with multiple values is parsed as an _OR_ condition, while a JSON array is directly translated to the single condition it contains.

## Reusing Subexpressions by References (#, ## and _REF_)

If a name being defined in the ruleset starts with the `#` character, it means a reference instead of a category definition. It does not generate a category but instead, a (sub)expression being named for reuse in possibly multiple rules.

Using references is encouraged not only for better comprehensibility and reducing redundancy in rule definitions, but also for effective processing, since OpenLostCat uses a caching mechanism to speed up evaluation of rules or rule sets. If a reference is used multiple times during a categorization process, it will only be evaluated once.

The next example shows a definition of two references defined for different types of public transport accessibility, being combined into a category with an or-condition:

```
"categoryRules": [
    {
        "#pt_platform_close": [
            {"public_transport": ["stop_position", "platform"] },
            {"railway": "platform"}
        ]
    },
    {
        "#pt_ferry_close": {"amenity": "ferry_terminal"}
    },
    {
        "pt_accessible": [ #pt_platform_close, #pt_ferry_close ]
    }
```

We can also use a reference in a JSON object-context, using the keyword `__REF_`, as follows, where we use one of the references above in defining a category with an and-condition:

```
    {
        "subway_accessible": {
            "__REF_": "#pt_platform_close",
            "subway": true
        }
    }

```

References can be nested into each other. Cycles of references are not possible as any reference can only be used only after having been defined.  

Note: Some (sub)expressions must be preceded with two hashmarks `##` to be defined as references, depending on their intended logical level of use in category definitions (also influenced by the type of operators they contain). See more details later (Section _Two types of references_) about this.


### Const Expression and Default (Fallback) Category (_true_ constant)

A _constant_ operand is either an explicit _true_ or _false_ boolean value, which can be used at any point where a subexpression is expected in OpenLostCat rules.

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
        "pt_inaccessible": true
    }
]
```

Note: For this to be evaluated correctly, the  `evaluationStrategy` must be set to `firstMatching` in the `properties` of the category catalog, or left out, as it is the default.

### Implication Condition (_IMPL_)

Logical implication is a form of statement saying whenever a given condition is true then another condition must also be true. 
OpenLostCat can treat such statements as categorization conditions with the keyword `__IMPL_`, meaning that a location matches the category defined by the implication 
if it is valid for _all_ queried OpenStretMap elements in its proximity.

If we want to define, for example, that each public transport stop or platform nearby a location is wheelchair-accessible, we may use the following condition:

```
{ 
    "__IMPL_": [ 
        {"public_transport": ["stop_position", "platform"] }, 
        {"wheelchair": [true, "designated"]} 
    ]
}
```

The implication may have multiple premises and a single conclusion. In such cases, wherever each of the premises match, the conclusion must also hold, in order for the location to be categorized as matching. The following example defines the same as above, with a restriction to subway stations, that is, the wheelchair-accessibility must only hold if the stop is a subway station:

```
{
    "__IMPL_": [ 
        {"public_transport": ["stop_position", "platform"] }, 
        {"subway": true},
        {"wheelchair": [true, "designated"]} 
    ]
}
```

An implication condition being evaluated for a single object (tag bundle) is basically equivalent to a disjunction (_OR_ condition) where all its premises are negated and its single conclusion remains positive. Therefore, if any of the premises evaluates to false, the implication becomes true for the object (tag bundle) without looking at its conclusion or further premises.

Applying to sets of tag bundles, the implication is in fact usually becomes a universal condition (if it contains only atomic filters then always), that is, a category defined by a single implication will match only if _all_ queried map elements in its proximity matches the condition. 
In the example above, it means each element having a _public\_transport_ tag with either a _stop\_position_ or _platform_ value must have a _wheelchair_ tag as well with the value _yes_ or _designated_.

Warning! From the above, it follows that the truth of implication does not mean there is any map object in the proximity with the given premises. The above example rules will match even if there is no public transport station in the proximity. To fix this, an explicit existential condition must be added as follows (see more details in the Any-condition section):

```
{
    "__IMPL_": [ 
        {"public_transport": ["stop_position", "platform"] }, 
        {"subway": true},
        {"wheelchair": [true, "designated"]} 
    ],
    "__ANY_": {
        "public_transport": ["stop_position", "platform"]
    }
}
```

Or, similarly:

```
{
    "__IMPL_": [ 
        {"public_transport": ["stop_position", "platform"] }, 
        {"subway": true},
        {"wheelchair": [true, "designated"]} 
    ],
    "__ANY_": [
        {"public_transport": ["stop_position", "platform"] }
    ]
}
```

### All-Condition (_ALL_, universal quantification)

Any condition can be turned into universal by using the universal quantification, denoted by the keyword `__ALL_`. 
It naturally makes sense with negated conditions, as seen in the following example, where we define the condition of a location not having public transport accessibility, that is, for all queried map elements in its proximity, there is no public transport stop or platform tag. In other words, neither of the queried map elements is a public transport stop or platform object:

```
{
    "__ALL_": {
        "__NOT_": { "public_transport": ["stop_position", "platform"] }
    }
}
```

The last single implication occured in the previous section is logically equivalent with the following condition, literally stating that each map object in the proximity must either not be a public transport stop or platform, or not being tagged with subway=yes, or be wheelchair-accessible, for the location to belong to the category defined by this rule:
```
{
    "__ALL_": [
         { "__NOT_": { "public_transport": ["stop_position", "platform"] },
         { "__NOT_": { "subway": true },
         { "wheelchair": [true, "designated"] }
    ]
}
```

Warning! If the input set of map objects in the proximity happens to be empty, the result of a universal quantification for the empty set will be `true`.

To avoid this, a combined formula with the existential part follows, being equivalent to the last two formulae in the previous section (see more on ANY in the next section):

```
{
    "__ALL_": [
         { "__NOT_": { "public_transport": ["stop_position", "platform"] },
         { "__NOT_": { "subway": true },
         { "wheelchair": [true, "designated"] }
    ],
    "__ANY_": {
        "public_transport": ["stop_position", "platform"]
    }    
}
```


Note that whenever a reference to a quantified (sub)expression is defined, its name must start with `##`. More explanation follows. 

### Any-Condition (_ANY_, existential quantification)

Similarly to the universal quantification introduced above, the existential quantifier "__ANY_" can be used in rules, stating explicitly that at least one map object in the proximity of the location must be found with the nested condition, in order the location to match the category defined by the rule.

The following two rule examples are equivalent when they define a category without any other rules. In fact, the first one is a shorthand for the second one:

```
{ "public_transport": "stop_position" }
```

```
{
    "__ANY_": { "public_transport": "stop_position" }
}
```

An explicit existential quantification makes sense, for example, if we want a location category which states to have multiple facitilites in its proximity with tag conditions not being applied to the same object. The following example is a rule which matches a location having both a light-rail and a subway stop in its proximity, which might be tags of different geographical objects:

```
{
    "__ANY_lr": { "public_transport": ["stop_position", "platform"], "light_rail": true },
    "__ANY_sw": { "public_transport": ["stop_position", "platform"], "subway": true }
}
```

It can be simplified with the reference `"#pt_stop": { "public_transport": ["stop_position", "platform"] }` having been defined:

```
{
    "__ANY_lr": { "__REF_": "#pt_stop", "light_rail": true },
    "__ANY_sw": { "__REF_": "#pt_stop", "subway": true }
}
```

### The Two-Level Nature of the Rule Language

A simple condition is evaluated in principle for each queried map object in the proximity of a location being categorized, 
and thus produces a true/false value for each single map object. These single values must eventually be aggregated into a single true/false value
so that it can be decided whether the location (having a _set_ of map objects queried in its proximity) actually belongs to a particular category.
This is always done by using quantifiers, either explicitly or implicitly.

OpenLostCat applies quantifiers to each rule expression defining a category at some point. If the whole expression is explicitly quantified using `__ANY_` or `__ALL_`,
then it is already complete. If not, OpenLostCat wraps the expression implicitly with a quantifier, whose type depends on the operators in the expression (explained below in a separate section).

Therefore, each rule defining a category must be quantified, either explicitly or implicitly. This results in our language having two levels of (sub)expression:
* _Item-level_ (a.k.a. _filter-level_) subexpressions are non-quantified expressions being evaluated on an input set of queried map objects in the proximity of the location one-by-one, 
thus resulting a subset of their input set with the matching map objects (actually, the tag bundles of them). They can be either
  * Atomic filters or constants (true/false) or
  * Compound expressions formed using logical connectives (and, or, not, implication), which function similarly to set operatios (resulting the actual set of matching map objects).
* _Category-level_ (a.k.a. _bool-level_) (sub/)expressions are (explicitly or implicitly) quantified expressions resulting a single boolean value. 
  * _Quantifiers_ operate on item-level subexpressions and produce a single aggregated boolean value (from the matching set of objects, wheter it is empty or equals the full set), 
  * Other logical operations (and, or, not, implication) on the category level work with single boolean inputs and produce boolean results.

### Complex Rule Cases

As we have seen in the section of any-conditions, logical operators can be used on the category-level as well, making it possible to combine quantified expressions for defining a category.
All simple logical constructs (and, or, not, implication) can be used both on the item-level as filter conditions, or the (quantified) category-level as (simple) boolean conditions.

For example, the following rule states a location belongs to the category being defined if all public transport facilities nearby are wheelchair-accessible, and there is at least one wheelchair-accessible supermarket nearby as well:

```
{
    "__ALL_": {
        "__IMPL_": [ 
            {"public_transport": ["stop_position", "platform"] }, 
            {"wheelchair": [true, "designated"]} 
        ]
    },
    "__ANY_": {
        "shop": "supermarket",
        "wheelchair": [true, "designated"]
    }
}
```

Note that the implication part is an item(filter)-level subexpression, while the parts enclosed with the quantifiers ALL and ANY, as well as the whole expression are category(bool)-level (sub)expressions.

Considering implicit quantifier wrapping, the above expression is equivalent with either one of the following.  
```
{
    "__IMPL_": [ 
            {"public_transport": ["stop_position", "platform"] }, 
            {"wheelchair": [true, "designated"]} 
    ],
    "__ANY_": {
        "shop": "supermarket",
        "wheelchair": [true, "designated"]
    }
```
```
{
    "__ALL_": {
        "__IMPL_": [ 
                {"public_transport": ["stop_position", "platform"] }, 
                {"wheelchair": [true, "designated"]} 
        ]
    },
    "__AND_": {
        "shop": "supermarket",
        "wheelchair": [true, "designated"]
    }
```

Note that one of the quantifiers must be kept, since it will explicitly raise the level of expression to the category (bool) level, enforcing an implicit quantification of the other operand. If both quantifiers were omitted, the expression would remain on the item (filter) level, and therefore, the whole as a conjunction (AND condition) would be implicitly quantified, which would not be equivalent with the above. 

Nor the explicit `__AND_` condition cannot be left out from the latter variant, since otherwise the atomic filters would be quantified one by one, meaning the two tags may belong to different geographical objects.

### The Two Types of References (# vs. ##)

As mentioned already, references are named subexpressions as shorthands for reusing them multiple times in the rules. Their definition looks similar as a category definition but their name starts with `#`. Names of some references start with `##`. This distinction has a meaning, and separates two types of references explicitly:

* __Non-quantified, item(filter)-level references start with a single `#`.__ They define a property being evaluated for potentially each single map object in the proximity of a location being categorized. 
These references can be used inside quantified expressions, or can be used directly as category-level expressions in which case they will be implicitly wrapped by a quantifier.
* __Quantified, category(bool)-level references start with `##`.__ They define a property being evaluated once for the whole set of map objects in the proximity of a location being categorized.
These references must either be explicitly quantified in their definition expression, or will be implicitly wrapped with a quantifier directly. They can be used as a standalone category definition or combined with category(bool)-level operators to define more complex category rules.

In short: A reference with a double `##` prefix can be used only on the category (bool) level (if it contains a set/filter level expression, it will implicitly be quantified _by_ the reference itself), while a reference with a single `#` prefix can either be used on the set/filter level or on the category/bool level, in the latter case, implicit quantification will be done on the level of expression containing the reference. An explicitly quantified expression can not be used in a reference with a single `#` prefix. 

For instance, the complex example above can alternatively be defined by references, where the wheelchair-accessibility (barrier-freeness) is defined as an item-level reference as being a property of single map objects, and the condition of the existence of a barrier-free supermarket on one hand, and the public transport facilities being each barrier-free on the other hand, are defined as category-level references:

```
"categoryRules": [
    {
        "#barrier-free": {"wheelchair": [true, "designated"]}
    },
    {
        "##all-pt-bf": {
            "__ALL_": {
                "__IMPL_": [ 
                    {"public_transport": ["stop_position", "platform"] }, 
                    "#barrier-free" 
                ]
            }
        }
    },
    {
        "##any-sm-bf": {
            "__ANY_": {
                "shop": "supermarket",
                "__REF_": "#barrier-free"
            }
        }
    },
    {
        "barrier-free-shopping-hub-category": {
            "__REF_1": "##all-pt-bf",
            "__REF_2": "##any-sm-bf"
        }
    }
]
```

Since the implication wraps with an ALL, and the conjunction of simple conditions wrap into an ANY, the above rules can be shortened by the following. Note this is because the reference prefix `##` enforces the expression to become category(bool)-level, and the referenced subexpression will be wrapped with a quantifier directly at the point of the reference. 

```
"categoryRules": [
    {
        "#barrier-free": {"wheelchair": [true, "designated"]}
    },
    {
        "##all-pt-bf": {
            "__IMPL_": [ 
                {"public_transport": ["stop_position", "platform"] }, 
                "#barrier-free" 
            ]
        }
    },
    {
        "##any-sm-bf": {
            "shop": "supermarket",
            "__REF_": "#barrier-free"
        }
    },
    {
        "barrier-free-shopping-hub-category": {
            "__REF_1": "##all-pt-bf",
            "__REF_2": "##any-sm-bf"
        }
    }
]
```

Note that in the latter example, the ##-named references could syntactically have been #-named references as well, but the meaning of the whole ruleset would have been different (and thus incorrect), due to the fact that the implicit quantifier wrapping will not be enforced at the point of the usage of the references, but only at the top-level of the whole expression.

The defined references can be (re)used for creating other categories in a simple manner, such as, for example, being added to the array of `categoryRules`:

```
        "any-barrier-free-shopping-category": "##any-sm-bf",
        "all-barrier-free-pt-category": "##all-pt-bf",
        "either-any-bf-sm-or-all-bf-pt-category": [ "##any-sm-bf", "##all-pt-bf" ],
        "any-barrier-free-facility-category": "#barrier-free"
```

Note that the last category is defined using an item(filter)-level reference expression consisting only a non-negated atomic filter, which is being wrapped by an existential quantifier implicitly. In other terms, the last category definition is a shorthand of the following one:
```
        "any-barrier-free-facility-category": { "__ANY_": "#barrier-free" }
```

### Quantifier Wrapping in Detail

If a non-quantified (item-level, a.k.a. filter-) (sub)expression appears somewhere where a quantified (category-level, a.k.a. bool-) expression is required, OpenLostCat wraps the (sub)expression implicitly with a quantifier. In most cases the wrapper becomes an `__ANY_`, which means the default usual interpretation of non-quantified expressions is existential, that is, to find if there is at least one map object in the proximity of the location matching the expression as a rule. However, there are cases when the default quantifier becomes `__ALL_` as will be explained below. 

Recall from the section of any-conditions the following examples as being equivalent, with the first one being a shorthand for the second one:

```
{ "public_transport": "stop_position" }
```

```
{
    "__ANY_": { "public_transport": "stop_position" }
}
```

Any combinations of such positive atomic filter conditions with _and_, _or_ constructs will be wrapped by default with `__ANY_` when directly used as the definition of a category.

However, for instance, in the case of the negation or the implication, the default wrapper quantifier is `__ALL_`. Therefore, the following two examples are equvalent, with the first one being a shorthand for the second one:

```
{ 
    "__NOT_": { 
        "public_transport": ["stop_position", "platform"],
        "wheelchair": [true, "designated"]
    }
}
```

```
{
    "__ALL_": {
        "__NOT_": { 
            "public_transport": ["stop_position", "platform"],
            "wheelchair": [true, "designated"]
        }
    }
}
```

The same equivalence holds for the following implication expressions:

```
{ 
    "__IMPL_": [ 
        {"public_transport": ["stop_position", "platform"] }, 
        {"wheelchair": [true, "designated"]} 
    ]
}
```

```
{
    "__ALL_": {
        "__IMPL_": [ 
            {"public_transport": ["stop_position", "platform"] }, 
            {"wheelchair": [true, "designated"]} 
        ]
    }
}
```


The and-combination of negation or implication subexpressions will also result in universal quantification. In other words, defining two or more negation or implication rules for a single category will be interpreted as each of them must hold for all map objects in the proximity of the location, to be in the defined category. It is, in fact, follows the common-sense interpretation of combining negation or implication rules. 

The following examples are therefore equivalent, with the first one being a shorthand of the second one, meaning a place belongs to the category being defined if _all_ nearby public transport services and supermarkets are wheelchair-accessible:

```
{ 
    "__IMPL_pt_wa": [ 
        {"public_transport": ["stop_position", "platform"] }, 
        {"wheelchair": [true, "designated"]} 
    ],
    "__IMPL_sm_wa": [ 
        {"supermarket": true }, 
        {"wheelchair": [true, "designated"]} 
    ]
}
```

```
{
    "__ALL_": {
        "__IMPL_pt_wa": [ 
            {"public_transport": ["stop_position", "platform"] }, 
            {"wheelchair": [true, "designated"]} 
        ],
       "__IMPL_sm_wa": [ 
            {"supermarket": true }, 
            {"wheelchair": [true, "designated"]} 
        ]
     }
}
```

Quantifier wrapping is well-defined for any combination of different subexpressions using the following rules:

If a set(filter)-level (sub)expression becomes a top-level (sub)expression defining a category, 
or becomes an operand of a multi-ary logical operator having category(bool)-level operands (subexpressions),
the set(filter)-level (sub)expression will be wrapped by a quantifier to become a category(bool)-level (sub)expression.

Each set(filter)-level operator type has its default wrapper quantifier for the cases 
wherever a category(bool)-level (sub)expression is expected and it must be wrapped to become such:
* wrapper quantifier of an atomic filter (or the boolean constant false) will default to ANY
* wrapper quantifier of a 'not' switches the inherited default wrapper quantifier from its subexpression (operand) between ANY and ALL
* wrapper quantifier of implication will default to the wrapper quantifier corresponding to its equivalent rewrite with not-or (usually becomes ALL, esp. when contains positive subexpressions only),
* wrapper quantifier of a #ref is inherited from its subexpression (operand)
* wrapper quantifier of 'and' will default to ALL if each of its subexpressions (operands) defaults to ALL, otherwise it will default to ANY
* wrapper quantifier of 'or' will default to ALL if at least one subexpressions (operands) defaults to ALL, otherwise it will default to ANY.

For complex cases, it is however advised to use explicit quantifiers as it is easier to be followed by human eyes.

This way, logically equvalent (sub)formulae will imply the same implicit quantifier, as implicit quantification depends not on the way the formula is expressed but on the eventual 'negatedness' of its variable-dependant parts. If an odd number of nested negations are present the implicit quantifier becomes universal, if an even or no nested negation is present then existential. If both types of negation nesting occurs in a formula, then the implication logic is followed eventually.

In more sophisticated logics terms, we can state that implicit quantification for a formula is defined generally as _existential_, except when _each_ of the disjunctive subformulas in its _conjunctive normal form_ has _at least one negated_ atomic operand (or an operand being the _false_ boolean constant). In that case, the implicit quantifier applied will be _universal_. This principle is exactly that of Zeman (1967) in his paper entitled _A System of Implicit Quantification_ (The Journal of Symbolic Logic 32(4), pp 480-504).

This is in correspondance with the common-sense interpretation that in a large set with a lot of variety, positive conditions implicitly considered as existential and negative statements as universal, and the implication as universal. 


### Expressive Power and Algebraic Equivalences

The rule language of OpenLostCat is a univariate first-order logic, somewhat similar to tuple calculus. It is relatively simple with an expressive power suited to usual scenarios as listed earlier in this document.

A category assessment is based on exact values of OpenStreetMap tags, or the presence or absence of tags, logical combinations of such item-based conditions - on the item/filter level -, the existence of an element in the set of nearby map objects (in a given proximity of the location) with such properties, or a universal condition regarding such properties - for instance, all elements in the set of nearby objects must have a specific tag, value or constellation -, and finally, logical combinations of such existential or universal conditions on the category level. 

As the general logical equivalences hold (such as the algebaic commutativity, associativity, distributivity etc. of logical operators), the same meaning can be expressed usually in different forms.

A classical equivalence is the exchangeability of quantifiers with negation, which swaps the quantifiers, such as in the following example, which defines a category where no primary or secondary road is present. The two rules are logically equivalent:

```
"__ALL_" : {
    "__NOT_" : {"highway": ["primary", "secondary"]}
}
```

```
"__NOT_" : {
    "__ANY_" : {"highway": ["primary", "secondary"]}
}
```

Note that both of the above formulae are equivalent with the one below, as it will actually produce the first one above by implicit quantification:

```
{
    "__NOT_" : {"highway": ["primary", "secondary"]}
}
```

The above quantifier-negation interchangeability can be derived from the so-called _De Morgan_ rules, stating the interchangeability of negation with conjunctive and disjunctive conditions in the following way. The two expressions below are equivalent:

```
{
    "__NOT_": [
        {"public_transport": ["stop_position", "platform"] },
        {"amenity": "ferry_terminal"}
    ]       
}
```
```
{
    "__NOT_1": { "public_transport": ["stop_position", "platform"] },
    "__NOT_2": { "amenity": "ferry_terminal"}
}
```
And similarly:
```
{
    "__NOT_": { 
        "public_transport": ["stop_position", "platform"], 
        "wheelchair": [true, "designated"]
    }
}
```
```
{
    "__OR_": [
        { "__NOT_": { "public_transport": ["stop_position", "platform"] } }, 
        { "__NOT_": { "wheelchair": [true, "designated"] } }
    ]
}
```

Note that for each of the four formulae above, the implicit wrapper quantifier will be ` __ALL_ `.

Equivalences present on the level of multiple categories as well.

For example, using first-matching category evaluation, the following two examples are equvalent definitions of a category catalog (if the allowed values for _wheelchair_ are the listed ones in the second variant):

```
"categoryRules": [
    {
        "#wheelchair_accessible": {"wheelchair": [true, "limited", "designated"]}
    }
    {
        "wheelchair_shopping": { "shop": "supermarket", "#wheelchair_accessible" }
    },
    {
        "wheelchair_shopping_paradise": {
            "__IMPL_": [{"shop": "supermarket"}, "#wheelchair_accessible"]
         }
    },
    {
        "no_wheelchair_shopping": true
    }
]
```

```
"categoryRules": [
    {
        "no_wheelchair_shopping": {
            "__IMPL_": [{"shop": "supermarket"}, {"wheelchair": [false, null]}]
        }
    },
    {
        "wheelchair_shopping_paradise": {
            "__IMPL_": [{"shop": "supermarket"}, {"wheelchair": [true, "limited", "designated"]}]
         }
    },
    {
        "wheelchair_shopping": true
    }
]
```

### Repeating Category Names

An alternative way of expressing certain rules is by utilizing the explicit order of rules and (re)using the same category name at different points.

It is possible to define a category name multiple times. Since OpenLostCat indexes the categories, such a definition will yield a category assignment with a different index but the same name. This can be utilized in special cases, when, for example, the user treats these as a single category by name, but wants to know which rule caused the location being categorized as such.

The following rules assign the same category name to locations with general public transport stops and stations, and locations having only ferry connections, but the latter gets a different numeric index for its category:

```
"categoryRules": [
    {
        "pt_accessible": {"public_transport": ["stop_position", "platform"] }
    },
    {
        "pt_accessible": {"amenity": "ferry_terminal"}
    },
    {
        "pt_inaccessible": true
    }
]
```

Another example is when a category is defined using a positive-negative-positive scheme, such as in the following example, where the third category definition rule (after the reference definition) yields the same category name as the first one, but gets a different numeric index for the category (indicating here the locations with bus stops being only tagged using legacy tagging scheme):

```
"categoryRules": [
    {
        "#pt_stop": { "public_transport": ["stop_position", "platform"] }
    },
    {
        "bus_accessible": { "bus": true, "__REF_": "#pt_stop"}
    },
    {
        "pt_accessible": "#pt_stop"
    },
    {
        "bus_accessible": {"highway": "bus_stop"}
    },
    {
        "pt_inaccessible": true
    }
]
```

Both of the above examples are meant being evaluated by the (default) first matching strategy. 

If only the category names are relevant, they can be rewritten using the logical operators without a default rule.

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

AtomicFilter ::= "[^_].*" : ValueOrListOrEmptyObj
ValueOrListOrEmptyObj ::= SingleValue | [SingleValue, ...] | { }
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

## Quick User Reference of Classes and Methods 


### MainOsmCategorizer 
[main_osm_categorizer.py](openlostcat/main_osm_categorizer.py) 

Methods:

#### Constructor
```__init__(self, category_catalog_source, debug=False, category_catalog_parser=None)```

Initializes the categorizer by setting up the category catalog

Parameters
 - `category_catalog_source`:   a JSON structure as python dictionary or a file path string
 - `debug`:                     Boolean, set to true for more detailed output
 - `category_catalog_parser`:   parse using the given parser
 
 Example
 
 ```categorizer =  MainOsmCategorizer(json.loads('{ "type": "CategoryRuleCollection", "categoryRules": [ { "pt_accessible": { "public_transport": "stop_position" } }, { "pt_inaccessible": true } ] }'))```
 
 _or_
 
 ```categorizer = MainOsmCategorizer('rules/publictransport_rules.json')```
 ___
 
#### categorize

```categorize(self, osm_json_dict)```

Categorizes a location by the osm tag bundle set of the objects located there/nearby

Parameters
 - `osm_json_dict`: tag bundle set of the osm objects at/near the location
 
 `return` categories matching the location by the given strategy
 
 
Example

```categorizer.categorize(osm_neighborhood_railway_station)```
```categorizer.categorize(ask_osm_around_point(47.5001, 19.0247, distance = 300))```
 
___

#### get_categories_enumerated_key_map
 
```get_categories_enumerated_key_map(self)```
 
 

```get_categories_enumerated_key_map()```

Retrieves the categories parsed by init

`return` categories

Example

```categorizer.get_categories_enumerated_key_map()```

___
#### print

Visualization of the category catalog (set of parsed expression rules)

```print(categorizer)```

___

### Ask_osm
[osmqueryutils/ask_osm.py](openlostcat/osmqueryutils/ask_osm.py)

Methods:

#### ask_osm
```ask_osm(query, url=overpass_url)```

Queries the Overpass API with a query string

Parameters
 - `query`: an overpass query string
 - `url`:   API address
 
 `return` query results in json
 
 Example
 
 ```
 ask_osm("""[out:json];
                nwr[tourism=hotel](47.507, 19.034, 47.566, 19.063);
            out tags center;""")
 ```
 
___
#### ask_osm_around_point

```ask_osm_around_point(lat, lng, distance=100, url=overpass_url)```

Queries the Overpass API around a point with a distance as radius

Parameters
 - `lat`:       wgs84 latitude
 - `lng`:       wgs84 longitude
 - `distance`:  radius in meters
 - `url`:       API address
 
 `return` query results in json
 
 Example
 
 ```ask_osm_around_point(47.5001, 19.0247, distance = 300)```
 
___
#### ask_osm_around_point_df
 
```ask_osm_around_point_df(df_row, distance=100, url=overpass_url)```

Queries the Overpass API around a point with a distance as radius, given in a dataframe

Parameters
 - `df_row`:    a dataframe row with wgs84 coordinates in fields named lat, lng
 - `distance`:  radius in meters
 - `url`:       API address
 
 `return` query results in json
 
 Example
 
 ```df.T.apply(ask_osm_around_point_df)``` 
 _or_  
 ```df.apply(ask_osm_around_point_df, axis = 1)```
 
___
#### ask_osm_around_point_np

```ask_osm_around_point_np(coord_row, distance=100, lat_index=0, lng_index=1, url=overpass_url)```

Queries the Overpass API around a point with a distance as radius, given in a np array of coords

Parameters
 - `df_row`:    a dataframe row with wgs84 coordinates in fields named lat, lng
 - `distance`:  radius in meters
 - `url`:       API address
 
 `return` query results in json
 
 Example
 
 ```np.apply_along_axis(ask_osm_around_point_np, 1, coords)```

## Quick User Reference of JSON Rule Operators

A valid OpenLostCat rule collection JSON file looks like: 


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
     ][ "##pt_accessible", { "__ANY_" : { "shop" : "supermarket" } } ]
}
```

The operators used in category and reference definitions are the following: 

|  Name *        |  Operator Level {Default quantifier wrapper}                 |  Description                                                                                                          |  Key-value syntax  |  Standalone syntax  |  Example  |
|  ----         |  -----                                                        |  -----------                                                                                                          |  ----------------  |  -----------------  |  -------  |
| atomic filter |  item(filter) {ANY}                                           |  Tests whether a tag value equals the given value, or any of the given values (list case), or is missing (null)       |  `"key" : "value"`, `"key" : ["value1", ...]`, `"key" : null` | - | `"public_transport" : "stop_position"`, `"public_transport" : ["stop_position", "platform"]` |
| const         |  item(filter) {true: ALL, false: ANY}                                         |  Always true or false, according to the value given.                                                                  |  `"__CONST_xy" : true`, ˙"__CONST_xy": false˙ | `true`, `false` | `true` |
| CONST         |  category(bool)                                               |  Always true or false, according to the value given.                                                                  |  `"__CONST_xy" : true`, ˙"__CONST_xy": false˙ | `true`, `false` | `true` |
| ANY           |  item(filter) --> category(bool)                              |  Tests whether the truth set of the operand is not empty (there is at least one item for which the operand it true).  |  `"__ANY_xy" : ...` | - |  `"__ANY_": { "public_transport" : "stop_position" }` |
| ALL           |  item(filter) --> category(bool)                              |  Tests whether the truth set of the operand equals to the input set (the operand it true for all items).              |  `"__ALL_xy" : ...` | - |  `"__ALL_": { "public_transport" : null }` |
| ref (#)       |  item(filter) {inherits from operand}                         |  Tests whether the expression defined by the reference is true (gives the truth set of the operand).                  |  `"__REF_xy" : "#ref_name"` | `"#ref_name"` | `"#pt_platform"` where it was defined in a separate rule ss ` { "#pt_platform" : { "public_transport" : "stop_position" } }` | 
| REF (##)      |  category(bool)                                               |  Tests whether the expression defined by the reference is true.                                                       |  `"__REF_xy" : "##ref_name"` | `"##ref_name"` | `"##pt_accessible"` where it was defined in a separate rule ss ` { "##pt_accessible" : { "__ANY_": { "public_transport" : "stop_position" } } }` |
| and           |  item(filter) {ALL if each operand wraps to ALL, else ANY}    |  True if all operands are true (intersects the truth sets of the operands).                                           |  `"__AND_xy" : { ..., ..., ..... }` | `{ ..., ..., ..... }` | `{"public_transport" : "stop_position", "wheelchair" : "yes" } |
| AND           |  category(bool)                                               |  True if all operands are true.                                                                                       |  `"__AND_xy" : { ..., ..., ..... }` | `{ ..., ..., ..... }` | `{ "__REF_" : "##pt_accessible", "__ANY_" : { "shop" : "supermarket" } } }` |
| or            |  item(filter) {ALL if either operand wraps to ALL, else ANY}  |  True if either of the operands is true (unites the truth sets of the operands).                                      |  `"__OR_xy" : [ ..., ..., ..... ]` | `[ ..., ..., ..... ]` | `[ "#pt_platform", { "shop" : "supermarket" } ]` |
| OR            |  category(bool)                                               |  True if either of the operands is true.                                                                              |  `"__OR_xy" : [ ..., ..., ..... ]` | `[ ..., ..., ..... ]` | `[ "##pt_accessible", { "__ANY_" : { "shop" : "supermarket" } } ]` |
| not           |  item(filter) {switches ALL<->ANY inherited from operand}                         |  Negates the truth value of the operand (forms the complementer set of the truth set of the operand).                 |  `"__NOT_xy" : ...` | - | `"__NOT_" : { "shop" : null }` |
| NOT           |  category(bool)                                               |  Negates the truth value of the operand.                                                                              |  `"__NOT_xy" : ...` | - | `"__NOT_" : "##pt_accessible"` |
| impl          |  item(filter) {Ihnerits from the OR operand of its rewritten format (usually ALL)}                                           |  Tests whether the last operand (conclusion) is implied by the other operands (premises).                             |  `"__IMPL_xy" : [ ..., ..., ..... ]` | - | `"__IMPL_" : [ "#pt_platform", { "wheelchair" : "yes" } ]` |
| IMPL          |  category(bool)                                               |  Tests whether the last operand (conclusion) is implied by the other operands (premises).                             |  `"__IMPL_xy" : [ ..., ..., ..... ]` | - | `"__IMPL_" : [ "##pt_accessible", { "__ANY_" : { "shop" : "supermarket" } } ]` |

Remark: * Names are written always in uppercase in rule defitions. Here, writing of names follow the way they are output by the OpenLostCat AST console log (lowercase: set-level, uppercase: category-level operators).   

## Further Info and Contribution

See the Developers' Documentation in [devdoc](devdoc/).

Contact the creators Gábor Lukács ([lukacsg](https://github.com/lukacsg)) and András Molnár ([zarandras](https://github.com/zarandras)) with any questions, suggestions or contributions.


