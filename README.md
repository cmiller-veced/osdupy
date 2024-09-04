# osdupy readme

There is low-hanging fruit and we are going to pluck it.

First step is to read swagger / OpenAPI files.
These files are in json/yaml.
We shall take the things we find there and represent them as data.

# How to do it?

We follow some straightforward principles that I've learned by studying ...

- the Unix Philosophy
- the Agile Manifesto
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

## Links

- https://swagger.io/specification/
- https://docs.python.org/3/library/json.html
- https://agilemanifesto.org
- https://en.wikipedia.org/wiki/Unix\_philosophy
- https://daringfireball.net/projects/markdown/
- https://github.com
- https://docs.pydantic.dev/latest/
- https://marshmallow.readthedocs.io/en/stable/
- https://www.paulgraham.com
- https://github.com/boto/botocore
- https://pypi.org/project/PyYAML/

### TODO

- hyperlinks
- code
- data source






