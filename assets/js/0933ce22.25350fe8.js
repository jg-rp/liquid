"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[9086],{3905:(e,t,n)=>{n.d(t,{Zo:()=>d,kt:()=>k});var a=n(7294);function i(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function l(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function r(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?l(Object(n),!0).forEach((function(t){i(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):l(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function o(e,t){if(null==e)return{};var n,a,i=function(e,t){if(null==e)return{};var n,a,i={},l=Object.keys(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||(i[n]=e[n]);return i}(e,t);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(i[n]=e[n])}return i}var p=a.createContext({}),s=function(e){var t=a.useContext(p),n=t;return e&&(n="function"==typeof e?e(t):r(r({},t),e)),n},d=function(e){var t=s(e.components);return a.createElement(p.Provider,{value:t},e.children)},u="mdxType",m={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},c=a.forwardRef((function(e,t){var n=e.components,i=e.mdxType,l=e.originalType,p=e.parentName,d=o(e,["components","mdxType","originalType","parentName"]),u=s(n),c=i,k=u["".concat(p,".").concat(c)]||u[c]||m[c]||l;return n?a.createElement(k,r(r({ref:t},d),{},{components:n})):a.createElement(k,r({ref:t},d))}));function k(e,t){var n=arguments,i=t&&t.mdxType;if("string"==typeof e||i){var l=n.length,r=new Array(l);r[0]=c;var o={};for(var p in t)hasOwnProperty.call(t,p)&&(o[p]=t[p]);o.originalType=e,o[u]="string"==typeof e?e:i,r[1]=o;for(var s=2;s<l;s++)r[s]=n[s];return a.createElement.apply(null,r)}return a.createElement.apply(null,n)}c.displayName="MDXCreateElement"},8508:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>p,contentTitle:()=>r,default:()=>m,frontMatter:()=>l,metadata:()=>o,toc:()=>s});var a=n(7462),i=(n(7294),n(3905));const l={},r="Extra Tags",o={unversionedId:"extra/tags",id:"extra/tags",title:"Extra Tags",description:"This page documents extra tags that are not included in standard Liquid. See the tag reference for details of all standard tags. Each tag described here must be registered with a liquid.Environment to make it available to templates rendered from that environment.",source:"@site/docs/extra/tags.md",sourceDirName:"extra",slug:"/extra/tags",permalink:"/liquid/extra/tags",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/extra/tags.md",tags:[],version:"current",frontMatter:{},sidebar:"languageSidebar",previous:{title:"Extra Filters",permalink:"/liquid/extra/filters"},next:{title:"Python Liquid Babel",permalink:"/liquid/babel/introduction"}},p={},s=[{value:"extends / block",id:"extends--block",level:2},{value:"Block Names",id:"block-names",level:3},{value:"Block Scope",id:"block-scope",level:3},{value:"Required Blocks",id:"required-blocks",level:3},{value:"Super Blocks",id:"super-blocks",level:3},{value:"if (not)",id:"if-not",level:2},{value:"Parentheses",id:"parentheses",level:3},{value:"inline if / else",id:"inline-if--else",level:2},{value:"With Filters",id:"with-filters",level:3},{value:"macro / call",id:"macro--call",level:2},{value:"Excess Arguments",id:"excess-arguments",level:3},{value:"with",id:"with",level:2}],d={toc:s},u="wrapper";function m(e){let{components:t,...n}=e;return(0,i.kt)(u,(0,a.Z)({},d,n,{components:t,mdxType:"MDXLayout"}),(0,i.kt)("h1",{id:"extra-tags"},"Extra Tags"),(0,i.kt)("p",null,"This page documents extra tags that are not included in standard Liquid. See the ",(0,i.kt)("a",{parentName:"p",href:"/liquid/language/tags"},"tag reference")," for details of all standard tags. Each tag described here must be registered with a ",(0,i.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,i.kt)("inlineCode",{parentName:"a"},"liquid.Environment"))," to make it available to templates rendered from that environment."),(0,i.kt)("h2",{id:"extends--block"},"extends / block"),(0,i.kt)("p",null,(0,i.kt)("strong",{parentName:"p"},(0,i.kt)("em",{parentName:"strong"},"New in version 1.8.0"))),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain"},'{% extends "<string>" %}\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain"},"{% block <identifier,string> [, required] %}\n  <literal,statement,tag> ...\n{% endblock [<identifier,string>] %}\n")),(0,i.kt)("p",null,"The ",(0,i.kt)("inlineCode",{parentName:"p"},"{% extends %}")," and ",(0,i.kt)("inlineCode",{parentName:"p"},"{% block %}")," tags add template inheritance features to Python Liquid. In this example ",(0,i.kt)("inlineCode",{parentName:"p"},"page.html")," inherits from ",(0,i.kt)("inlineCode",{parentName:"p"},"base.html")," and overrides the ",(0,i.kt)("inlineCode",{parentName:"p"},"content")," block. As ",(0,i.kt)("inlineCode",{parentName:"p"},"page.html")," does not define a ",(0,i.kt)("inlineCode",{parentName:"p"},"footer")," block, the footer from ",(0,i.kt)("inlineCode",{parentName:"p"},"base.html")," is used."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import DictLoader\nfrom liquid import Environment\nfrom liquid.extra import add_inheritance_tags\n\nloader = DictLoader(\n    {\n        "base.html": (\n            "<body>\\n"\n            \'  <div id="content">{% block content required %}{% endblock %}</div>\\n\'\n            \'  <div id="footer">{% block footer %}Default footer{% endblock %}</div>\\n\'\n            "</body>"\n        ),\n        "page.html": (\n            "{% extends \'base.html\' %}\\n"\n            "{% block content %}Hello, {{ you }}!{% endblock %}"\n        ),\n    }\n)\n\nenv = Environment(loader=loader)\nadd_inheritance_tags(env)\n\ntemplate = env.get_template("page.html")\nprint(template.render(you="World"))\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-html",metastring:'title="output"',title:'"output"'},'<body>\n  <div id="content">Hello, World!</div>\n  <div id="footer">Default footer</div>\n</body>\n')),(0,i.kt)("p",null,"A template can contain at most one ",(0,i.kt)("inlineCode",{parentName:"p"},"{% extends %}")," tag, and that tag should normally be the first in the template. All other template text and tags (including whitespace) preceding ",(0,i.kt)("inlineCode",{parentName:"p"},"{% extends %}")," will be output normally. Subsequent template text and tags outside any ",(0,i.kt)("inlineCode",{parentName:"p"},"{% block %}")," tags will be ignored, unless rendering a base template directly."),(0,i.kt)("p",null,"As soon as an ",(0,i.kt)("inlineCode",{parentName:"p"},"{% extends %}")," tag is found, template rendering stops and Python Liquid loads the parent template (using the configured ",(0,i.kt)("a",{parentName:"p",href:"/liquid/introduction/loading-templates"},"loader"),") before searching for ",(0,i.kt)("inlineCode",{parentName:"p"},"{% block %}")," tags. We keep loading and searching up the inheritance chain until a parent template with no ",(0,i.kt)("inlineCode",{parentName:"p"},"{% extends %}")," tag is found, this is the ",(0,i.kt)("em",{parentName:"p"},"base")," template."),(0,i.kt)("p",null,"The base template is then rendered, substituting its blocks with those defined in its children."),(0,i.kt)("h3",{id:"block-names"},"Block Names"),(0,i.kt)("p",null,"Every ",(0,i.kt)("inlineCode",{parentName:"p"},"{% block %}")," must have a name and that name must be unique within a single template. Block names must be valid Liquid identifiers, optionally enclosed in quotes (quoted and unquoted block names are equivalent)."),(0,i.kt)("p",null,(0,i.kt)("inlineCode",{parentName:"p"},"{% endblock %}")," tags can include a name too. If given a name and that name does not match the one given at the start of the block, a ",(0,i.kt)("inlineCode",{parentName:"p"},"TemplateInheritanceError")," is raised when parsing the template."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid"},'<body>\n  <div id="content">\n    {% block content %}\n      {% block title %}\n        <h1>Some Title</h1>\n      {% endblock title %}\n    {% endblock content %}\n  </div>\n  <div id="footer">\n    {% block footer %}\n      Default footer\n    {% endblock footer %}\n  </div>\n</body>\n')),(0,i.kt)("h3",{id:"block-scope"},"Block Scope"),(0,i.kt)("p",null,"All blocks are scoped. Variables defined in base templates and enclosing blocks will be in scope when rendering overridden blocks."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="base"',title:'"base"'},"{% assign thing = 'item' %}\n{% for i in (1..3) %}\n  {% block list-item %}{% endblock %}\n{% endfor %}\n")),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="child"',title:'"child"'},'{% extends "base" %}\n{% block list-item %}\n  {{ thing }} #{{ i }}\n{% endblock %}\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"item #1\n\nitem #2\n\nitem #3\n")),(0,i.kt)("p",null,"Variables defined in an overridden block will go out of scope after that block has been rendered."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="base"',title:'"base"'},'{% assign greeting = "Hello" %}\n{% block say-hi %}{{ greeting }}, World!{% endblock %}\n{{ greeting }}, World!\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="child"',title:'"child"'},'{% extends "base" %}\n{% block say-hi %}\n  {% assign greeting = "Goodbye" %}\n  {{ greeting }}, World!\n  {{ block.super }}\n{% endblock %}\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"Goodbye, World!\nHello, World!\n\nHello, World!\n")),(0,i.kt)("h3",{id:"required-blocks"},"Required Blocks"),(0,i.kt)("p",null,"Use the ",(0,i.kt)("inlineCode",{parentName:"p"},"{% block %}")," tag's ",(0,i.kt)("inlineCode",{parentName:"p"},"required")," argument to indicate that the block must be overridden by a child template. If a required block does not get implemented by a child template, a ",(0,i.kt)("inlineCode",{parentName:"p"},"RequiredBlockError")," exception is raised at render time."),(0,i.kt)("p",null,"In this example, if the template were to be rendered directly, we would expect a ",(0,i.kt)("inlineCode",{parentName:"p"},"RequiredBlockError")," due to the ",(0,i.kt)("inlineCode",{parentName:"p"},"content")," block being required."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="base"',title:'"base"'},'<head>\n  {% block head %}{% endblock %}\n<head>\n<body>\n  <div id="content">{% block content required %}{% endblock %}</div>\n  <div id="footer">{% block footer %}Default footer{% endblock %}</div>\n</body>\n')),(0,i.kt)("h3",{id:"super-blocks"},"Super Blocks"),(0,i.kt)("p",null,"A ",(0,i.kt)("inlineCode",{parentName:"p"},"block")," object is available inside every ",(0,i.kt)("inlineCode",{parentName:"p"},"{% block %}")," tag. It has just one property, ",(0,i.kt)("inlineCode",{parentName:"p"},"super"),". If a ",(0,i.kt)("inlineCode",{parentName:"p"},"{% block %}")," is overriding a parent block, ",(0,i.kt)("inlineCode",{parentName:"p"},"{{ block.super }}")," will render the parent's implementation of that block."),(0,i.kt)("p",null,"In this example we use ",(0,i.kt)("inlineCode",{parentName:"p"},"{{ block.super }}")," in the ",(0,i.kt)("inlineCode",{parentName:"p"},"footer")," block to output the base template's footer with a year appended to it."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="base"',title:'"base"'},'<head>\n  {% block head %}{% endblock %}\n<head>\n<body>\n  <div id="content">{% block content required %}{% endblock %}</div>\n  <div id="footer">{% block footer %}Default footer{% endblock %}</div>\n</body>\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="child"',title:'"child"'},'{% extends "base" %}\n{% block content %}Hello, World!{% endblock %}\n{% block footer %}{{ block.super }} - 2023{% endblock %}\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-html",metastring:'title="output"',title:'"output"'},'<body>\n  <div id="content">Hello, World!</div>\n  <div id="footer">Default footer - 2023</div>\n</body>\n')),(0,i.kt)("h2",{id:"if-not"},"if (not)"),(0,i.kt)("p",null,(0,i.kt)("strong",{parentName:"p"},(0,i.kt)("em",{parentName:"strong"},"New in version 1.5.0"))),(0,i.kt)("p",null,"A drop-in replacement for the standard ",(0,i.kt)("a",{parentName:"p",href:"/liquid/language/tags#if"},(0,i.kt)("inlineCode",{parentName:"a"},"if"))," tag that supports a logical ",(0,i.kt)("inlineCode",{parentName:"p"},"not")," operator and grouping terms with parentheses. See ",(0,i.kt)("a",{parentName:"p",href:"/liquid/language/tags#expressions"},"the tag reference")," for a description of standard ",(0,i.kt)("inlineCode",{parentName:"p"},"if")," expressions."),(0,i.kt)("p",null,"In this example, ",(0,i.kt)("inlineCode",{parentName:"p"},"{% if not user %}")," is equivalent to ",(0,i.kt)("inlineCode",{parentName:"p"},"{% unless user %}"),", however, ",(0,i.kt)("inlineCode",{parentName:"p"},"not")," can also be used after ",(0,i.kt)("inlineCode",{parentName:"p"},"and")," and ",(0,i.kt)("inlineCode",{parentName:"p"},"or"),", like ",(0,i.kt)("inlineCode",{parentName:"p"},"{% if user.active and not user.title %}"),", potentially saving nested ",(0,i.kt)("inlineCode",{parentName:"p"},"if")," and ",(0,i.kt)("inlineCode",{parentName:"p"},"unless")," tags."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\nfrom liquid.extra.tags import IfNotTag\n\nenv = Environment()\nenv.add_tag(IfNotTag)\n\ntemplate = env.from_string("""\\\n{% if not user %}\n  please log in\n{% else %}\n  hello user\n{% endif %}\n""")\n\ndata = {\n  "user": {\n    "eligible": False,\n    "score": 5\n  }\n}\n\nprint(template.render(**data))\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"hello user\n")),(0,i.kt)("p",null,"The ",(0,i.kt)("inlineCode",{parentName:"p"},"not")," prefix operator uses Liquid truthiness. Only ",(0,i.kt)("inlineCode",{parentName:"p"},"false")," and ",(0,i.kt)("inlineCode",{parentName:"p"},"nil")," are not truthy. Empty strings, arrays and objects all evaluate to ",(0,i.kt)("inlineCode",{parentName:"p"},"true"),"."),(0,i.kt)("h3",{id:"parentheses"},"Parentheses"),(0,i.kt)("p",null,(0,i.kt)("inlineCode",{parentName:"p"},"and")," and ",(0,i.kt)("inlineCode",{parentName:"p"},"or")," operators in Liquid are right associative. Where ",(0,i.kt)("inlineCode",{parentName:"p"},"true and false and false or true")," is equivalent to ",(0,i.kt)("inlineCode",{parentName:"p"},"(true and (false and (false or true)))"),", evaluating to ",(0,i.kt)("inlineCode",{parentName:"p"},"false"),". Python, on the other hand, would parse the same expression as ",(0,i.kt)("inlineCode",{parentName:"p"},"(((true and false) and false) or true)"),", evaluating to ",(0,i.kt)("inlineCode",{parentName:"p"},"true"),"."),(0,i.kt)("p",null,"This implementation of ",(0,i.kt)("inlineCode",{parentName:"p"},"if")," maintains that right associativity so that any standard ",(0,i.kt)("inlineCode",{parentName:"p"},"if")," expression will behave the same, with or without non-standard ",(0,i.kt)("inlineCode",{parentName:"p"},"if"),". Only when ",(0,i.kt)("inlineCode",{parentName:"p"},"not")," or parentheses are used will behavior deviate from the standard."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-json",metastring:'title="data"',title:'"data"'},'{\n  "user": {\n    "eligible": false,\n    "score": 5\n  },\n  "exempt": true\n}\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template with parentheses"',title:'"template',with:!0,'parentheses"':!0},"{% if (user != empty and user.eligible and user.score > 100) or exempt %}\n    user is special\n{% else %}\n    denied\n{% endif %}\n")),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"user is special\n")),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template without parentheses"',title:'"template',without:!0,'parentheses"':!0},"{% if user != empty and user.eligible and user.score > 100 or exempt %}\n    user is special\n{% else %}\n    denied\n{% endif %}\n")),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"denied\n")),(0,i.kt)("h2",{id:"inline-if--else"},"inline if / else"),(0,i.kt)("p",null,(0,i.kt)("strong",{parentName:"p"},(0,i.kt)("em",{parentName:"strong"},"New in version 1.5.0"))),(0,i.kt)("p",null,"Drop-in replacements for the standard output statement, ",(0,i.kt)("a",{parentName:"p",href:"/liquid/language/tags#assign"},(0,i.kt)("inlineCode",{parentName:"a"},"assign"))," tag, and ",(0,i.kt)("a",{parentName:"p",href:"/liquid/language/tags#echo"},(0,i.kt)("inlineCode",{parentName:"a"},"echo"))," tag that support inline ",(0,i.kt)("inlineCode",{parentName:"p"},"if"),"/",(0,i.kt)("inlineCode",{parentName:"p"},"else")," expressions. You can find a BNF-like description of the inline conditional expression in ",(0,i.kt)("a",{parentName:"p",href:"https://gist.github.com/jg-rp/e2dc4da9e5033e087e46016008a9d91c#file-inline_if_expression-bnf"},"this gist"),"."),(0,i.kt)("p",null,"Inline ",(0,i.kt)("inlineCode",{parentName:"p"},"if"),"/",(0,i.kt)("inlineCode",{parentName:"p"},"else")," expressions are designed to be backwards compatible with standard filtered expressions. As long as there are no template variables called ",(0,i.kt)("inlineCode",{parentName:"p"},"if")," or ",(0,i.kt)("inlineCode",{parentName:"p"},"else")," within a filtered expression, standard output statements, ",(0,i.kt)("inlineCode",{parentName:"p"},"assign")," tags and ",(0,i.kt)("inlineCode",{parentName:"p"},"echo")," tags will behave the same."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\nfrom liquid.extra import add_inline_expression_tags\n\nenv = Environment()\nadd_inline_expression_tags(env)\n\ntemplate = env.from_string("{{ \'hello user\' if user.logged_in else \'please log in\' }}")\n\ndata = {\n  "user": {\n    "logged_in": False\n  }\n}\n\nprint(template.render(**data))\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"please log in\n")),(0,i.kt)("p",null,"The ",(0,i.kt)("inlineCode",{parentName:"p"},"else")," part of an inline expression is optional, defaulting to ",(0,i.kt)("a",{parentName:"p",href:"/liquid/introduction/strictness#undefined-variables"},"undefined"),"."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template"',title:'"template"'},"{{ 'hello user' if user.logged_in }}!\n")),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"!\n")),(0,i.kt)("p",null,"Inline conditional expressions are evaluated lazily. If the condition is falsy, the leading object is not evaluated. Equally, if the condition is truthy, any expression following ",(0,i.kt)("inlineCode",{parentName:"p"},"else")," will not be evaluated."),(0,i.kt)("h3",{id:"with-filters"},"With Filters"),(0,i.kt)("admonition",{type:"caution"},(0,i.kt)("p",{parentName:"admonition"},'The inline conditional expressions added to Python Liquid 1.5.0 differs slightly from those found in Python Liquid Extra. Previously, trailing filters would be applied regardless of which branch of the condition was taken. Now, "tail filters" are distinguished from alternative branch filters with a double pipe token (',(0,i.kt)("inlineCode",{parentName:"p"},"||"),"). See examples below.")),(0,i.kt)("p",null,"Filters can appear before an inline ",(0,i.kt)("inlineCode",{parentName:"p"},"if")," expression."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template"',title:'"template"'},"{{ 'hello user' | capitalize if user.logged_in else 'please log in' }}\n")),(0,i.kt)("p",null,"Or after an inline ",(0,i.kt)("inlineCode",{parentName:"p"},"if")," expression. In which case filters will only be applied to the ",(0,i.kt)("inlineCode",{parentName:"p"},"else")," clause."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template"',title:'"template"'},"{% assign param = 'hello user' if user.logged_in else 'please log in' | url_encode %}\n")),(0,i.kt)("p",null,"Or both."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template"',title:'"template"'},"{{% assign param = 'hello user' | capitalize if user.logged_in else 'please log in' | url_encode %}\n")),(0,i.kt)("p",null,"Use a double pipe (",(0,i.kt)("inlineCode",{parentName:"p"},"||"),') to start any filters you want to apply regardless of which branch is taken. Subsequent "tail filters" should be separated by a single pipe (',(0,i.kt)("inlineCode",{parentName:"p"},"|"),")."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template"',title:'"template"'},"{{% assign name =\n  user.nickname | downcase\n  if user.has_nickname\n  else user.last_name | capitalize\n  || prepend: user.title | strip\n%}\n")),(0,i.kt)("h2",{id:"macro--call"},"macro / call"),(0,i.kt)("p",null,(0,i.kt)("strong",{parentName:"p"},(0,i.kt)("em",{parentName:"strong"},"New in version 1.5.0"))),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain"},"{% macro <string> [[,] [ <object>, ... ] [ <identifier>: <object>, ... ]] %}\n")),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain"},"{% call <string> [[,] [ <object>, ... ] [ <identifier>: <object>, ... ]] %}\n")),(0,i.kt)("p",null,"Define parameterized Liquid snippets using the ",(0,i.kt)("inlineCode",{parentName:"p"},"macro")," tag, and call them using the ",(0,i.kt)("inlineCode",{parentName:"p"},"call")," tag."),(0,i.kt)("p",null,"Using the ",(0,i.kt)("inlineCode",{parentName:"p"},"macro")," tag is like defining a function. Its parameter list defines arguments, possibly with default values. A ",(0,i.kt)("inlineCode",{parentName:"p"},"macro")," tag's block has its own scope including its arguments and template global variables, just like the ",(0,i.kt)("inlineCode",{parentName:"p"},"render")," tag."),(0,i.kt)("p",null,"Note that argument defaults are bound late. They are evaluated when a ",(0,i.kt)("inlineCode",{parentName:"p"},"call")," expression is evaluated, not when the macro is defined."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\nfrom liquid import StrictUndefined\nfrom liquid.extra import add_macro_tags\n\nenv = Environment(undefined=StrictUndefined)\nadd_macro_tags(env)\n\ntemplate = env.from_string("""\\\n{% macro \'price\' product, on_sale: false %}\n  <div class="price-wrapper">\n  {% if on_sale %}\n    <p>Was {{ product.regular_price | prepend: \'$\' }}</p>\n    <p>Now {{ product.price | prepend: \'$\' }}</p>\n  {% else %}\n    <p>{{ product.price | prepend: \'$\' }}</p>\n  {% endif %}\n  </div>\n{% endmacro %}\n\n{% call \'price\' products[0], on_sale: true %}\n{% call \'price\' products[1] %}\n""")\n\ndata = {\n  "products": [\n    {\n      "title": "Some Shoes",\n      "regular_price": "5.99",\n      "price": "4.99"\n    },\n    {\n      "title": "A Hat",\n      "regular_price": "16.00",\n      "price": "12.00"\n    }\n  ]\n}\n\nprint(template.render(**data))\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-html",metastring:'title="output"',title:'"output"'},'<div class="price-wrapper">\n  <p>Was $5.99</p>\n  <p>Now $4.99</p>\n</div>\n\n<div class="price-wrapper">\n  <p>$12.00</p>\n</div>\n')),(0,i.kt)("h3",{id:"excess-arguments"},"Excess Arguments"),(0,i.kt)("p",null,"Excess arguments passed to ",(0,i.kt)("inlineCode",{parentName:"p"},"call")," are collected into ",(0,i.kt)("inlineCode",{parentName:"p"},"args")," and ",(0,i.kt)("inlineCode",{parentName:"p"},"kwargs"),"."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template"',title:'"template"'},"{% macro 'foo' %}\n  {% for arg in args %}\n    - {{ arg }}\n  {% endfor %}\n\n  {% for arg in kwargs %}\n    - {{ arg.0 }} => {{ arg.1 }}\n  {% endfor %}\n{% endmacro %}\n\n{% call 'foo' 42, 43, 99, a: 3.14, b: 2.71828 %}\n")),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"- 42\n- 43\n- 99\n\n- a => 3.14\n- b => 2.71828\n")),(0,i.kt)("h2",{id:"with"},"with"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain"},"{% with <identifier>: <object> [, <identifier>: object ... ] %}\n  <literal,statement,tag> ...\n{% endwith %}\n")),(0,i.kt)("p",null,"Extend the local namespace with block scoped variables."),(0,i.kt)("p",null,"Register ",(0,i.kt)("inlineCode",{parentName:"p"},"WithTag")," with a ",(0,i.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,i.kt)("inlineCode",{parentName:"a"},"liquid.Environment"))," to make ",(0,i.kt)("inlineCode",{parentName:"p"},"with")," available to templates rendered from that environment."),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},"from liquid import Environment\nfrom liquid.extra.tags import WithTag\n\nenv = Environment()\nenv.add_tag(WithTag)\n")),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-json",metastring:'title="data"',title:'"data"'},'{ "collection": { "products": [{ "title": "A Shoe" }] } }\n')),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template"',title:'"template"'},"{% with p: collection.products.first %}\n  {{ p.title }}\n{% endwith %}\n{{ p.title }}\n\n{% with a: 1, b: 3.4 %}\n  {{ a }} + {{ b }} = {{ a | plus: b }}\n{% endwith %}\n")),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"A Shoe\n\n1 + 3.4 = 4.4\n")))}m.isMDXComponent=!0}}]);