"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[8870],{3905:(e,n,t)=>{t.r(n),t.d(n,{MDXContext:()=>m,MDXProvider:()=>u,mdx:()=>x,useMDXComponents:()=>p,withMDXComponents:()=>s});var i=t(7294);function a(e,n,t){return n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}function r(){return r=Object.assign||function(e){for(var n=1;n<arguments.length;n++){var t=arguments[n];for(var i in t)Object.prototype.hasOwnProperty.call(t,i)&&(e[i]=t[i])}return e},r.apply(this,arguments)}function l(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);n&&(i=i.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,i)}return t}function o(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?l(Object(t),!0).forEach((function(n){a(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):l(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function d(e,n){if(null==e)return{};var t,i,a=function(e,n){if(null==e)return{};var t,i,a={},r=Object.keys(e);for(i=0;i<r.length;i++)t=r[i],n.indexOf(t)>=0||(a[t]=e[t]);return a}(e,n);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);for(i=0;i<r.length;i++)t=r[i],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(a[t]=e[t])}return a}var m=i.createContext({}),s=function(e){return function(n){var t=p(n.components);return i.createElement(e,r({},n,{components:t}))}},p=function(e){var n=i.useContext(m),t=n;return e&&(t="function"==typeof e?e(n):o(o({},n),e)),t},u=function(e){var n=p(e.components);return i.createElement(m.Provider,{value:n},e.children)},c="mdxType",h={inlineCode:"code",wrapper:function(e){var n=e.children;return i.createElement(i.Fragment,{},n)}},g=i.forwardRef((function(e,n){var t=e.components,a=e.mdxType,r=e.originalType,l=e.parentName,m=d(e,["components","mdxType","originalType","parentName"]),s=p(t),u=a,c=s["".concat(l,".").concat(u)]||s[u]||h[u]||r;return t?i.createElement(c,o(o({ref:n},m),{},{components:t})):i.createElement(c,o({ref:n},m))}));function x(e,n){var t=arguments,a=n&&n.mdxType;if("string"==typeof e||a){var r=t.length,l=new Array(r);l[0]=g;var o={};for(var d in n)hasOwnProperty.call(n,d)&&(o[d]=n[d]);o.originalType=e,o[c]="string"==typeof e?e:a,l[1]=o;for(var m=2;m<r;m++)l[m]=t[m];return i.createElement.apply(null,l)}return i.createElement.apply(null,t)}g.displayName="MDXCreateElement"},7988:(e,n,t)=>{t.r(n),t.d(n,{contentTitle:()=>l,default:()=>p,frontMatter:()=>r,metadata:()=>o,toc:()=>d});var i=t(7462),a=(t(7294),t(3905));const r={title:"Compatibility",description:"Known incompatibilities between Python Liquid and Ruby Liquid",hide_table_of_contents:!1},l="Known Issues",o={type:"mdx",permalink:"/liquid/known_issues",source:"@site/src/pages/known_issues.md",title:"Compatibility",description:"Known incompatibilities between Python Liquid and Ruby Liquid",frontMatter:{title:"Compatibility",description:"Known incompatibilities between Python Liquid and Ruby Liquid",hide_table_of_contents:!1}},d=[{value:"Coercing Strings to Integers Inside Filters",id:"coercing-strings-to-integers-inside-filters",level:2},{value:"Comment Parsing",id:"comment-parsing",level:2},{value:"Counters",id:"counters",level:2},{value:"Cycle Arguments",id:"cycle-arguments",level:2},{value:"Cycle Groups",id:"cycle-groups",level:2},{value:"The Date Filter",id:"the-date-filter",level:2},{value:"Error Handling",id:"error-handling",level:2},{value:"Floats in Ranges",id:"floats-in-ranges",level:2},{value:"The Split Filter",id:"the-split-filter",level:2},{value:"Indexable Strings",id:"indexable-strings",level:2},{value:"Iterating Strings",id:"iterating-strings",level:2},{value:"Summing Floats",id:"summing-floats",level:2}],m={toc:d},s="wrapper";function p(e){let{components:n,...t}=e;return(0,a.mdx)(s,(0,i.default)({},m,t,{components:n,mdxType:"MDXLayout"}),(0,a.mdx)("h1",{id:"known-issues"},"Known Issues"),(0,a.mdx)("p",null,"This page documents known compatibility issues between Python Liquid's default ",(0,a.mdx)("a",{parentName:"p",href:"/api/Environment"},(0,a.mdx)("inlineCode",{parentName:"a"},"Environment"))," and the ",(0,a.mdx)("a",{parentName:"p",href:"https://shopify.github.io/liquid/"},"reference implementation")," of Liquid, written in Ruby. We strive to be 100% compatible with the reference implementation. That is, given an equivalent render context, a template rendered with Python Liquid should produce the same output as when rendered with Ruby Liquid."),(0,a.mdx)("admonition",{type:"info"},(0,a.mdx)("p",{parentName:"admonition"},"Python Liquid version 1.7.0 introduced ",(0,a.mdx)("a",{parentName:"p",href:"/api/future-environment"},(0,a.mdx)("inlineCode",{parentName:"a"},"liquid.future.Environment"))," as an alternative to the default ",(0,a.mdx)("a",{parentName:"p",href:"/api/Environment"},(0,a.mdx)("inlineCode",{parentName:"a"},"Environment")),". This alternative environment is intended to transition Python Liquid towards greater compatibility with Ruby Liquid, without changing template rendering behavior for existing Python Liquid users."),(0,a.mdx)("p",{parentName:"admonition"},"Some of the issues described below have been resolved with ",(0,a.mdx)("inlineCode",{parentName:"p"},"liquid.future.Environment"),". To use it, simply import ",(0,a.mdx)("inlineCode",{parentName:"p"},"Environment")," from ",(0,a.mdx)("inlineCode",{parentName:"p"},"liquid.future")," instead of ",(0,a.mdx)("inlineCode",{parentName:"p"},"liquid"),".")),(0,a.mdx)("h2",{id:"coercing-strings-to-integers-inside-filters"},"Coercing Strings to Integers Inside Filters"),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},(0,a.mdx)("em",{parentName:"strong"},"See issue ",(0,a.mdx)("a",{parentName:"em",href:"https://github.com/jg-rp/liquid/issues/49"},"#49")))),(0,a.mdx)("p",null,"Many filters built in to Liquid will automatically convert a string representation of a number to an integer or float as needed. When converting integers, Ruby Liquid uses ",(0,a.mdx)("a",{parentName:"p",href:"https://ruby-doc.org/core-3.1.1/String.html#method-i-to_i"},"Ruby's String.to_i method"),", which will disregard trailing non-digit characters. In the following example, ",(0,a.mdx)("inlineCode",{parentName:"p"},"'7,42'")," is converted to ",(0,a.mdx)("inlineCode",{parentName:"p"},"7")),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"template:")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-liquid"},"{{ 3.14 | plus: '7,42' }}\n{{ '123abcdef45' | plus: '1,,,,..!@qwerty' }}\n")),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"output")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-plain"},"10.14\n124\n")),(0,a.mdx)("p",null,"Python Liquid currently falls back to ",(0,a.mdx)("inlineCode",{parentName:"p"},"0")," for any string that can't be converted to an integer in its entirety. As is the case in Ruby Liquid for strings without leading digits."),(0,a.mdx)("p",null,"This does not apply to parsing of integer literals, only converting strings to integers (not floats) inside filters."),(0,a.mdx)("h2",{id:"comment-parsing"},"Comment Parsing"),(0,a.mdx)("p",null,"Python Liquid will raise a ",(0,a.mdx)("inlineCode",{parentName:"p"},"LiquidSyntaxError")," if it finds the string ",(0,a.mdx)("inlineCode",{parentName:"p"},"{% endcomment %}")," inside a comment block. Ruby Liquid, on the other hand, will successfully parse fully-formed nested comment blocks, but will fail to parse a comment block containing either a ",(0,a.mdx)("inlineCode",{parentName:"p"},"{% comment %}")," or ",(0,a.mdx)("inlineCode",{parentName:"p"},"{% endcomment %}")," on its own."),(0,a.mdx)("h2",{id:"counters"},"Counters"),(0,a.mdx)("p",null,"In Ruby Liquid, the built-in ",(0,a.mdx)("a",{parentName:"p",href:"/language/tags#increment"},(0,a.mdx)("inlineCode",{parentName:"a"},"increment"))," and ",(0,a.mdx)("a",{parentName:"p",href:"/language/tags#decrement"},(0,a.mdx)("inlineCode",{parentName:"a"},"decrement")),' tags can, in some cases, mutate "global" context and keep named counters alive between renders. Although not difficult to implement, I can\'t quite bring myself to do it.'),(0,a.mdx)("h2",{id:"cycle-arguments"},"Cycle Arguments"),(0,a.mdx)("p",null,"Python Liquid will accept ",(0,a.mdx)("a",{parentName:"p",href:"/language/tags#cycle"},(0,a.mdx)("inlineCode",{parentName:"a"},"cycle")),' arguments of any type, including identifiers to be resolved, this behavior is considered "unintended" or "undefined" in Ruby Liquid (see ',(0,a.mdx)("a",{parentName:"p",href:"https://github.com/Shopify/liquid/issues/1519"},"issue #1519"),"). If you need interoperability between Python Liquid and Ruby Liquid, only use strings or numbers as arguments to ",(0,a.mdx)("inlineCode",{parentName:"p"},"cycle"),"."),(0,a.mdx)("h2",{id:"cycle-groups"},"Cycle Groups"),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},(0,a.mdx)("em",{parentName:"strong"},"See issue ",(0,a.mdx)("a",{parentName:"em",href:"https://github.com/jg-rp/liquid/issues/43"},"#43")))),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},(0,a.mdx)("em",{parentName:"strong"},"Fixed in version 1.7.0"))," with ",(0,a.mdx)("a",{parentName:"p",href:"/api/future-environment"},(0,a.mdx)("inlineCode",{parentName:"a"},"liquid.future.Environment")),"."),(0,a.mdx)("p",null,"When the ",(0,a.mdx)("a",{parentName:"p",href:"/language/tags#cycle"},(0,a.mdx)("inlineCode",{parentName:"a"},"cycle"))," tag is given a name, Python Liquid will use that name and all other arguments to distinguish one cycle from another. Ruby Liquid will disregard all other arguments when given a name. For example."),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-liquid"},'{% cycle a: 1, 2, 3 %}\n{% cycle a: "x", "y", "z" %}\n{% cycle a: 1, 2, 3 %}\n')),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"Ruby Liquid Output:")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-plain"},"1\ny\n3\n")),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"Python Liquid Output:")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-plain"},"1\nx\n2\n")),(0,a.mdx)("h2",{id:"the-date-filter"},"The Date Filter"),(0,a.mdx)("p",null,"The built-in ",(0,a.mdx)("a",{parentName:"p",href:"/language/filters#date"},(0,a.mdx)("inlineCode",{parentName:"a"},"date"))," filter uses ",(0,a.mdx)("a",{parentName:"p",href:"https://dateutil.readthedocs.io/en/stable/"},"dateutil")," for parsing strings to ",(0,a.mdx)("inlineCode",{parentName:"p"},"datetime"),"s, and ",(0,a.mdx)("inlineCode",{parentName:"p"},"strftime")," for formatting. There are likely to be some inconsistencies between this and the reference implementation's equivalent parsing and formatting of dates and times."),(0,a.mdx)("h2",{id:"error-handling"},"Error Handling"),(0,a.mdx)("p",null,"Python Liquid might not handle syntax or type errors in the same way as the reference implementation. We might fail earlier or later, and will almost certainly produce a different error message."),(0,a.mdx)("p",null,'Python Liquid does not have a "lax" parser, like Ruby Liquid. Upon finding an error, Python Liquid\'s ',(0,a.mdx)("a",{parentName:"p",href:"/introduction/strictness"},"lax mode")," simply discards the current block and continues to parse/render the next block, if one is available. Also, Python Liquid will never inject error messages into an output document. Although this can be achieved by extending ",(0,a.mdx)("a",{parentName:"p",href:"/api/BoundTemplate"},(0,a.mdx)("inlineCode",{parentName:"a"},"BoundTemplate"))," and overriding ",(0,a.mdx)("a",{parentName:"p",href:"/api/BoundTemplate#render_with_context"},(0,a.mdx)("inlineCode",{parentName:"a"},"render_with_context()")),"."),(0,a.mdx)("h2",{id:"floats-in-ranges"},"Floats in Ranges"),(0,a.mdx)("p",null,"If a range literal uses a float literal as its start or stop value, the float literal must have something after the decimal point. This is OK ",(0,a.mdx)("inlineCode",{parentName:"p"},"(1.0..3)"),". This is not ",(0,a.mdx)("inlineCode",{parentName:"p"},"(1...3)"),". Ruby Liquid will accept either, resulting in a sequence of ",(0,a.mdx)("inlineCode",{parentName:"p"},"[1,2,3]"),"."),(0,a.mdx)("h2",{id:"the-split-filter"},"The Split Filter"),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},(0,a.mdx)("em",{parentName:"strong"},"See issue ",(0,a.mdx)("a",{parentName:"em",href:"https://github.com/jg-rp/liquid/issues/134"},"#134")))),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},(0,a.mdx)("em",{parentName:"strong"},"Fixed in version 1.10.2"))," with ",(0,a.mdx)("a",{parentName:"p",href:"/api/future-environment"},(0,a.mdx)("inlineCode",{parentName:"a"},"liquid.future.Environment")),"."),(0,a.mdx)("p",null,"When given an empty string to split or when the string and the delimiter are equal, we used Python's ",(0,a.mdx)("inlineCode",{parentName:"p"},"str.split()")," behavior of producing one or two element lists containing empty strings. Shopify/Liquid returns an empty list/array in such cases."),(0,a.mdx)("h2",{id:"indexable-strings"},"Indexable Strings"),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},(0,a.mdx)("em",{parentName:"strong"},"See issue ",(0,a.mdx)("a",{parentName:"em",href:"https://github.com/jg-rp/liquid/issues/90"},"#90")))),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},(0,a.mdx)("em",{parentName:"strong"},"Fixed in version 1.7.0"))," with ",(0,a.mdx)("a",{parentName:"p",href:"/api/future-environment"},(0,a.mdx)("inlineCode",{parentName:"a"},"liquid.future.Environment")),"."),(0,a.mdx)("p",null,"The reference implementation does not allow us to access characters in a string by their index. Python Liquid does."),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"Template")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-liquid"},"{% assign x = 'foobar' -%}\n{{ x[0] }}\n{{ x[1] }}\n{{ x[-1] }}\n")),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"Python Liquid output")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-plain"},"f\no\nr\n")),(0,a.mdx)("p",null,"Shopify/liquid will throw an error (in strict mode) for each attempt at accessing a character by its index."),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-plain"},"<Liquid::UndefinedVariable: Liquid error: undefined variable 0>\n<Liquid::UndefinedVariable: Liquid error: undefined variable 1>\n<Liquid::UndefinedVariable: Liquid error: undefined variable -1>\n")),(0,a.mdx)("h2",{id:"iterating-strings"},"Iterating Strings"),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},(0,a.mdx)("em",{parentName:"strong"},"See issue ",(0,a.mdx)("a",{parentName:"em",href:"https://github.com/jg-rp/liquid/issues/102"},"#102")))),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},(0,a.mdx)("em",{parentName:"strong"},"Fixed in version 1.8.0"))," with ",(0,a.mdx)("a",{parentName:"p",href:"/api/future-environment"},(0,a.mdx)("inlineCode",{parentName:"a"},"liquid.future.Environment")),"."),(0,a.mdx)("p",null,"When looping over strings with the ",(0,a.mdx)("inlineCode",{parentName:"p"},"{% for %}")," tag, the reference implementation of Liquid will iterate over a one element array, where the first and only element is the string. Python Liquid will iterate through characters in the string."),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"Template:")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-liquid"},"{% assign foo = 'hello world' %}\n{% for x in foo %}{{ x }} / {% endfor %}\n")),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"Ruby Liquid Output:")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-plain"},"hello world /\n")),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"Python Liquid Output:")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-plain"},"h / e / l / l / o /   / w / o / r / l / d /\n")),(0,a.mdx)("p",null,"It appears that this is unintended behavior for Ruby Liquid. Previously, Ruby Liquid would iterate over lines in a string, also not intended behavior. See ",(0,a.mdx)("a",{parentName:"p",href:"https://github.com/Shopify/liquid/pull/1667"},"https://github.com/Shopify/liquid/pull/1667"),"."),(0,a.mdx)("h2",{id:"summing-floats"},"Summing Floats"),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},(0,a.mdx)("em",{parentName:"strong"},"See ",(0,a.mdx)("a",{parentName:"em",href:"https://github.com/Shopify/liquid/issues/1725"},"Shopify/Liquid#1725")))),(0,a.mdx)("p",null,"When given one or more floats as input, the reference implementation's standard ",(0,a.mdx)("inlineCode",{parentName:"p"},"sum")," filter will return a ",(0,a.mdx)("inlineCode",{parentName:"p"},"BigDecimal"),", which is rendered in scientific notation (or similar). Python Liquid will coerce the result to a float, and render that, without an exponent."),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"Template:")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-liquid"},'{% assign a = "0.1,0.2,0.3" | split: "," %}\n{{ a | sum }}\n')),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"Ruby Liquid Output:")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-plain"},"0.6e0\n")),(0,a.mdx)("p",null,(0,a.mdx)("strong",{parentName:"p"},"Python Liquid Output:")),(0,a.mdx)("pre",null,(0,a.mdx)("code",{parentName:"pre",className:"language-plain"},"0.6\n")))}p.isMDXComponent=!0}}]);