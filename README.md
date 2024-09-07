# osdupy readme

There is low-hanging fruit and we are going to pluck it.

First step is to read swagger / OpenAPI files.
These files are in json/yaml.
We shall take the things we find there and represent them as data.
DONE

Next step is to validate data against the swagger.  The tricky part is getting
references.  Worthwhile because it keeps us in the original data format.  No
DAO (data access objects).

Other tasks present themselves as we go.  Navigating json data is tedious
without good tools so we create the tools as we go.
Yes, I know there are tools out there already.  But I want GOOD tools.


# How to do it?

We follow some straightforward principles that I've learned by studying ...

- the Unix Philosophy
- the Agile Manifesto
- good code
- bad code
- etc

There are important factors that are routinely ignored in typical Python
programming.  Two of these include...

- do not duplicate effort
- do not transform without justification

If someone else has already defined important data we will not repeat that
effort.  Likewise, when we receive data we will not transform it without a good
reason.  "our programmers like Pydantic" (or other xxx) is not a good reason.

Our target users are people who understand the swagger.  The goal is to remove
the need for the programmer between the data analyst and the data.

Our system will be intuitive for data analysts.

We pull data from swagger and use it.  Unfortunately, swagger files often
contain errors so a pre-processing step(s) is required.

Tests are written BEFORE code.  When tests are written after code the bugs
become baked into the tests.  Fooey on that!

Using swagger as data has multiple benefits.

- no duplication of effort that went into swagger defs
- a record of swagger errors

We do not have to define our data if someone else (the swagger author) has
already done it.  This is a huge benefit.

Our tests will reveal any errors in the swagger.  Errors are corrected in the
pre-processing step.  Errors also generate bug reports to the swagger maintaner.
Given the option of multiple swagger sources we go for the one with fewest
errors and best responsiveness to bug reports.

Swagger is not the only acceptable data source.  It is a good data source
because it is a well-defined json/yaml representation with good documentation.
There are plenty of other good options, for example botocore.  botocore is
a well thought-out system.
The important thing is to have a well-defined, slowly changing interface.  If we
have that we can write code quickly to leverage the API.  If we have competition
that prefers the xxx/marshmallow/pydantic approach of manually defined Python
classes, so much the better.  We will run circles around them.  (read Paul
Graham).

### Our motivation

- https://agilemanifesto.org
- https://en.wikipedia.org/wiki/Unix_philosophy
- https://github.com/boto/botocore
- https://www.paulgraham.com
- https://d3js.org

d3js is a javascript library that provides a minimal wrapper around SVG.  If you
understand SVG, d3js will make a lot of sense to you.

- https://aframe.io/docs/1.6.0/introduction/

Aframe is a javascript library around (WebGL?).



### Our tools

- https://swagger.io/specification/
- https://docs.python.org/3/library/json.html
- https://daringfireball.net/projects/markdown/
- https://github.com
- https://json-schema.org
- https://json-schema.org/understanding-json-schema
- https://developer.mozilla.org/en-US/docs/Web/API/

-----------------------------

- https://www.postman.com
- https://pypi.org/project/PyYAML/
- https://jinja.palletsprojects.com/en/3.1.x/

Jinja does for text strings, something like what d3js does for svg.  A minimal
way of inserting data into a fixed string.

### Not our tools

There is nothing wrong with the below tools.  If we have reason, we will use
them.  But it requires justification.  Unfamiliarity with functional programming
in Python is not justification.  "Everyone does it that way." is not
justification.

- https://docs.pydantic.dev/latest/
- https://marshmallow.readthedocs.io/en/stable/

These tools tend to make life easy for programmers and their managers.  Most
programmers are familiar with the approach.  It's not too demanding and provides
a simple, rigid interface.  Our goal is to make life easy for the data analyst
or manager who is interested in exploring the interface in real time without
waiting for programmers to define their options for them.

The code we write will demand more from the programmer but will be far more
compact than code written using the above approach.  Also far more flexible.
The data analyst will thank us.



### TODO

- hyperlinks
- code
- data source

### Potential data sources

- https://documents.worldbank.org/en/publication/documents-reports/api
- https://fred.stlouisfed.org/docs/api/fred/
- https://opensource.fb.com/projects/
- https://developer.x.com/en/docs/x-api

### swagger petstore

We are currently using the Petstore data from the swagger docs.

- https://petstore.swagger.io/v2/swagger.json


### Interfaces / handoffs / context switch / complexity

Cognitive load is not a joke.


### Functional programming in Python

Python has almost all functional programming features of Lisp, except macros.

To get a handle on functional programming in Python, decorators are a good
starting point.  The coder who has a solid understanding of decorators is well
on the way to having a good grounding in functional programming in Python.
There are several things to consider.

- basic decorator
- class-based decorator

The first thing with decorators is to understand the simplest possible version.
Then we can move on to class-based decorators.   One could gain a solid
understanding without ever using class-based decorators but they are good to
know about and understand.  One could make the argument that a class-based
decorator is sort of like object-oriented Perl or a dog walking on its hind
legs.  You can do it but it is ugly and does not work well.  So feel free to
skip class-based decorators at first but come back and figure them out later.

Parameterized decorators, on the other hand, are essential for a good
understanding.  Decorators (and particularly parameterized decorators) are
a special case of Python functional programming.  But once you really understand
parameterized decorators you will begin to understand where functional
programming can be used most effectively.

Python is a multi-paradigm language.  It's support for functional programming is
solid and baked in.  It's not going away.  Treating Python as a strictly OO
language is like sawing off one of the legs of your three-legged stool.
You miss out on a lot.


# Glossary

- DAO: data in object drag


